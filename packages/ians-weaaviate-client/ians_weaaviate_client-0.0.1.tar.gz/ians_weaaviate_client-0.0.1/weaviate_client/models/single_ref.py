from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.property_schema import PropertySchema
    from ..models.reference_meta_classification import ReferenceMetaClassification


T = TypeVar("T", bound="SingleRef")


@_attrs_define
class SingleRef:
    """Either set beacon (direct reference) or set class and schema (concept reference)

    Attributes:
        class_ (Union[Unset, str]): If using a concept reference (rather than a direct reference), specify the desired
            class name here
        schema (Union[Unset, PropertySchema]): Names and values of an individual property. A returned response may also
            contain additional metadata, such as from classification or feature projection.
        beacon (Union[Unset, str]): If using a direct reference, specify the URI to point to the cross-ref here. Should
            be in the form of weaviate://localhost/<uuid> for the example of a local cross-ref to an object
        href (Union[Unset, str]): If using a direct reference, this read-only fields provides a link to the referenced
            resource. If 'origin' is globally configured, an absolute URI is shown - a relative URI otherwise.
        classification (Union[Unset, ReferenceMetaClassification]): This meta field contains additional info about the
            classified reference property
    """

    class_: Union[Unset, str] = UNSET
    schema: Union[Unset, "PropertySchema"] = UNSET
    beacon: Union[Unset, str] = UNSET
    href: Union[Unset, str] = UNSET
    classification: Union[Unset, "ReferenceMetaClassification"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_ = self.class_

        schema: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        beacon = self.beacon

        href = self.href

        classification: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_ is not UNSET:
            field_dict["class"] = class_
        if schema is not UNSET:
            field_dict["schema"] = schema
        if beacon is not UNSET:
            field_dict["beacon"] = beacon
        if href is not UNSET:
            field_dict["href"] = href
        if classification is not UNSET:
            field_dict["classification"] = classification

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.property_schema import PropertySchema
        from ..models.reference_meta_classification import ReferenceMetaClassification

        d = dict(src_dict)
        class_ = d.pop("class", UNSET)

        _schema = d.pop("schema", UNSET)
        schema: Union[Unset, PropertySchema]
        if isinstance(_schema, Unset):
            schema = UNSET
        else:
            schema = PropertySchema.from_dict(_schema)

        beacon = d.pop("beacon", UNSET)

        href = d.pop("href", UNSET)

        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, ReferenceMetaClassification]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = ReferenceMetaClassification.from_dict(_classification)

        single_ref = cls(
            class_=class_,
            schema=schema,
            beacon=beacon,
            href=href,
            classification=classification,
        )

        single_ref.additional_properties = d
        return single_ref

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
