from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="C11YExtension")


@_attrs_define
class C11YExtension:
    """A resource describing an extension to the contextinoary, containing both the identifier and the definition of the
    extension

        Attributes:
            concept (Union[Unset, str]): The new concept you want to extend. Must be an all-lowercase single word, or a
                space delimited compound word. Examples: 'foobarium', 'my custom concept' Example: foobarium.
            definition (Union[Unset, str]): A list of space-delimited words or a sentence describing what the custom concept
                is about. Avoid using the custom concept itself. An Example definition for the custom concept 'foobarium': would
                be 'a naturally occurring element which can only be seen by programmers'
            weight (Union[Unset, float]): Weight of the definition of the new concept where 1='override existing definition
                entirely' and 0='ignore custom definition'. Note that if the custom concept is not present in the contextionary
                yet, the weight cannot be less than 1.
    """

    concept: Union[Unset, str] = UNSET
    definition: Union[Unset, str] = UNSET
    weight: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concept = self.concept

        definition = self.definition

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if concept is not UNSET:
            field_dict["concept"] = concept
        if definition is not UNSET:
            field_dict["definition"] = definition
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        concept = d.pop("concept", UNSET)

        definition = d.pop("definition", UNSET)

        weight = d.pop("weight", UNSET)

        c11y_extension = cls(
            concept=concept,
            definition=definition,
            weight=weight,
        )

        c11y_extension.additional_properties = d
        return c11y_extension

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
