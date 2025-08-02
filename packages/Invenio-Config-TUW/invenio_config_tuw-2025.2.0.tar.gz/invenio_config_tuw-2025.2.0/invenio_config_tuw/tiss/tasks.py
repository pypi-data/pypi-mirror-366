# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TISS-related celery tasks running in the background."""

import copy
from collections import defaultdict
from difflib import SequenceMatcher
from typing import List, Optional

import requests
from celery import shared_task
from celery.schedules import crontab
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import RecordIndexOp, UnitOfWork
from invenio_vocabularies.contrib.names.api import Name

from . import Employee, fetch_tiss_data


def get_tuw_ror_aliases() -> List[str]:
    """Fetch the aliases of TU Wien known to ROR."""
    try:
        response = requests.get("https://api.ror.org/organizations/04d836q62")
        if response.ok:
            tuw_ror = response.json()
            tuw_ror_names = [tuw_ror["name"], *tuw_ror["acronyms"], *tuw_ror["aliases"]]
            return tuw_ror_names

    except Exception as e:
        current_app.logger.warn(
            f"Error while fetching TU Wien information from ROR: {e}"
        )

    return [
        "TU Wien",
        "TUW",
        "Technische Universität Wien",
        "Vienna University of Technology",
    ]


def find_orcid_match(orcid: str, names: List[Name]) -> Optional[Name]:
    """Find the name entry with the given ORCID."""
    if not orcid:
        return None

    for name in names:
        if {"scheme": "orcid", "identifier": orcid} in name.get("identifiers", []):
            return name

    return None


def update_name_data(
    name: dict, employee: Employee, tuw_aliases: Optional[List[str]] = None
) -> dict:
    """Update the given name entry data with the information from the employee."""
    tuw_aliases = tuw_aliases or ["TU Wien"]
    name = copy.deepcopy(name)
    name["given_name"] = employee.first_name
    name["family_name"] = employee.last_name
    if "name" in name:
        name["name"] = f"{employee.last_name}, {employee.first_name}"

    # normalize & deduplicate affilations, and make sure that TU Wien is one of them
    # NOTE: sorting is done to remove indeterminism and prevent unnecessary updates
    affiliations = {
        aff["name"] for aff in name["affiliations"] if aff["name"] not in tuw_aliases
    }
    affiliations.add("TU Wien")
    name["affiliations"] = sorted(
        [{"name": aff} for aff in affiliations], key=lambda aff: aff["name"]
    )

    # similar to above, add the ORCID mentioned in TISS and deduplicate
    identifiers = {(id_["scheme"], id_["identifier"]) for id_ in name["identifiers"]}
    if employee.orcid:
        identifiers.add(("orcid", employee.orcid))

    name["identifiers"] = sorted(
        [{"scheme": scheme, "identifier": id_} for scheme, id_ in identifiers],
        key=lambda id_: f'{id_["scheme"]}:{id_["identifier"]}',
    )

    return name


def _calc_name_distance(
    employee: Optional[Employee], name_voc: Optional[Name]
) -> float:
    """Calculate the distance between the employee name and the vocabulary entry."""
    if employee is None or name_voc is None:
        return 0

    fn, ln = name_voc.get("given_name", ""), name_voc.get("family_name", "")
    fn_dist = SequenceMatcher(a=fn, b=employee.first_name).ratio()
    ln_dist = SequenceMatcher(a=ln, b=employee.last_name).ratio()
    return fn_dist + ln_dist


@shared_task(ignore_result=True)
def sync_names_from_tiss() -> dict:
    """Look up TU Wien employees via TISS and update the names vocabulary."""
    results = {"created": 0, "updated": 0, "failed": 0}
    tuw_ror_aliases = get_tuw_ror_aliases()
    svc = current_app.extensions["invenio-vocabularies"].names_service

    all_names = [
        svc.record_cls.get_record(model.id)
        for model in svc.record_cls.model_cls.query.all()
        if not model.is_deleted and model.data
    ]
    _, employees = fetch_tiss_data()

    # it can happen that 2+ TISS profiles have the same ORCID listed
    orcid_employees = defaultdict(list)
    for employee in employees:
        if not employee.pseudoperson and employee.orcid:
            orcid_employees[employee.orcid].append(employee)

    with UnitOfWork(db.session) as uow:
        for orcid, employees in orcid_employees.items():
            matching_name = find_orcid_match(orcid, all_names)
            if len(employees) == 1:
                (employee,) = employees
            elif len(employees) > 1:
                # if we several TISS profiles with the same ORCID, we use the one
                # with the closest match in name in our names vocabulary
                employee = sorted(
                    employees,
                    key=lambda e: _calc_name_distance(employee, matching_name),
                )[-1]
            else:
                continue

            try:
                if matching_name:
                    name_voc_id = matching_name.pid.pid_value
                    old_name = matching_name.get(
                        "name",
                        f"{matching_name.get('family_name')}, {matching_name.get('given_name')}",
                    )
                    new_name = f"{employee.last_name}, {employee.first_name}"

                    # if we found a match via ORCID, we update it according to the TISS data
                    name = svc.read(identity=system_identity, id_=name_voc_id)

                    # reset created & updated timestamps to their datetime/non-string
                    # form, to avoid breakage in the serialization
                    name._obj["updated"] = name._obj.updated
                    name._obj["created"] = name._obj.created
                    new_name_data = update_name_data(
                        name.data, employee, tuw_ror_aliases
                    )

                    # only update the entry if it actually differs somehow
                    if name.data != new_name_data:
                        # note: it seems like `svc.update()` is currently broken because
                        # some fields that get added to the record (e.g. "pid") isn't
                        # expected in the JSONSchema used for validation
                        # we avoid this by popping "$schema" here
                        # app-rdm v12, vocabularies v3.4.2
                        name_rec = name._record
                        name_rec.update(new_name_data)
                        name_rec.pop("$schema")
                        name_rec.commit()
                        uow.register(RecordIndexOp(name_rec))
                        results["updated"] += 1

                        current_app.logger.info(
                            f"TISS sync: updated name '{name_voc_id}' from "
                            f"'{old_name}' to '{new_name}'"
                        )

                else:
                    # if we couldn't find a match via ORCID, that's a new entry
                    svc.create(
                        identity=system_identity, data=employee.to_name_entry(), uow=uow
                    )
                    results["created"] += 1

            except Exception as e:
                results["failed"] += 1
                current_app.logger.warn(
                    f"TISS sync: failed for '{employee}', with error: {e}"
                )

        uow.commit()

    return results


CELERY_BEAT_SCHEDULE = {
    "tiss-name-sync": {
        "task": "invenio_config_tuw.tiss.tasks.sync_names_from_tiss",
        "schedule": crontab(minute=0, hour=3, day_of_week="sat"),
    },
}
