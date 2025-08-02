from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deprecation import Deprecation
    from ..models.object_ import Object


T = TypeVar("T", bound="ObjectsListResponse")


@_attrs_define
class ObjectsListResponse:
    """List of Objects.

    Attributes:
        objects (Union[Unset, list['Object']]): The actual list of Objects.
        deprecations (Union[Unset, list['Deprecation']]):
        total_results (Union[Unset, int]): The total number of Objects for the query. The number of items in a response
            may be smaller due to paging.
    """

    objects: Union[Unset, list["Object"]] = UNSET
    deprecations: Union[Unset, list["Deprecation"]] = UNSET
    total_results: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        objects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.objects, Unset):
            objects = []
            for objects_item_data in self.objects:
                objects_item = objects_item_data.to_dict()
                objects.append(objects_item)

        deprecations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.deprecations, Unset):
            deprecations = []
            for deprecations_item_data in self.deprecations:
                deprecations_item = deprecations_item_data.to_dict()
                deprecations.append(deprecations_item)

        total_results = self.total_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if objects is not UNSET:
            field_dict["objects"] = objects
        if deprecations is not UNSET:
            field_dict["deprecations"] = deprecations
        if total_results is not UNSET:
            field_dict["totalResults"] = total_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deprecation import Deprecation
        from ..models.object_ import Object

        d = dict(src_dict)
        objects = []
        _objects = d.pop("objects", UNSET)
        for objects_item_data in _objects or []:
            objects_item = Object.from_dict(objects_item_data)

            objects.append(objects_item)

        deprecations = []
        _deprecations = d.pop("deprecations", UNSET)
        for deprecations_item_data in _deprecations or []:
            deprecations_item = Deprecation.from_dict(deprecations_item_data)

            deprecations.append(deprecations_item)

        total_results = d.pop("totalResults", UNSET)

        objects_list_response = cls(
            objects=objects,
            deprecations=deprecations,
            total_results=total_results,
        )

        objects_list_response.additional_properties = d
        return objects_list_response

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
