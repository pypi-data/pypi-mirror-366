from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWellKnownOpenidConfigurationResponse200")


@_attrs_define
class GetWellKnownOpenidConfigurationResponse200:
    """
    Attributes:
        href (Union[Unset, str]): The Location to redirect to
        client_id (Union[Unset, str]): OAuth Client ID
        scopes (Union[Unset, list[str]]): OAuth Scopes
    """

    href: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        client_id = self.client_id

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if scopes is not UNSET:
            field_dict["scopes"] = scopes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        href = d.pop("href", UNSET)

        client_id = d.pop("clientId", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))

        get_well_known_openid_configuration_response_200 = cls(
            href=href,
            client_id=client_id,
            scopes=scopes,
        )

        get_well_known_openid_configuration_response_200.additional_properties = d
        return get_well_known_openid_configuration_response_200

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
