from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.role import Role


T = TypeVar("T", bound="UserOwnInfo")


@_attrs_define
class UserOwnInfo:
    """
    Attributes:
        username (str): The username associated with the provided key
        groups (Union[Unset, list[str]]): The groups associated to the user
        roles (Union[Unset, list['Role']]):
    """

    username: str
    groups: Union[Unset, list[str]] = UNSET
    roles: Union[Unset, list["Role"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        groups: Union[Unset, list[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()
                roles.append(roles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
            }
        )
        if groups is not UNSET:
            field_dict["groups"] = groups
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role import Role

        d = dict(src_dict)
        username = d.pop("username")

        groups = cast(list[str], d.pop("groups", UNSET))

        roles = []
        _roles = d.pop("roles", UNSET)
        for roles_item_data in _roles or []:
            roles_item = Role.from_dict(roles_item_data)

            roles.append(roles_item)

        user_own_info = cls(
            username=username,
            groups=groups,
            roles=roles,
        )

        user_own_info.additional_properties = d
        return user_own_info

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
