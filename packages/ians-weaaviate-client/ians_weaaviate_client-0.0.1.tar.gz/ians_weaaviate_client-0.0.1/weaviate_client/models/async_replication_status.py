from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AsyncReplicationStatus")


@_attrs_define
class AsyncReplicationStatus:
    """The status of the async replication.

    Attributes:
        objects_propagated (Union[Unset, float]): The number of objects propagated in the most recent iteration.
        start_diff_time_unix_millis (Union[Unset, float]): The start time of the most recent iteration.
        target_node (Union[Unset, str]): The target node of the replication, if set, otherwise empty.
    """

    objects_propagated: Union[Unset, float] = UNSET
    start_diff_time_unix_millis: Union[Unset, float] = UNSET
    target_node: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        objects_propagated = self.objects_propagated

        start_diff_time_unix_millis = self.start_diff_time_unix_millis

        target_node = self.target_node

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if objects_propagated is not UNSET:
            field_dict["objectsPropagated"] = objects_propagated
        if start_diff_time_unix_millis is not UNSET:
            field_dict["startDiffTimeUnixMillis"] = start_diff_time_unix_millis
        if target_node is not UNSET:
            field_dict["targetNode"] = target_node

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        objects_propagated = d.pop("objectsPropagated", UNSET)

        start_diff_time_unix_millis = d.pop("startDiffTimeUnixMillis", UNSET)

        target_node = d.pop("targetNode", UNSET)

        async_replication_status = cls(
            objects_propagated=objects_propagated,
            start_diff_time_unix_millis=start_diff_time_unix_millis,
            target_node=target_node,
        )

        async_replication_status.additional_properties = d
        return async_replication_status

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
