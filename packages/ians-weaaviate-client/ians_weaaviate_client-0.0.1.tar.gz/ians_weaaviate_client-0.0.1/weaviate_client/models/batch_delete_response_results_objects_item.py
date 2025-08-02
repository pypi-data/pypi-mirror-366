from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.batch_delete_response_results_objects_item_status import BatchDeleteResponseResultsObjectsItemStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_response import ErrorResponse


T = TypeVar("T", bound="BatchDeleteResponseResultsObjectsItem")


@_attrs_define
class BatchDeleteResponseResultsObjectsItem:
    """Results for this specific Object.

    Attributes:
        id (Union[Unset, UUID]): ID of the Object.
        status (Union[Unset, BatchDeleteResponseResultsObjectsItemStatus]):  Default:
            BatchDeleteResponseResultsObjectsItemStatus.SUCCESS.
        errors (Union[Unset, ErrorResponse]): An error response given by Weaviate end-points.
    """

    id: Union[Unset, UUID] = UNSET
    status: Union[Unset, BatchDeleteResponseResultsObjectsItemStatus] = (
        BatchDeleteResponseResultsObjectsItemStatus.SUCCESS
    )
    errors: Union[Unset, "ErrorResponse"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        errors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_response import ErrorResponse

        d = dict(src_dict)
        _id = d.pop("id", UNSET)
        id: Union[Unset, UUID]
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        _status = d.pop("status", UNSET)
        status: Union[Unset, BatchDeleteResponseResultsObjectsItemStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = BatchDeleteResponseResultsObjectsItemStatus(_status)

        _errors = d.pop("errors", UNSET)
        errors: Union[Unset, ErrorResponse]
        if isinstance(_errors, Unset):
            errors = UNSET
        else:
            errors = ErrorResponse.from_dict(_errors)

        batch_delete_response_results_objects_item = cls(
            id=id,
            status=status,
            errors=errors,
        )

        batch_delete_response_results_objects_item.additional_properties = d
        return batch_delete_response_results_objects_item

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
