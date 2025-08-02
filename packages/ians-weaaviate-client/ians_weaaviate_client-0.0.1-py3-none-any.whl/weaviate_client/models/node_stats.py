from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeStats")


@_attrs_define
class NodeStats:
    """The summary of Weaviate's statistics.

    Attributes:
        shard_count (Union[Unset, float]): The count of Weaviate's shards. To see this value, set `output` to `verbose`.
        object_count (Union[Unset, float]): The total number of objects in DB.
    """

    shard_count: Union[Unset, float] = UNSET
    object_count: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        shard_count = self.shard_count

        object_count = self.object_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shard_count is not UNSET:
            field_dict["shardCount"] = shard_count
        if object_count is not UNSET:
            field_dict["objectCount"] = object_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        shard_count = d.pop("shardCount", UNSET)

        object_count = d.pop("objectCount", UNSET)

        node_stats = cls(
            shard_count=shard_count,
            object_count=object_count,
        )

        node_stats.additional_properties = d
        return node_stats

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
