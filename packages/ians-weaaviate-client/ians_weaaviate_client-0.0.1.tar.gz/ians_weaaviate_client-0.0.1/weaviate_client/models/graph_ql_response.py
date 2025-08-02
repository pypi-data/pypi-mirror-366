from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_ql_error import GraphQLError
    from ..models.graph_ql_response_data import GraphQLResponseData


T = TypeVar("T", bound="GraphQLResponse")


@_attrs_define
class GraphQLResponse:
    """GraphQL based response: http://facebook.github.io/graphql/.

    Attributes:
        data (Union[Unset, GraphQLResponseData]): GraphQL data object.
        errors (Union[Unset, list['GraphQLError']]): Array with errors.
    """

    data: Union[Unset, "GraphQLResponseData"] = UNSET
    errors: Union[Unset, list["GraphQLError"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        errors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_ql_error import GraphQLError
        from ..models.graph_ql_response_data import GraphQLResponseData

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: Union[Unset, GraphQLResponseData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = GraphQLResponseData.from_dict(_data)

        errors = []
        _errors = d.pop("errors", UNSET)
        for errors_item_data in _errors or []:
            errors_item = GraphQLError.from_dict(errors_item_data)

            errors.append(errors_item)

        graph_ql_response = cls(
            data=data,
            errors=errors,
        )

        graph_ql_response.additional_properties = d
        return graph_ql_response

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
