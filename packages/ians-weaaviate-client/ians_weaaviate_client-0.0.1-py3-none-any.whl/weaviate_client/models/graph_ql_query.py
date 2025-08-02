from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_ql_query_variables import GraphQLQueryVariables


T = TypeVar("T", bound="GraphQLQuery")


@_attrs_define
class GraphQLQuery:
    """GraphQL query based on: http://facebook.github.io/graphql/.

    Attributes:
        operation_name (Union[Unset, str]): The name of the operation if multiple exist in the query.
        query (Union[Unset, str]): Query based on GraphQL syntax.
        variables (Union[Unset, GraphQLQueryVariables]): Additional variables for the query.
    """

    operation_name: Union[Unset, str] = UNSET
    query: Union[Unset, str] = UNSET
    variables: Union[Unset, "GraphQLQueryVariables"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operation_name = self.operation_name

        query = self.query

        variables: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if operation_name is not UNSET:
            field_dict["operationName"] = operation_name
        if query is not UNSET:
            field_dict["query"] = query
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_ql_query_variables import GraphQLQueryVariables

        d = dict(src_dict)
        operation_name = d.pop("operationName", UNSET)

        query = d.pop("query", UNSET)

        _variables = d.pop("variables", UNSET)
        variables: Union[Unset, GraphQLQueryVariables]
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = GraphQLQueryVariables.from_dict(_variables)

        graph_ql_query = cls(
            operation_name=operation_name,
            query=query,
            variables=variables,
        )

        graph_ql_query.additional_properties = d
        return graph_ql_query

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
