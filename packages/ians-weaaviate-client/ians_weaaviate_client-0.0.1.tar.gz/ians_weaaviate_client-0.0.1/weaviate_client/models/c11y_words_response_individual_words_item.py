from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c11y_words_response_individual_words_item_info import C11YWordsResponseIndividualWordsItemInfo


T = TypeVar("T", bound="C11YWordsResponseIndividualWordsItem")


@_attrs_define
class C11YWordsResponseIndividualWordsItem:
    """
    Attributes:
        word (Union[Unset, str]):
        present (Union[Unset, bool]):
        info (Union[Unset, C11YWordsResponseIndividualWordsItemInfo]):
    """

    word: Union[Unset, str] = UNSET
    present: Union[Unset, bool] = UNSET
    info: Union[Unset, "C11YWordsResponseIndividualWordsItemInfo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        word = self.word

        present = self.present

        info: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.info, Unset):
            info = self.info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if word is not UNSET:
            field_dict["word"] = word
        if present is not UNSET:
            field_dict["present"] = present
        if info is not UNSET:
            field_dict["info"] = info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.c11y_words_response_individual_words_item_info import C11YWordsResponseIndividualWordsItemInfo

        d = dict(src_dict)
        word = d.pop("word", UNSET)

        present = d.pop("present", UNSET)

        _info = d.pop("info", UNSET)
        info: Union[Unset, C11YWordsResponseIndividualWordsItemInfo]
        if isinstance(_info, Unset):
            info = UNSET
        else:
            info = C11YWordsResponseIndividualWordsItemInfo.from_dict(_info)

        c11y_words_response_individual_words_item = cls(
            word=word,
            present=present,
            info=info,
        )

        c11y_words_response_individual_words_item.additional_properties = d
        return c11y_words_response_individual_words_item

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
