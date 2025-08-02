from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PermissionAliases")


@_attrs_define
class PermissionAliases:
    """Resource definition for alias-related actions and permissions. Used to specify which aliases and collections can be
    accessed or modified.

        Attributes:
            collection (Union[Unset, str]): A string that specifies which collections this permission applies to. Can be an
                exact collection name or a regex pattern. The default value `*` applies the permission to all collections.
                Default: '*'.
            alias (Union[Unset, str]): A string that specifies which aliases this permission applies to. Can be an exact
                alias name or a regex pattern. The default value `*` applies the permission to all aliases. Default: '*'.
    """

    collection: Union[Unset, str] = "*"
    alias: Union[Unset, str] = "*"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection = self.collection

        alias = self.alias

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collection is not UNSET:
            field_dict["collection"] = collection
        if alias is not UNSET:
            field_dict["alias"] = alias

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collection = d.pop("collection", UNSET)

        alias = d.pop("alias", UNSET)

        permission_aliases = cls(
            collection=collection,
            alias=alias,
        )

        permission_aliases.additional_properties = d
        return permission_aliases

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
