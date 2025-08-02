from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_type_input import UserTypeInput
from ..types import UNSET, Unset

T = TypeVar("T", bound="Principal")


@_attrs_define
class Principal:
    """
    Attributes:
        username (Union[Unset, str]): The username that was extracted either from the authentication information
        groups (Union[Unset, list[str]]):
        user_type (Union[Unset, UserTypeInput]): the type of user
    """

    username: Union[Unset, str] = UNSET
    groups: Union[Unset, list[str]] = UNSET
    user_type: Union[Unset, UserTypeInput] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        groups: Union[Unset, list[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        user_type: Union[Unset, str] = UNSET
        if not isinstance(self.user_type, Unset):
            user_type = self.user_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if groups is not UNSET:
            field_dict["groups"] = groups
        if user_type is not UNSET:
            field_dict["userType"] = user_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username", UNSET)

        groups = cast(list[str], d.pop("groups", UNSET))

        _user_type = d.pop("userType", UNSET)
        user_type: Union[Unset, UserTypeInput]
        if isinstance(_user_type, Unset):
            user_type = UNSET
        else:
            user_type = UserTypeInput(_user_type)

        principal = cls(
            username=username,
            groups=groups,
            user_type=user_type,
        )

        principal.additional_properties = d
        return principal

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
