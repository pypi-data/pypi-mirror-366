from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_reference_response_result import BatchReferenceResponseResult


T = TypeVar("T", bound="BatchReferenceResponse")


@_attrs_define
class BatchReferenceResponse:
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
        result (Union[Unset, BatchReferenceResponseResult]): Results for this specific reference.
    """

    from_: Union[Unset, str] = UNSET
    to: Union[Unset, str] = UNSET
    tenant: Union[Unset, str] = UNSET
    result: Union[Unset, "BatchReferenceResponseResult"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_ = self.from_

        to = self.to

        tenant = self.tenant

        result: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_reference_response_result import BatchReferenceResponseResult

        d = dict(src_dict)
        from_ = d.pop("from", UNSET)

        to = d.pop("to", UNSET)

        tenant = d.pop("tenant", UNSET)

        _result = d.pop("result", UNSET)
        result: Union[Unset, BatchReferenceResponseResult]
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = BatchReferenceResponseResult.from_dict(_result)

        batch_reference_response = cls(
            from_=from_,
            to=to,
            tenant=tenant,
            result=result,
        )

        batch_reference_response.additional_properties = d
        return batch_reference_response

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
