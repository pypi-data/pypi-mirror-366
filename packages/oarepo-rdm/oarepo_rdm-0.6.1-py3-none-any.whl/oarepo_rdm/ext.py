#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo-Requests extension."""
from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.resources.config import record_serializers
from oarepo_runtime.datastreams.utils import get_record_service_for_record_class
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_records_resources.proxies import current_service_registry
from werkzeug.local import LocalProxy

from oarepo_rdm.resources.records.config import global_search_response_handlers

if TYPE_CHECKING:
    from flask import Flask

from invenio_rdm_records.services import RDMRecordService, RDMRecordServiceConfig
from invenio_rdm_records.resources import RDMRecordResource, RDMRecordResourceConfig
from invenio_rdm_records.records.api import RDMRecord, RDMDraft

@dataclass
class RDMModel:
    service_id: str
    api_service: RDMRecordService
    api_service_config: RDMRecordServiceConfig
    api_resource: RDMRecordResource
    api_resource_config: RDMRecordResourceConfig
    record_cls: type[RDMRecord]
    draft_cls: type[RDMDraft]
    pid_type: str
    ui_resource_config: Any

class OARepoRDM(object):
    """OARepo extension of Invenio-Vocabularies."""

    def __init__(self, app: Flask = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)
            self.init_config(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        app.extensions["oarepo-rdm"] = self

    def init_config(self, app: Flask) -> None:
        app.config.setdefault(
            "APP_RDM_ROUTES",
            {
                "record_detail": "/records/<pid_value>",
                "record_file_download": "/records/<pid_value>/files/<path:filename>",
            },
        )
        proxy = LocalProxy(global_search_response_handlers)
        app.config.setdefault("RDM_RECORDS_SERIALIZERS", record_serializers | {"application/vnd.inveniordm.v1+json": proxy})

    def record_cls_from_pid_type(self, pid_type, is_draft: bool):
        for model in self.app.config["GLOBAL_SEARCH_MODELS"]:
            service_cfg = obj_or_import_string(model["service_config"])
            if is_draft:
                draft_cls = getattr(service_cfg, "draft_cls", None)
                if draft_cls:
                    provider = draft_cls.pid.field._provider
                    if provider.pid_type == pid_type:
                        return draft_cls
            else:
                record_cls = getattr(service_cfg, "record_cls", None)
                if record_cls:
                    provider = record_cls.pid.field._provider
                    if provider.pid_type == pid_type:
                        return record_cls

    def pick_record_pid(self, pids, id):
        if not pids:
            raise PIDDoesNotExistError(None, None)
        pids_without_skipped = [pid for pid in pids if pid.pid_type in self.primary_model_pids]
        if not pids_without_skipped:
            raise PIDDoesNotExistError(None, None)
        if len(pids_without_skipped) > 1:
            raise ValueError("Multiple PIDs found") #use some piderror
        return pids_without_skipped[0]

    def get_pid_type_from_pid(self, pid_value):
        pids = PersistentIdentifier.query.filter_by(pid_value=pid_value).all()
        pid = self.pick_record_pid(pids, pid_value)
        return pid.pid_type

    def pid_from_uuid(self, uuid):
        pids = PersistentIdentifier.query.filter_by(object_uuid=uuid).all()
        return self.pick_record_pid(pids, uuid)

    def record_service_from_pid_type(
        self, pid_type, is_draft: bool = False
    ):  # there isn't specialized draft service for now
        record_cls = self.record_cls_from_pid_type(pid_type, is_draft)
        return get_record_service_for_record_class(record_cls)

    def _instantiate_configurator_cls(self, cls_):
        if issubclass(cls_, ConfiguratorMixin):
            return cls_.build(self.app)
        else:
            return cls_()

    def get_rdm_model(self, service_id: str)->RDMModel:
        for model in self.rdm_models:
            if model.service_id == service_id:
                return model

    def get_api_resource_config(self, service_id: str)->RDMRecordResourceConfig:
        model = self.get_rdm_model(service_id)
        if model:
            return model.api_resource_config

    @cached_property
    def primary_model_pids(self): # as opposed to oai, technical..
        return {model.pid_type for model in self.rdm_models}

    @cached_property
    def rdm_models(self)->list[RDMModel]:
        models = self.app.config["RDM_MODELS"]
        ret = []
        for model_dict in models:
            model_service_id = model_dict["service_id"]
            for service_id, service in current_service_registry._services.items():
                if service_id == model_service_id:
                    break
            else:
                # exception?
                continue
            # todo resource instances from exts
            api_resource_config = self._instantiate_configurator_cls(
                obj_or_import_string(model_dict["api_resource_config"]))
            api_resource = obj_or_import_string(model_dict["api_resource"])(service=service, config=api_resource_config)
            ret.append(RDMModel(model_dict["service_id"],
                                service,
                                service.config,
                                api_resource,
                                api_resource_config,
                                obj_or_import_string(model_dict["record_cls"]),
                                obj_or_import_string(model_dict["draft_cls"]),
                                model_dict["pid_type"],
                                self._instantiate_configurator_cls(
                                    obj_or_import_string(model_dict["ui_resource_config"]))))
        return ret
