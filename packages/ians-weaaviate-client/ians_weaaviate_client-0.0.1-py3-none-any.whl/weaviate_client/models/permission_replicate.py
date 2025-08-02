from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PermissionReplicate")


@_attrs_define
class PermissionReplicate:
    """resources applicable for replicate actions

    Attributes:
        collection (Union[Unset, str]): string or regex. if a specific collection name, if left empty it will be ALL or
            * Default: '*'.
        shard (Union[Unset, str]): string or regex. if a specific shard name, if left empty it will be ALL or * Default:
            '*'.
    """

    collection: Union[Unset, str] = "*"
    shard: Union[Unset, str] = "*"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection = self.collection

        shard = self.shard

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collection is not UNSET:
            field_dict["collection"] = collection
        if shard is not UNSET:
            field_dict["shard"] = shard

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collection = d.pop("collection", UNSET)

        shard = d.pop("shard", UNSET)

        permission_replicate = cls(
            collection=collection,
            shard=shard,
        )

        permission_replicate.additional_properties = d
        return permission_replicate

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
