from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statistics import Statistics


T = TypeVar("T", bound="ClusterStatisticsResponse")


@_attrs_define
class ClusterStatisticsResponse:
    """The cluster statistics of all of the Weaviate nodes

    Attributes:
        statistics (Union[Unset, list['Statistics']]):
        synchronized (Union[Unset, bool]):
    """

    statistics: Union[Unset, list["Statistics"]] = UNSET
    synchronized: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        statistics: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.statistics, Unset):
            statistics = []
            for statistics_item_data in self.statistics:
                statistics_item = statistics_item_data.to_dict()
                statistics.append(statistics_item)

        synchronized = self.synchronized

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if statistics is not UNSET:
            field_dict["statistics"] = statistics
        if synchronized is not UNSET:
            field_dict["synchronized"] = synchronized

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.statistics import Statistics

        d = dict(src_dict)
        statistics = []
        _statistics = d.pop("statistics", UNSET)
        for statistics_item_data in _statistics or []:
            statistics_item = Statistics.from_dict(statistics_item_data)

            statistics.append(statistics_item)

        synchronized = d.pop("synchronized", UNSET)

        cluster_statistics_response = cls(
            statistics=statistics,
            synchronized=synchronized,
        )

        cluster_statistics_response.additional_properties = d
        return cluster_statistics_response

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
