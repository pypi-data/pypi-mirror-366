#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""invenio-oaiserver percolator extensions."""
from flask import current_app
from invenio_oaiserver import current_oaiserver
from invenio_search import current_search, current_search_client
from invenio_oaiserver.query import query_string_parser
from collections import defaultdict
from invenio_access.permissions import system_identity
from oarepo_global_search.proxies import current_global_search
from invenio_oaiserver.percolator import percolate_query, _create_percolator_mapping, _build_percolator_index_name
from invenio_records_resources.services.records.results import RecordItem
from oarepo_rdm.proxies import current_oarepo_rdm
from invenio_search.utils import prefix_index, build_alias_name
from oarepo_runtime.utils.index import prefixed_index
from invenio_search.proxies import current_search


def _get_rdm_model_record_class_index_aliases(rdm_model):

    index = prefixed_index(rdm_model.api_service_config.record_cls.index)
    rdm_model_alias_dict = index.get_alias() # we expect get_alias returns values with prefix

    return list(rdm_model_alias_dict.values())[0]["aliases"].keys()


def _get_current_search_mapping_name(oai_index_alias):
    prefixed_oai_index_alias = build_alias_name(oai_index_alias)
    prefixed_mapping_names_map = {build_alias_name(k): k for k in current_search.mappings.keys()}
    for rdm_model in current_oarepo_rdm.rdm_models:
        aliases = _get_rdm_model_record_class_index_aliases(rdm_model)
        if prefixed_oai_index_alias not in aliases:
            continue
        intersection = aliases & prefixed_mapping_names_map.keys()
        if len(intersection) != 1:
            raise ValueError(f"OAI index alias {oai_index_alias} does not have a resolvable mapping.")
        return prefixed_mapping_names_map[intersection.pop()]

    if current_oarepo_rdm.rdm_models:
        raise ValueError(f"OAI index alias {oai_index_alias} is not a valid index alias.")


def _new_percolator(spec, search_pattern):
    """Create new percolator associated with the new set."""
    if spec and search_pattern:
        query = query_string_parser(search_pattern=search_pattern).to_dict()
        oai_records_index = current_app.config["OAISERVER_RECORD_INDEX"]
        for oai_index_alias in oai_records_index.split(','): #todo discussion now percolator is created for each oai index even when it doesn't have the mapping
            current_search_mapping_name = _get_current_search_mapping_name(oai_index_alias)
            if current_search_mapping_name:
                try:
                    _create_percolator_mapping(current_search_mapping_name,
                                               current_search.mappings[current_search_mapping_name])
                    current_search_client.index(
                        index=_build_percolator_index_name(current_search_mapping_name),
                        id="oaiset-{}".format(spec),
                        body={"query": query},
                    )
                except Exception as e:
                    current_app.logger.warning(e)


def _delete_percolator(spec, search_pattern):
    oai_records_index = current_app.config["OAISERVER_RECORD_INDEX"]
    for oai_index_alias in oai_records_index.split(','):
        current_search_mapping_name = _get_current_search_mapping_name(oai_index_alias)
        if current_search_mapping_name:
            current_search_client.delete(
                index=_build_percolator_index_name(current_search_mapping_name),
                id="oaiset-{}".format(spec),
                ignore=[404],
            )

def get_service_by_record_schema(record_dict):
    for service in current_global_search.global_search_model_services:
        if not hasattr(service, "record_cls") or not hasattr(service.record_cls, "schema"):
            continue
        if service.record_cls.schema.value == record_dict["$schema"]:
            return service
    return None

def sets_search_all(records):
    # in invenio it's used only for find_sets_for_record, which doesn't use more than one record
    if not records:
        return []

    processed_schemas = set()
    indices_mapping = {}
    records_mapping = defaultdict(list)
    results_for_index = {}
    records_sets_mapping = {}

    for record in records:
        if isinstance(record, RecordItem):
            record = record._record.dumps()

        schema = record["$schema"]
        if schema not in processed_schemas:
            service = get_service_by_record_schema(record)
            record_item = service.read(system_identity, record["id"])
            record_index = record_item._record.index._name
            _create_percolator_mapping(record_index)
            percolator_index = _build_percolator_index_name(record_index)
            indices_mapping[schema] = percolator_index
            processed_schemas.add(service)

        records_mapping[schema].append(record)

    for schema, index in indices_mapping.items():
        records = records_mapping[schema]
        record_sets = [[] for _ in range(len(records))]
        result = percolate_query(indices_mapping[schema], documents=records)
        results_for_index[schema] = result
        records_sets_mapping[schema] = record_sets

    prefix = "oaiset-"
    prefix_len = len(prefix)

    for schema, result in results_for_index.items():
        for s in result:
            set_index_id = s["_id"]
            if set_index_id.startswith(prefix):
                set_spec = set_index_id[prefix_len:]
                for record_index in s.get("fields", {}).get(
                    "_percolator_document_slot", []
                ):
                    records_sets_mapping[schema][record_index].append(set_spec)
    return [item for sublist in records_sets_mapping.values() for item in sublist]

def find_sets_for_record(record):
    """Fetch a record's sets."""
    return current_oaiserver.record_list_sets_fetcher([record])[0]