from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Link")


@_attrs_define
class Link:
    """
    Attributes:
        href (Union[Unset, str]): target of the link
        rel (Union[Unset, str]): relationship if both resources are related, e.g. 'next', 'previous', 'parent', etc.
        name (Union[Unset, str]): human readable name of the resource group
        documentation_href (Union[Unset, str]): weaviate documentation about this resource group
    """

    href: Union[Unset, str] = UNSET
    rel: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    documentation_href: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        rel = self.rel

        name = self.name

        documentation_href = self.documentation_href

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if rel is not UNSET:
            field_dict["rel"] = rel
        if name is not UNSET:
            field_dict["name"] = name
        if documentation_href is not UNSET:
            field_dict["documentationHref"] = documentation_href

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        href = d.pop("href", UNSET)

        rel = d.pop("rel", UNSET)

        name = d.pop("name", UNSET)

        documentation_href = d.pop("documentationHref", UNSET)

        link = cls(
            href=href,
            rel=rel,
            name=name,
            documentation_href=documentation_href,
        )

        link.additional_properties = d
        return link

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
