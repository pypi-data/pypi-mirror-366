from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_type_input import UserTypeInput
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssignRoleToUserBody")


@_attrs_define
class AssignRoleToUserBody:
    """
    Attributes:
        roles (Union[Unset, list[str]]): the roles that assigned to user
        user_type (Union[Unset, UserTypeInput]): the type of user
    """

    roles: Union[Unset, list[str]] = UNSET
    user_type: Union[Unset, UserTypeInput] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        user_type: Union[Unset, str] = UNSET
        if not isinstance(self.user_type, Unset):
            user_type = self.user_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if roles is not UNSET:
            field_dict["roles"] = roles
        if user_type is not UNSET:
            field_dict["userType"] = user_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        roles = cast(list[str], d.pop("roles", UNSET))

        _user_type = d.pop("userType", UNSET)
        user_type: Union[Unset, UserTypeInput]
        if isinstance(_user_type, Unset):
            user_type = UNSET
        else:
            user_type = UserTypeInput(_user_type)

        assign_role_to_user_body = cls(
            roles=roles,
            user_type=user_type,
        )

        assign_role_to_user_body.additional_properties = d
        return assign_role_to_user_body

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
