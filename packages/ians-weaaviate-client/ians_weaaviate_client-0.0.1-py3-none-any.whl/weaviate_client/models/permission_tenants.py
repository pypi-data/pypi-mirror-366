from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PermissionTenants")


@_attrs_define
class PermissionTenants:
    """resources applicable for tenant actions

    Attributes:
        collection (Union[Unset, str]): string or regex. if a specific collection name, if left empty it will be ALL or
            * Default: '*'.
        tenant (Union[Unset, str]): string or regex. if a specific tenant name, if left empty it will be ALL or *
            Default: '*'.
    """

    collection: Union[Unset, str] = "*"
    tenant: Union[Unset, str] = "*"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection = self.collection

        tenant = self.tenant

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collection is not UNSET:
            field_dict["collection"] = collection
        if tenant is not UNSET:
            field_dict["tenant"] = tenant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collection = d.pop("collection", UNSET)

        tenant = d.pop("tenant", UNSET)

        permission_tenants = cls(
            collection=collection,
            tenant=tenant,
        )

        permission_tenants.additional_properties = d
        return permission_tenants

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
