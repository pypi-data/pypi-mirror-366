from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReferenceMetaClassification")


@_attrs_define
class ReferenceMetaClassification:
    """This meta field contains additional info about the classified reference property

    Attributes:
        overall_count (Union[Unset, float]): overall neighbors checked as part of the classification. In most cases this
            will equal k, but could be lower than k - for example if not enough data was present
        winning_count (Union[Unset, float]): size of the winning group, a number between 1..k
        losing_count (Union[Unset, float]): size of the losing group, can be 0 if the winning group size equals k
        closest_overall_distance (Union[Unset, float]): The lowest distance of any neighbor, regardless of whether they
            were in the winning or losing group
        winning_distance (Union[Unset, float]): deprecated - do not use, to be removed in 0.23.0
        mean_winning_distance (Union[Unset, float]): Mean distance of all neighbors from the winning group
        closest_winning_distance (Union[Unset, float]): Closest distance of a neighbor from the winning group
        closest_losing_distance (Union[None, Unset, float]): The lowest distance of a neighbor in the losing group.
            Optional. If k equals the size of the winning group, there is no losing group
        losing_distance (Union[None, Unset, float]): deprecated - do not use, to be removed in 0.23.0
        mean_losing_distance (Union[None, Unset, float]): Mean distance of all neighbors from the losing group.
            Optional. If k equals the size of the winning group, there is no losing group.
    """

    overall_count: Union[Unset, float] = UNSET
    winning_count: Union[Unset, float] = UNSET
    losing_count: Union[Unset, float] = UNSET
    closest_overall_distance: Union[Unset, float] = UNSET
    winning_distance: Union[Unset, float] = UNSET
    mean_winning_distance: Union[Unset, float] = UNSET
    closest_winning_distance: Union[Unset, float] = UNSET
    closest_losing_distance: Union[None, Unset, float] = UNSET
    losing_distance: Union[None, Unset, float] = UNSET
    mean_losing_distance: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overall_count = self.overall_count

        winning_count = self.winning_count

        losing_count = self.losing_count

        closest_overall_distance = self.closest_overall_distance

        winning_distance = self.winning_distance

        mean_winning_distance = self.mean_winning_distance

        closest_winning_distance = self.closest_winning_distance

        closest_losing_distance: Union[None, Unset, float]
        if isinstance(self.closest_losing_distance, Unset):
            closest_losing_distance = UNSET
        else:
            closest_losing_distance = self.closest_losing_distance

        losing_distance: Union[None, Unset, float]
        if isinstance(self.losing_distance, Unset):
            losing_distance = UNSET
        else:
            losing_distance = self.losing_distance

        mean_losing_distance: Union[None, Unset, float]
        if isinstance(self.mean_losing_distance, Unset):
            mean_losing_distance = UNSET
        else:
            mean_losing_distance = self.mean_losing_distance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if overall_count is not UNSET:
            field_dict["overallCount"] = overall_count
        if winning_count is not UNSET:
            field_dict["winningCount"] = winning_count
        if losing_count is not UNSET:
            field_dict["losingCount"] = losing_count
        if closest_overall_distance is not UNSET:
            field_dict["closestOverallDistance"] = closest_overall_distance
        if winning_distance is not UNSET:
            field_dict["winningDistance"] = winning_distance
        if mean_winning_distance is not UNSET:
            field_dict["meanWinningDistance"] = mean_winning_distance
        if closest_winning_distance is not UNSET:
            field_dict["closestWinningDistance"] = closest_winning_distance
        if closest_losing_distance is not UNSET:
            field_dict["closestLosingDistance"] = closest_losing_distance
        if losing_distance is not UNSET:
            field_dict["losingDistance"] = losing_distance
        if mean_losing_distance is not UNSET:
            field_dict["meanLosingDistance"] = mean_losing_distance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        overall_count = d.pop("overallCount", UNSET)

        winning_count = d.pop("winningCount", UNSET)

        losing_count = d.pop("losingCount", UNSET)

        closest_overall_distance = d.pop("closestOverallDistance", UNSET)

        winning_distance = d.pop("winningDistance", UNSET)

        mean_winning_distance = d.pop("meanWinningDistance", UNSET)

        closest_winning_distance = d.pop("closestWinningDistance", UNSET)

        def _parse_closest_losing_distance(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        closest_losing_distance = _parse_closest_losing_distance(d.pop("closestLosingDistance", UNSET))

        def _parse_losing_distance(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        losing_distance = _parse_losing_distance(d.pop("losingDistance", UNSET))

        def _parse_mean_losing_distance(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        mean_losing_distance = _parse_mean_losing_distance(d.pop("meanLosingDistance", UNSET))

        reference_meta_classification = cls(
            overall_count=overall_count,
            winning_count=winning_count,
            losing_count=losing_count,
            closest_overall_distance=closest_overall_distance,
            winning_distance=winning_distance,
            mean_winning_distance=mean_winning_distance,
            closest_winning_distance=closest_winning_distance,
            closest_losing_distance=closest_losing_distance,
            losing_distance=losing_distance,
            mean_losing_distance=mean_losing_distance,
        )

        reference_meta_classification.additional_properties = d
        return reference_meta_classification

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
