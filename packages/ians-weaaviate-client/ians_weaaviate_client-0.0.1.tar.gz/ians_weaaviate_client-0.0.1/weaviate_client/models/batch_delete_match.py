from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.where_filter import WhereFilter


T = TypeVar("T", bound="BatchDeleteMatch")


@_attrs_define
class BatchDeleteMatch:
    """Outlines how to find the objects to be deleted.

    Attributes:
        class_ (Union[Unset, str]): Class (name) which objects will be deleted. Example: City.
        where (Union[Unset, WhereFilter]): Filter search results using a where filter
    """

    class_: Union[Unset, str] = UNSET
    where: Union[Unset, "WhereFilter"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_ = self.class_

        where: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.where, Unset):
            where = self.where.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_ is not UNSET:
            field_dict["class"] = class_
        if where is not UNSET:
            field_dict["where"] = where

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.where_filter import WhereFilter

        d = dict(src_dict)
        class_ = d.pop("class", UNSET)

        _where = d.pop("where", UNSET)
        where: Union[Unset, WhereFilter]
        if isinstance(_where, Unset):
            where = UNSET
        else:
            where = WhereFilter.from_dict(_where)

        batch_delete_match = cls(
            class_=class_,
            where=where,
        )

        batch_delete_match.additional_properties = d
        return batch_delete_match

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
