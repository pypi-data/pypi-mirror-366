from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.permission_roles_scope import PermissionRolesScope
from ..types import UNSET, Unset

T = TypeVar("T", bound="PermissionRoles")


@_attrs_define
class PermissionRoles:
    """resources applicable for role actions

    Attributes:
        role (Union[Unset, str]): string or regex. if a specific role name, if left empty it will be ALL or * Default:
            '*'.
        scope (Union[Unset, PermissionRolesScope]): set the scope for the manage role permission Default:
            PermissionRolesScope.MATCH.
    """

    role: Union[Unset, str] = "*"
    scope: Union[Unset, PermissionRolesScope] = PermissionRolesScope.MATCH
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role

        scope: Union[Unset, str] = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = d.pop("role", UNSET)

        _scope = d.pop("scope", UNSET)
        scope: Union[Unset, PermissionRolesScope]
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = PermissionRolesScope(_scope)

        permission_roles = cls(
            role=role,
            scope=scope,
        )

        permission_roles.additional_properties = d
        return permission_roles

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
