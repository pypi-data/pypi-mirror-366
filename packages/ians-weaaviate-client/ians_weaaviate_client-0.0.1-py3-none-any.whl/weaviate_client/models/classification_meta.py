import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationMeta")


@_attrs_define
class ClassificationMeta:
    """Additional information to a specific classification

    Attributes:
        started (Union[Unset, datetime.datetime]): time when this classification was started Example: 2017-07-21
            17:32:28+00:00.
        completed (Union[Unset, datetime.datetime]): time when this classification finished Example: 2017-07-21
            17:32:28+00:00.
        count (Union[Unset, int]): number of objects which were taken into consideration for classification Example:
            147.
        count_succeeded (Union[Unset, int]): number of objects successfully classified Example: 140.
        count_failed (Union[Unset, int]): number of objects which could not be classified - see error message for
            details Example: 7.
    """

    started: Union[Unset, datetime.datetime] = UNSET
    completed: Union[Unset, datetime.datetime] = UNSET
    count: Union[Unset, int] = UNSET
    count_succeeded: Union[Unset, int] = UNSET
    count_failed: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        started: Union[Unset, str] = UNSET
        if not isinstance(self.started, Unset):
            started = self.started.isoformat()

        completed: Union[Unset, str] = UNSET
        if not isinstance(self.completed, Unset):
            completed = self.completed.isoformat()

        count = self.count

        count_succeeded = self.count_succeeded

        count_failed = self.count_failed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if started is not UNSET:
            field_dict["started"] = started
        if completed is not UNSET:
            field_dict["completed"] = completed
        if count is not UNSET:
            field_dict["count"] = count
        if count_succeeded is not UNSET:
            field_dict["countSucceeded"] = count_succeeded
        if count_failed is not UNSET:
            field_dict["countFailed"] = count_failed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _started = d.pop("started", UNSET)
        started: Union[Unset, datetime.datetime]
        if isinstance(_started, Unset):
            started = UNSET
        else:
            started = isoparse(_started)

        _completed = d.pop("completed", UNSET)
        completed: Union[Unset, datetime.datetime]
        if isinstance(_completed, Unset):
            completed = UNSET
        else:
            completed = isoparse(_completed)

        count = d.pop("count", UNSET)

        count_succeeded = d.pop("countSucceeded", UNSET)

        count_failed = d.pop("countFailed", UNSET)

        classification_meta = cls(
            started=started,
            completed=completed,
            count=count,
            count_succeeded=count_succeeded,
            count_failed=count_failed,
        )

        classification_meta.additional_properties = d
        return classification_meta

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
