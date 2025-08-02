from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bm25_config import BM25Config
    from ..models.stopword_config import StopwordConfig


T = TypeVar("T", bound="InvertedIndexConfig")


@_attrs_define
class InvertedIndexConfig:
    """Configure the inverted index built into Weaviate (default: 60).

    Attributes:
        cleanup_interval_seconds (Union[Unset, float]): Asynchronous index clean up happens every n seconds
        bm25 (Union[Unset, BM25Config]): tuning parameters for the BM25 algorithm
        stopwords (Union[Unset, StopwordConfig]): fine-grained control over stopword list usage
        index_timestamps (Union[Unset, bool]): Index each object by its internal timestamps (default: 'false').
        index_null_state (Union[Unset, bool]): Index each object with the null state (default: 'false').
        index_property_length (Union[Unset, bool]): Index length of properties (default: 'false').
        using_block_max_wand (Union[Unset, bool]): Using BlockMax WAND for query execution (default: 'false', will be
            'true' for new collections created after 1.30).
    """

    cleanup_interval_seconds: Union[Unset, float] = UNSET
    bm25: Union[Unset, "BM25Config"] = UNSET
    stopwords: Union[Unset, "StopwordConfig"] = UNSET
    index_timestamps: Union[Unset, bool] = UNSET
    index_null_state: Union[Unset, bool] = UNSET
    index_property_length: Union[Unset, bool] = UNSET
    using_block_max_wand: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cleanup_interval_seconds = self.cleanup_interval_seconds

        bm25: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.bm25, Unset):
            bm25 = self.bm25.to_dict()

        stopwords: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.stopwords, Unset):
            stopwords = self.stopwords.to_dict()

        index_timestamps = self.index_timestamps

        index_null_state = self.index_null_state

        index_property_length = self.index_property_length

        using_block_max_wand = self.using_block_max_wand

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cleanup_interval_seconds is not UNSET:
            field_dict["cleanupIntervalSeconds"] = cleanup_interval_seconds
        if bm25 is not UNSET:
            field_dict["bm25"] = bm25
        if stopwords is not UNSET:
            field_dict["stopwords"] = stopwords
        if index_timestamps is not UNSET:
            field_dict["indexTimestamps"] = index_timestamps
        if index_null_state is not UNSET:
            field_dict["indexNullState"] = index_null_state
        if index_property_length is not UNSET:
            field_dict["indexPropertyLength"] = index_property_length
        if using_block_max_wand is not UNSET:
            field_dict["usingBlockMaxWAND"] = using_block_max_wand

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bm25_config import BM25Config
        from ..models.stopword_config import StopwordConfig

        d = dict(src_dict)
        cleanup_interval_seconds = d.pop("cleanupIntervalSeconds", UNSET)

        _bm25 = d.pop("bm25", UNSET)
        bm25: Union[Unset, BM25Config]
        if isinstance(_bm25, Unset):
            bm25 = UNSET
        else:
            bm25 = BM25Config.from_dict(_bm25)

        _stopwords = d.pop("stopwords", UNSET)
        stopwords: Union[Unset, StopwordConfig]
        if isinstance(_stopwords, Unset):
            stopwords = UNSET
        else:
            stopwords = StopwordConfig.from_dict(_stopwords)

        index_timestamps = d.pop("indexTimestamps", UNSET)

        index_null_state = d.pop("indexNullState", UNSET)

        index_property_length = d.pop("indexPropertyLength", UNSET)

        using_block_max_wand = d.pop("usingBlockMaxWAND", UNSET)

        inverted_index_config = cls(
            cleanup_interval_seconds=cleanup_interval_seconds,
            bm25=bm25,
            stopwords=stopwords,
            index_timestamps=index_timestamps,
            index_null_state=index_null_state,
            index_property_length=index_property_length,
            using_block_max_wand=using_block_max_wand,
        )

        inverted_index_config.additional_properties = d
        return inverted_index_config

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
