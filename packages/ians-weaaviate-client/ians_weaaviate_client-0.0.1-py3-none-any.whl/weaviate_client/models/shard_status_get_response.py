from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShardStatusGetResponse")


@_attrs_define
class ShardStatusGetResponse:
    """Response body of shard status get request

    Attributes:
        name (Union[Unset, str]): Name of the shard
        status (Union[Unset, str]): Status of the shard
        vector_queue_size (Union[Unset, int]): Size of the vector queue of the shard
    """

    name: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    vector_queue_size: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status = self.status

        vector_queue_size = self.vector_queue_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if vector_queue_size is not UNSET:
            field_dict["vectorQueueSize"] = vector_queue_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        status = d.pop("status", UNSET)

        vector_queue_size = d.pop("vectorQueueSize", UNSET)

        shard_status_get_response = cls(
            name=name,
            status=status,
            vector_queue_size=vector_queue_size,
        )

        shard_status_get_response.additional_properties = d
        return shard_status_get_response

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
