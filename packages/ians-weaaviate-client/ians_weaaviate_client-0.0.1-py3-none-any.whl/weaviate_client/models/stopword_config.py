from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StopwordConfig")


@_attrs_define
class StopwordConfig:
    """fine-grained control over stopword list usage

    Attributes:
        preset (Union[Unset, str]): Pre-existing list of common words by language (default: 'en'). Options: ['en',
            'none'].
        additions (Union[Unset, list[str]]): Stopwords to be considered additionally (default: []). Can be any array of
            custom strings.
        removals (Union[Unset, list[str]]): Stopwords to be removed from consideration (default: []). Can be any array
            of custom strings.
    """

    preset: Union[Unset, str] = UNSET
    additions: Union[Unset, list[str]] = UNSET
    removals: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        preset = self.preset

        additions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.additions, Unset):
            additions = self.additions

        removals: Union[Unset, list[str]] = UNSET
        if not isinstance(self.removals, Unset):
            removals = self.removals

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if preset is not UNSET:
            field_dict["preset"] = preset
        if additions is not UNSET:
            field_dict["additions"] = additions
        if removals is not UNSET:
            field_dict["removals"] = removals

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        preset = d.pop("preset", UNSET)

        additions = cast(list[str], d.pop("additions", UNSET))

        removals = cast(list[str], d.pop("removals", UNSET))

        stopword_config = cls(
            preset=preset,
            additions=additions,
            removals=removals,
        )

        stopword_config.additional_properties = d
        return stopword_config

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
