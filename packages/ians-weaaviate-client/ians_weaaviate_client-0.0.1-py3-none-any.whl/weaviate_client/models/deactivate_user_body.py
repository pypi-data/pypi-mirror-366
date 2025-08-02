from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeactivateUserBody")


@_attrs_define
class DeactivateUserBody:
    """
    Attributes:
        revoke_key (Union[Unset, bool]): if the key should be revoked when deactivating the user Default: False.
    """

    revoke_key: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        revoke_key = self.revoke_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if revoke_key is not UNSET:
            field_dict["revoke_key"] = revoke_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        revoke_key = d.pop("revoke_key", UNSET)

        deactivate_user_body = cls(
            revoke_key=revoke_key,
        )

        deactivate_user_body.additional_properties = d
        return deactivate_user_body

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
