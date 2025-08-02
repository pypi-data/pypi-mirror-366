from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_ql_error_locations_item import GraphQLErrorLocationsItem


T = TypeVar("T", bound="GraphQLError")


@_attrs_define
class GraphQLError:
    """An error response caused by a GraphQL query.

    Attributes:
        locations (Union[Unset, list['GraphQLErrorLocationsItem']]):
        message (Union[Unset, str]):
        path (Union[Unset, list[str]]):
    """

    locations: Union[Unset, list["GraphQLErrorLocationsItem"]] = UNSET
    message: Union[Unset, str] = UNSET
    path: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        message = self.message

        path: Union[Unset, list[str]] = UNSET
        if not isinstance(self.path, Unset):
            path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if locations is not UNSET:
            field_dict["locations"] = locations
        if message is not UNSET:
            field_dict["message"] = message
        if path is not UNSET:
            field_dict["path"] = path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_ql_error_locations_item import GraphQLErrorLocationsItem

        d = dict(src_dict)
        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = GraphQLErrorLocationsItem.from_dict(locations_item_data)

            locations.append(locations_item)

        message = d.pop("message", UNSET)

        path = cast(list[str], d.pop("path", UNSET))

        graph_ql_error = cls(
            locations=locations,
            message=message,
            path=path,
        )

        graph_ql_error.additional_properties = d
        return graph_ql_error

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
