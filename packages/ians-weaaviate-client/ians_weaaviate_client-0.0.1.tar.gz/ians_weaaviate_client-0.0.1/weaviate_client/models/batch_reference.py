from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchReference")


@_attrs_define
class BatchReference:
    """
    Attributes:
        from_ (Union[Unset, str]): Long-form beacon-style URI to identify the source of the cross-ref including the
            property name. Should be in the form of weaviate://localhost/<kinds>/<uuid>/<className>/<propertyName>, where
            <kinds> must be one of 'objects', 'objects' and <className> and <propertyName> must represent the cross-ref
            property of source class to be used. Example:
            weaviate://localhost/Zoo/a5d09582-4239-4702-81c9-92a6e0122bb4/hasAnimals.
        to (Union[Unset, str]): Short-form URI to point to the cross-ref. Should be in the form of
            weaviate://localhost/<uuid> for the example of a local cross-ref to an object Example:
            weaviate://localhost/97525810-a9a5-4eb0-858a-71449aeb007f.
        tenant (Union[Unset, str]): Name of the reference tenant.
    """

    from_: Union[Unset, str] = UNSET
    to: Union[Unset, str] = UNSET
    tenant: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_ = self.from_

        to = self.to

        tenant = self.tenant

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if tenant is not UNSET:
            field_dict["tenant"] = tenant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        from_ = d.pop("from", UNSET)

        to = d.pop("to", UNSET)

        tenant = d.pop("tenant", UNSET)

        batch_reference = cls(
            from_=from_,
            to=to,
            tenant=tenant,
        )

        batch_reference.additional_properties = d
        return batch_reference

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
