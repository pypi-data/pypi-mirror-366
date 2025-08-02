from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c11y_nearest_neighbors_item import C11YNearestNeighborsItem


T = TypeVar("T", bound="C11YWordsResponseIndividualWordsItemInfo")


@_attrs_define
class C11YWordsResponseIndividualWordsItemInfo:
    """
    Attributes:
        vector (Union[Unset, list[float]]): A vector representation of the object in the Contextionary. If provided at
            object creation, this wil take precedence over any vectorizer setting.
        nearest_neighbors (Union[Unset, list['C11YNearestNeighborsItem']]): C11y function to show the nearest neighbors
            to a word.
    """

    vector: Union[Unset, list[float]] = UNSET
    nearest_neighbors: Union[Unset, list["C11YNearestNeighborsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vector: Union[Unset, list[float]] = UNSET
        if not isinstance(self.vector, Unset):
            vector = self.vector

        nearest_neighbors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nearest_neighbors, Unset):
            nearest_neighbors = []
            for componentsschemas_c11_y_nearest_neighbors_item_data in self.nearest_neighbors:
                componentsschemas_c11_y_nearest_neighbors_item = (
                    componentsschemas_c11_y_nearest_neighbors_item_data.to_dict()
                )
                nearest_neighbors.append(componentsschemas_c11_y_nearest_neighbors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vector is not UNSET:
            field_dict["vector"] = vector
        if nearest_neighbors is not UNSET:
            field_dict["nearestNeighbors"] = nearest_neighbors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.c11y_nearest_neighbors_item import C11YNearestNeighborsItem

        d = dict(src_dict)
        vector = cast(list[float], d.pop("vector", UNSET))

        nearest_neighbors = []
        _nearest_neighbors = d.pop("nearestNeighbors", UNSET)
        for componentsschemas_c11_y_nearest_neighbors_item_data in _nearest_neighbors or []:
            componentsschemas_c11_y_nearest_neighbors_item = C11YNearestNeighborsItem.from_dict(
                componentsschemas_c11_y_nearest_neighbors_item_data
            )

            nearest_neighbors.append(componentsschemas_c11_y_nearest_neighbors_item)

        c11y_words_response_individual_words_item_info = cls(
            vector=vector,
            nearest_neighbors=nearest_neighbors,
        )

        c11y_words_response_individual_words_item_info.additional_properties = d
        return c11y_words_response_individual_words_item_info

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
