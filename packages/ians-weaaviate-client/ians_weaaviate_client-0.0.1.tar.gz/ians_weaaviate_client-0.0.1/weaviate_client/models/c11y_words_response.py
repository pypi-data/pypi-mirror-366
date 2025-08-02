from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c11y_words_response_concatenated_word import C11YWordsResponseConcatenatedWord
    from ..models.c11y_words_response_individual_words_item import C11YWordsResponseIndividualWordsItem


T = TypeVar("T", bound="C11YWordsResponse")


@_attrs_define
class C11YWordsResponse:
    """An array of available words and contexts.

    Attributes:
        concatenated_word (Union[Unset, C11YWordsResponseConcatenatedWord]): Weighted results for all words
        individual_words (Union[Unset, list['C11YWordsResponseIndividualWordsItem']]): Weighted results for per
            individual word
    """

    concatenated_word: Union[Unset, "C11YWordsResponseConcatenatedWord"] = UNSET
    individual_words: Union[Unset, list["C11YWordsResponseIndividualWordsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concatenated_word: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.concatenated_word, Unset):
            concatenated_word = self.concatenated_word.to_dict()

        individual_words: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.individual_words, Unset):
            individual_words = []
            for individual_words_item_data in self.individual_words:
                individual_words_item = individual_words_item_data.to_dict()
                individual_words.append(individual_words_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if concatenated_word is not UNSET:
            field_dict["concatenatedWord"] = concatenated_word
        if individual_words is not UNSET:
            field_dict["individualWords"] = individual_words

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.c11y_words_response_concatenated_word import C11YWordsResponseConcatenatedWord
        from ..models.c11y_words_response_individual_words_item import C11YWordsResponseIndividualWordsItem

        d = dict(src_dict)
        _concatenated_word = d.pop("concatenatedWord", UNSET)
        concatenated_word: Union[Unset, C11YWordsResponseConcatenatedWord]
        if isinstance(_concatenated_word, Unset):
            concatenated_word = UNSET
        else:
            concatenated_word = C11YWordsResponseConcatenatedWord.from_dict(_concatenated_word)

        individual_words = []
        _individual_words = d.pop("individualWords", UNSET)
        for individual_words_item_data in _individual_words or []:
            individual_words_item = C11YWordsResponseIndividualWordsItem.from_dict(individual_words_item_data)

            individual_words.append(individual_words_item)

        c11y_words_response = cls(
            concatenated_word=concatenated_word,
            individual_words=individual_words,
        )

        c11y_words_response.additional_properties = d
        return c11y_words_response

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
