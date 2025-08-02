from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchStats")


@_attrs_define
class BatchStats:
    """The summary of a nodes batch queue congestion status.

    Attributes:
        queue_length (Union[None, Unset, float]): How many objects are currently in the batch queue.
        rate_per_second (Union[Unset, float]): How many objects are approximately processed from the batch queue per
            second.
    """

    queue_length: Union[None, Unset, float] = UNSET
    rate_per_second: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        queue_length: Union[None, Unset, float]
        if isinstance(self.queue_length, Unset):
            queue_length = UNSET
        else:
            queue_length = self.queue_length

        rate_per_second = self.rate_per_second

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if queue_length is not UNSET:
            field_dict["queueLength"] = queue_length
        if rate_per_second is not UNSET:
            field_dict["ratePerSecond"] = rate_per_second

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_queue_length(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        queue_length = _parse_queue_length(d.pop("queueLength", UNSET))

        rate_per_second = d.pop("ratePerSecond", UNSET)

        batch_stats = cls(
            queue_length=queue_length,
            rate_per_second=rate_per_second,
        )

        batch_stats.additional_properties = d
        return batch_stats

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
