from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_response_error_item import ErrorResponseErrorItem


T = TypeVar("T", bound="ErrorResponse")


@_attrs_define
class ErrorResponse:
    """An error response given by Weaviate end-points.

    Attributes:
        error (Union[Unset, list['ErrorResponseErrorItem']]):
    """

    error: Union[Unset, list["ErrorResponseErrorItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.error, Unset):
            error = []
            for error_item_data in self.error:
                error_item = error_item_data.to_dict()
                error.append(error_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_response_error_item import ErrorResponseErrorItem

        d = dict(src_dict)
        error = []
        _error = d.pop("error", UNSET)
        for error_item_data in _error or []:
            error_item = ErrorResponseErrorItem.from_dict(error_item_data)

            error.append(error_item)

        error_response = cls(
            error=error,
        )

        error_response.additional_properties = d
        return error_response

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
