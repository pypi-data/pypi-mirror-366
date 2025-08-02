from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.db_user_info_db_user_type import DBUserInfoDbUserType

T = TypeVar("T", bound="DBUserInfo")


@_attrs_define
class DBUserInfo:
    """
    Attributes:
        roles (list[str]): The role names associated to the user
        user_id (str): The user id of the given user
        db_user_type (DBUserInfoDbUserType): type of the returned user
        active (bool): activity status of the returned user
    """

    roles: list[str]
    user_id: str
    db_user_type: DBUserInfoDbUserType
    active: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        roles = self.roles

        user_id = self.user_id

        db_user_type = self.db_user_type.value

        active = self.active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "roles": roles,
                "userId": user_id,
                "dbUserType": db_user_type,
                "active": active,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        roles = cast(list[str], d.pop("roles"))

        user_id = d.pop("userId")

        db_user_type = DBUserInfoDbUserType(d.pop("dbUserType"))

        active = d.pop("active")

        db_user_info = cls(
            roles=roles,
            user_id=user_id,
            db_user_type=db_user_type,
            active=active,
        )

        db_user_info.additional_properties = d
        return db_user_info

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
