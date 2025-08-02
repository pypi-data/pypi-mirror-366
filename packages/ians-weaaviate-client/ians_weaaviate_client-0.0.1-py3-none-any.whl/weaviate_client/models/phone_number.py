from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PhoneNumber")


@_attrs_define
class PhoneNumber:
    """
    Attributes:
        input_ (Union[Unset, str]): The raw input as the phone number is present in your raw data set. It will be parsed
            into the standardized formats if valid.
        international_formatted (Union[Unset, str]): Read-only. Parsed result in the international format (e.g. +49 123
            ...)
        default_country (Union[Unset, str]): Optional. The ISO 3166-1 alpha-2 country code. This is used to figure out
            the correct countryCode and international format if only a national number (e.g. 0123 4567) is provided
        country_code (Union[Unset, float]): Read-only. The numerical country code (e.g. 49)
        national (Union[Unset, float]): Read-only. The numerical representation of the national part
        national_formatted (Union[Unset, str]): Read-only. Parsed result in the national format (e.g. 0123 456789)
        valid (Union[Unset, bool]): Read-only. Indicates whether the parsed number is a valid phone number
    """

    input_: Union[Unset, str] = UNSET
    international_formatted: Union[Unset, str] = UNSET
    default_country: Union[Unset, str] = UNSET
    country_code: Union[Unset, float] = UNSET
    national: Union[Unset, float] = UNSET
    national_formatted: Union[Unset, str] = UNSET
    valid: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_ = self.input_

        international_formatted = self.international_formatted

        default_country = self.default_country

        country_code = self.country_code

        national = self.national

        national_formatted = self.national_formatted

        valid = self.valid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if input_ is not UNSET:
            field_dict["input"] = input_
        if international_formatted is not UNSET:
            field_dict["internationalFormatted"] = international_formatted
        if default_country is not UNSET:
            field_dict["defaultCountry"] = default_country
        if country_code is not UNSET:
            field_dict["countryCode"] = country_code
        if national is not UNSET:
            field_dict["national"] = national
        if national_formatted is not UNSET:
            field_dict["nationalFormatted"] = national_formatted
        if valid is not UNSET:
            field_dict["valid"] = valid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_ = d.pop("input", UNSET)

        international_formatted = d.pop("internationalFormatted", UNSET)

        default_country = d.pop("defaultCountry", UNSET)

        country_code = d.pop("countryCode", UNSET)

        national = d.pop("national", UNSET)

        national_formatted = d.pop("nationalFormatted", UNSET)

        valid = d.pop("valid", UNSET)

        phone_number = cls(
            input_=input_,
            international_formatted=international_formatted,
            default_country=default_country,
            country_code=country_code,
            national=national,
            national_formatted=national_formatted,
            valid=valid,
        )

        phone_number.additional_properties = d
        return phone_number

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
