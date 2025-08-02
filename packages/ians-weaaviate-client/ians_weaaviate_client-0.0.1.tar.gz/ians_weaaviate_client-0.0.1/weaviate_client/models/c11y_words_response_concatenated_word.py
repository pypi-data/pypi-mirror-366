from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c11y_nearest_neighbors_item import C11YNearestNeighborsItem
    from ..models.c11y_words_response_concatenated_word_single_words_item import (
        C11YWordsResponseConcatenatedWordSingleWordsItem,
    )


T = TypeVar("T", bound="C11YWordsResponseConcatenatedWord")


@_attrs_define
class C11YWordsResponseConcatenatedWord:
    """Weighted results for all words

    Attributes:
        concatenated_word (Union[Unset, str]):
        single_words (Union[Unset, list['C11YWordsResponseConcatenatedWordSingleWordsItem']]):
        concatenated_vector (Union[Unset, list[float]]): A vector representation of the object in the Contextionary. If
            provided at object creation, this wil take precedence over any vectorizer setting.
        concatenated_nearest_neighbors (Union[Unset, list['C11YNearestNeighborsItem']]): C11y function to show the
            nearest neighbors to a word.
    """

    concatenated_word: Union[Unset, str] = UNSET
    single_words: Union[Unset, list["C11YWordsResponseConcatenatedWordSingleWordsItem"]] = UNSET
    concatenated_vector: Union[Unset, list[float]] = UNSET
    concatenated_nearest_neighbors: Union[Unset, list["C11YNearestNeighborsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concatenated_word = self.concatenated_word

        single_words: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.single_words, Unset):
            single_words = []
            for single_words_item_data in self.single_words:
                single_words_item = single_words_item_data.to_dict()
                single_words.append(single_words_item)

        concatenated_vector: Union[Unset, list[float]] = UNSET
        if not isinstance(self.concatenated_vector, Unset):
            concatenated_vector = self.concatenated_vector

        concatenated_nearest_neighbors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.concatenated_nearest_neighbors, Unset):
            concatenated_nearest_neighbors = []
            for componentsschemas_c11_y_nearest_neighbors_item_data in self.concatenated_nearest_neighbors:
                componentsschemas_c11_y_nearest_neighbors_item = (
                    componentsschemas_c11_y_nearest_neighbors_item_data.to_dict()
                )
                concatenated_nearest_neighbors.append(componentsschemas_c11_y_nearest_neighbors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if concatenated_word is not UNSET:
            field_dict["concatenatedWord"] = concatenated_word
        if single_words is not UNSET:
            field_dict["singleWords"] = single_words
        if concatenated_vector is not UNSET:
            field_dict["concatenatedVector"] = concatenated_vector
        if concatenated_nearest_neighbors is not UNSET:
            field_dict["concatenatedNearestNeighbors"] = concatenated_nearest_neighbors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.c11y_nearest_neighbors_item import C11YNearestNeighborsItem
        from ..models.c11y_words_response_concatenated_word_single_words_item import (
            C11YWordsResponseConcatenatedWordSingleWordsItem,
        )

        d = dict(src_dict)
        concatenated_word = d.pop("concatenatedWord", UNSET)

        single_words = []
        _single_words = d.pop("singleWords", UNSET)
        for single_words_item_data in _single_words or []:
            single_words_item = C11YWordsResponseConcatenatedWordSingleWordsItem.from_dict(single_words_item_data)

            single_words.append(single_words_item)

        concatenated_vector = cast(list[float], d.pop("concatenatedVector", UNSET))

        concatenated_nearest_neighbors = []
        _concatenated_nearest_neighbors = d.pop("concatenatedNearestNeighbors", UNSET)
        for componentsschemas_c11_y_nearest_neighbors_item_data in _concatenated_nearest_neighbors or []:
            componentsschemas_c11_y_nearest_neighbors_item = C11YNearestNeighborsItem.from_dict(
                componentsschemas_c11_y_nearest_neighbors_item_data
            )

            concatenated_nearest_neighbors.append(componentsschemas_c11_y_nearest_neighbors_item)

        c11y_words_response_concatenated_word = cls(
            concatenated_word=concatenated_word,
            single_words=single_words,
            concatenated_vector=concatenated_vector,
            concatenated_nearest_neighbors=concatenated_nearest_neighbors,
        )

        c11y_words_response_concatenated_word.additional_properties = d
        return c11y_words_response_concatenated_word

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
