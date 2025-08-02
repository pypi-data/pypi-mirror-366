import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.distributed_task_payload import DistributedTaskPayload


T = TypeVar("T", bound="DistributedTask")


@_attrs_define
class DistributedTask:
    """Distributed task metadata.

    Attributes:
        id (Union[Unset, str]): The ID of the task.
        version (Union[Unset, int]): The version of the task.
        status (Union[Unset, str]): The status of the task.
        started_at (Union[Unset, datetime.datetime]): The time when the task was created.
        finished_at (Union[Unset, datetime.datetime]): The time when the task was finished.
        finished_nodes (Union[Unset, list[str]]): The nodes that finished the task.
        error (Union[Unset, str]): The high level reason why the task failed.
        payload (Union[Unset, DistributedTaskPayload]): The payload of the task.
    """

    id: Union[Unset, str] = UNSET
    version: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    started_at: Union[Unset, datetime.datetime] = UNSET
    finished_at: Union[Unset, datetime.datetime] = UNSET
    finished_nodes: Union[Unset, list[str]] = UNSET
    error: Union[Unset, str] = UNSET
    payload: Union[Unset, "DistributedTaskPayload"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        version = self.version

        status = self.status

        started_at: Union[Unset, str] = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        finished_at: Union[Unset, str] = UNSET
        if not isinstance(self.finished_at, Unset):
            finished_at = self.finished_at.isoformat()

        finished_nodes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.finished_nodes, Unset):
            finished_nodes = self.finished_nodes

        error = self.error

        payload: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.payload, Unset):
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if version is not UNSET:
            field_dict["version"] = version
        if status is not UNSET:
            field_dict["status"] = status
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at
        if finished_nodes is not UNSET:
            field_dict["finishedNodes"] = finished_nodes
        if error is not UNSET:
            field_dict["error"] = error
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.distributed_task_payload import DistributedTaskPayload

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        version = d.pop("version", UNSET)

        status = d.pop("status", UNSET)

        _started_at = d.pop("startedAt", UNSET)
        started_at: Union[Unset, datetime.datetime]
        if isinstance(_started_at, Unset):
            started_at = UNSET
        else:
            started_at = isoparse(_started_at)

        _finished_at = d.pop("finishedAt", UNSET)
        finished_at: Union[Unset, datetime.datetime]
        if isinstance(_finished_at, Unset):
            finished_at = UNSET
        else:
            finished_at = isoparse(_finished_at)

        finished_nodes = cast(list[str], d.pop("finishedNodes", UNSET))

        error = d.pop("error", UNSET)

        _payload = d.pop("payload", UNSET)
        payload: Union[Unset, DistributedTaskPayload]
        if isinstance(_payload, Unset):
            payload = UNSET
        else:
            payload = DistributedTaskPayload.from_dict(_payload)

        distributed_task = cls(
            id=id,
            version=version,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            finished_nodes=finished_nodes,
            error=error,
            payload=payload,
        )

        distributed_task.additional_properties = d
        return distributed_task

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
