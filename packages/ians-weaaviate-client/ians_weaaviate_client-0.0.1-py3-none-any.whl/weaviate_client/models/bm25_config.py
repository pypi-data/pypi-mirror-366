from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BM25Config")


@_attrs_define
class BM25Config:
    """tuning parameters for the BM25 algorithm

    Attributes:
        k1 (Union[Unset, float]): Calibrates term-weight scaling based on the term frequency within a document (default:
            1.2).
        b (Union[Unset, float]): Calibrates term-weight scaling based on the document length (default: 0.75).
    """

    k1: Union[Unset, float] = UNSET
    b: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        k1 = self.k1

        b = self.b

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if k1 is not UNSET:
            field_dict["k1"] = k1
        if b is not UNSET:
            field_dict["b"] = b

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        k1 = d.pop("k1", UNSET)

        b = d.pop("b", UNSET)

        bm25_config = cls(
            k1=k1,
            b=b,
        )

        bm25_config.additional_properties = d
        return bm25_config

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
