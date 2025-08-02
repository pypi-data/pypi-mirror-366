from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geo_coordinates import GeoCoordinates
    from ..models.where_filter_geo_range_distance import WhereFilterGeoRangeDistance


T = TypeVar("T", bound="WhereFilterGeoRange")


@_attrs_define
class WhereFilterGeoRange:
    """filter within a distance of a georange

    Attributes:
        geo_coordinates (Union[Unset, GeoCoordinates]):
        distance (Union[Unset, WhereFilterGeoRangeDistance]):
    """

    geo_coordinates: Union[Unset, "GeoCoordinates"] = UNSET
    distance: Union[Unset, "WhereFilterGeoRangeDistance"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        geo_coordinates: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.geo_coordinates, Unset):
            geo_coordinates = self.geo_coordinates.to_dict()

        distance: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.distance, Unset):
            distance = self.distance.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if geo_coordinates is not UNSET:
            field_dict["geoCoordinates"] = geo_coordinates
        if distance is not UNSET:
            field_dict["distance"] = distance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geo_coordinates import GeoCoordinates
        from ..models.where_filter_geo_range_distance import WhereFilterGeoRangeDistance

        d = dict(src_dict)
        _geo_coordinates = d.pop("geoCoordinates", UNSET)
        geo_coordinates: Union[Unset, GeoCoordinates]
        if isinstance(_geo_coordinates, Unset):
            geo_coordinates = UNSET
        else:
            geo_coordinates = GeoCoordinates.from_dict(_geo_coordinates)

        _distance = d.pop("distance", UNSET)
        distance: Union[Unset, WhereFilterGeoRangeDistance]
        if isinstance(_distance, Unset):
            distance = UNSET
        else:
            distance = WhereFilterGeoRangeDistance.from_dict(_distance)

        where_filter_geo_range = cls(
            geo_coordinates=geo_coordinates,
            distance=distance,
        )

        where_filter_geo_range.additional_properties = d
        return where_filter_geo_range

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
