from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.where_filter import WhereFilter


T = TypeVar("T", bound="ClassificationFilters")


@_attrs_define
class ClassificationFilters:
    """
    Attributes:
        source_where (Union[Unset, WhereFilter]): Filter search results using a where filter
        training_set_where (Union[Unset, WhereFilter]): Filter search results using a where filter
        target_where (Union[Unset, WhereFilter]): Filter search results using a where filter
    """

    source_where: Union[Unset, "WhereFilter"] = UNSET
    training_set_where: Union[Unset, "WhereFilter"] = UNSET
    target_where: Union[Unset, "WhereFilter"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_where: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.source_where, Unset):
            source_where = self.source_where.to_dict()

        training_set_where: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.training_set_where, Unset):
            training_set_where = self.training_set_where.to_dict()

        target_where: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.target_where, Unset):
            target_where = self.target_where.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source_where is not UNSET:
            field_dict["sourceWhere"] = source_where
        if training_set_where is not UNSET:
            field_dict["trainingSetWhere"] = training_set_where
        if target_where is not UNSET:
            field_dict["targetWhere"] = target_where

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.where_filter import WhereFilter

        d = dict(src_dict)
        _source_where = d.pop("sourceWhere", UNSET)
        source_where: Union[Unset, WhereFilter]
        if isinstance(_source_where, Unset):
            source_where = UNSET
        else:
            source_where = WhereFilter.from_dict(_source_where)

        _training_set_where = d.pop("trainingSetWhere", UNSET)
        training_set_where: Union[Unset, WhereFilter]
        if isinstance(_training_set_where, Unset):
            training_set_where = UNSET
        else:
            training_set_where = WhereFilter.from_dict(_training_set_where)

        _target_where = d.pop("targetWhere", UNSET)
        target_where: Union[Unset, WhereFilter]
        if isinstance(_target_where, Unset):
            target_where = UNSET
        else:
            target_where = WhereFilter.from_dict(_target_where)

        classification_filters = cls(
            source_where=source_where,
            training_set_where=training_set_where,
            target_where=target_where,
        )

        classification_filters.additional_properties = d
        return classification_filters

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
