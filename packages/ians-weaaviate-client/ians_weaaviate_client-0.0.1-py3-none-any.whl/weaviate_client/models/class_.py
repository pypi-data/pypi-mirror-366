from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.class_module_config import ClassModuleConfig
    from ..models.class_sharding_config import ClassShardingConfig
    from ..models.class_vector_config import ClassVectorConfig
    from ..models.class_vector_index_config import ClassVectorIndexConfig
    from ..models.inverted_index_config import InvertedIndexConfig
    from ..models.multi_tenancy_config import MultiTenancyConfig
    from ..models.property_ import Property
    from ..models.replication_config import ReplicationConfig


T = TypeVar("T", bound="Class")


@_attrs_define
class Class:
    """
    Attributes:
        class_ (Union[Unset, str]): Name of the class (a.k.a. 'collection') (required). Multiple words should be
            concatenated in CamelCase, e.g. `ArticleAuthor`.
        vector_config (Union[Unset, ClassVectorConfig]): Configure named vectors. Either use this field or `vectorizer`,
            `vectorIndexType`, and `vectorIndexConfig` fields. Available from `v1.24.0`.
        vector_index_type (Union[Unset, str]): Name of the vector index to use, eg. (HNSW)
        vector_index_config (Union[Unset, ClassVectorIndexConfig]): Vector-index config, that is specific to the type of
            index selected in vectorIndexType
        sharding_config (Union[Unset, ClassShardingConfig]): Manage how the index should be sharded and distributed in
            the cluster
        replication_config (Union[Unset, ReplicationConfig]): Configure how replication is executed in a cluster
        inverted_index_config (Union[Unset, InvertedIndexConfig]): Configure the inverted index built into Weaviate
            (default: 60).
        multi_tenancy_config (Union[Unset, MultiTenancyConfig]): Configuration related to multi-tenancy within a class
        vectorizer (Union[Unset, str]): Specify how the vectors for this class should be determined. The options are
            either 'none' - this means you have to import a vector with each object yourself - or the name of a module that
            provides vectorization capabilities, such as 'text2vec-contextionary'. If left empty, it will use the globally
            configured default which can itself either be 'none' or a specific module.
        module_config (Union[Unset, ClassModuleConfig]): Configuration specific to modules in a collection context.
        description (Union[Unset, str]): Description of the collection for metadata purposes.
        properties (Union[Unset, list['Property']]): Define properties of the collection.
    """

    class_: Union[Unset, str] = UNSET
    vector_config: Union[Unset, "ClassVectorConfig"] = UNSET
    vector_index_type: Union[Unset, str] = UNSET
    vector_index_config: Union[Unset, "ClassVectorIndexConfig"] = UNSET
    sharding_config: Union[Unset, "ClassShardingConfig"] = UNSET
    replication_config: Union[Unset, "ReplicationConfig"] = UNSET
    inverted_index_config: Union[Unset, "InvertedIndexConfig"] = UNSET
    multi_tenancy_config: Union[Unset, "MultiTenancyConfig"] = UNSET
    vectorizer: Union[Unset, str] = UNSET
    module_config: Union[Unset, "ClassModuleConfig"] = UNSET
    description: Union[Unset, str] = UNSET
    properties: Union[Unset, list["Property"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_ = self.class_

        vector_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vector_config, Unset):
            vector_config = self.vector_config.to_dict()

        vector_index_type = self.vector_index_type

        vector_index_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vector_index_config, Unset):
            vector_index_config = self.vector_index_config.to_dict()

        sharding_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sharding_config, Unset):
            sharding_config = self.sharding_config.to_dict()

        replication_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.replication_config, Unset):
            replication_config = self.replication_config.to_dict()

        inverted_index_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.inverted_index_config, Unset):
            inverted_index_config = self.inverted_index_config.to_dict()

        multi_tenancy_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.multi_tenancy_config, Unset):
            multi_tenancy_config = self.multi_tenancy_config.to_dict()

        vectorizer = self.vectorizer

        module_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.module_config, Unset):
            module_config = self.module_config.to_dict()

        description = self.description

        properties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_ is not UNSET:
            field_dict["class"] = class_
        if vector_config is not UNSET:
            field_dict["vectorConfig"] = vector_config
        if vector_index_type is not UNSET:
            field_dict["vectorIndexType"] = vector_index_type
        if vector_index_config is not UNSET:
            field_dict["vectorIndexConfig"] = vector_index_config
        if sharding_config is not UNSET:
            field_dict["shardingConfig"] = sharding_config
        if replication_config is not UNSET:
            field_dict["replicationConfig"] = replication_config
        if inverted_index_config is not UNSET:
            field_dict["invertedIndexConfig"] = inverted_index_config
        if multi_tenancy_config is not UNSET:
            field_dict["multiTenancyConfig"] = multi_tenancy_config
        if vectorizer is not UNSET:
            field_dict["vectorizer"] = vectorizer
        if module_config is not UNSET:
            field_dict["moduleConfig"] = module_config
        if description is not UNSET:
            field_dict["description"] = description
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.class_module_config import ClassModuleConfig
        from ..models.class_sharding_config import ClassShardingConfig
        from ..models.class_vector_config import ClassVectorConfig
        from ..models.class_vector_index_config import ClassVectorIndexConfig
        from ..models.inverted_index_config import InvertedIndexConfig
        from ..models.multi_tenancy_config import MultiTenancyConfig
        from ..models.property_ import Property
        from ..models.replication_config import ReplicationConfig

        d = dict(src_dict)
        class_ = d.pop("class", UNSET)

        _vector_config = d.pop("vectorConfig", UNSET)
        vector_config: Union[Unset, ClassVectorConfig]
        if isinstance(_vector_config, Unset):
            vector_config = UNSET
        else:
            vector_config = ClassVectorConfig.from_dict(_vector_config)

        vector_index_type = d.pop("vectorIndexType", UNSET)

        _vector_index_config = d.pop("vectorIndexConfig", UNSET)
        vector_index_config: Union[Unset, ClassVectorIndexConfig]
        if isinstance(_vector_index_config, Unset):
            vector_index_config = UNSET
        else:
            vector_index_config = ClassVectorIndexConfig.from_dict(_vector_index_config)

        _sharding_config = d.pop("shardingConfig", UNSET)
        sharding_config: Union[Unset, ClassShardingConfig]
        if isinstance(_sharding_config, Unset):
            sharding_config = UNSET
        else:
            sharding_config = ClassShardingConfig.from_dict(_sharding_config)

        _replication_config = d.pop("replicationConfig", UNSET)
        replication_config: Union[Unset, ReplicationConfig]
        if isinstance(_replication_config, Unset):
            replication_config = UNSET
        else:
            replication_config = ReplicationConfig.from_dict(_replication_config)

        _inverted_index_config = d.pop("invertedIndexConfig", UNSET)
        inverted_index_config: Union[Unset, InvertedIndexConfig]
        if isinstance(_inverted_index_config, Unset):
            inverted_index_config = UNSET
        else:
            inverted_index_config = InvertedIndexConfig.from_dict(_inverted_index_config)

        _multi_tenancy_config = d.pop("multiTenancyConfig", UNSET)
        multi_tenancy_config: Union[Unset, MultiTenancyConfig]
        if isinstance(_multi_tenancy_config, Unset):
            multi_tenancy_config = UNSET
        else:
            multi_tenancy_config = MultiTenancyConfig.from_dict(_multi_tenancy_config)

        vectorizer = d.pop("vectorizer", UNSET)

        _module_config = d.pop("moduleConfig", UNSET)
        module_config: Union[Unset, ClassModuleConfig]
        if isinstance(_module_config, Unset):
            module_config = UNSET
        else:
            module_config = ClassModuleConfig.from_dict(_module_config)

        description = d.pop("description", UNSET)

        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in _properties or []:
            properties_item = Property.from_dict(properties_item_data)

            properties.append(properties_item)

        class_ = cls(
            class_=class_,
            vector_config=vector_config,
            vector_index_type=vector_index_type,
            vector_index_config=vector_index_config,
            sharding_config=sharding_config,
            replication_config=replication_config,
            inverted_index_config=inverted_index_config,
            multi_tenancy_config=multi_tenancy_config,
            vectorizer=vectorizer,
            module_config=module_config,
            description=description,
            properties=properties,
        )

        class_.additional_properties = d
        return class_

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
