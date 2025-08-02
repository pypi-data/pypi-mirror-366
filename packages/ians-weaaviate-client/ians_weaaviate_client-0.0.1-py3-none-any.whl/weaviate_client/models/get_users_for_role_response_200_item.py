from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_type_output import UserTypeOutput
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUsersForRoleResponse200Item")


@_attrs_define
class GetUsersForRoleResponse200Item:
    """
    Attributes:
        user_type (UserTypeOutput): the type of user
        user_id (Union[Unset, str]):
    """

    user_type: UserTypeOutput
    user_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_type = self.user_type.value

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userType": user_type,
            }
        )
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_type = UserTypeOutput(d.pop("userType"))

        user_id = d.pop("userId", UNSET)

        get_users_for_role_response_200_item = cls(
            user_type=user_type,
            user_id=user_id,
        )

        get_users_for_role_response_200_item.additional_properties = d
        return get_users_for_role_response_200_item

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
