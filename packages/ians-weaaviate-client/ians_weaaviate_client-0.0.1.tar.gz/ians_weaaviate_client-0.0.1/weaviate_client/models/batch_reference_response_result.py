from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.batch_reference_response_result_status import BatchReferenceResponseResultStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_response import ErrorResponse


T = TypeVar("T", bound="BatchReferenceResponseResult")


@_attrs_define
class BatchReferenceResponseResult:
    """Results for this specific reference.

    Attributes:
        status (Union[Unset, BatchReferenceResponseResultStatus]):  Default: BatchReferenceResponseResultStatus.SUCCESS.
        errors (Union[Unset, ErrorResponse]): An error response given by Weaviate end-points.
    """

    status: Union[Unset, BatchReferenceResponseResultStatus] = BatchReferenceResponseResultStatus.SUCCESS
    errors: Union[Unset, "ErrorResponse"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        errors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_response import ErrorResponse

        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: Union[Unset, BatchReferenceResponseResultStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = BatchReferenceResponseResultStatus(_status)

        _errors = d.pop("errors", UNSET)
        errors: Union[Unset, ErrorResponse]
        if isinstance(_errors, Unset):
            errors = UNSET
        else:
            errors = ErrorResponse.from_dict(_errors)

        batch_reference_response_result = cls(
            status=status,
            errors=errors,
        )

        batch_reference_response_result.additional_properties = d
        return batch_reference_response_result

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
