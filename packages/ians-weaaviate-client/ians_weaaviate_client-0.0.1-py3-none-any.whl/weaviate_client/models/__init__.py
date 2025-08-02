"""Contains all the data models used in inputs/outputs"""

from .add_permissions_body import AddPermissionsBody
from .additional_properties import AdditionalProperties
from .additional_properties_additional_property import AdditionalPropertiesAdditionalProperty
from .alias import Alias
from .alias_response import AliasResponse
from .aliases_update_body import AliasesUpdateBody
from .assign_role_to_group_body import AssignRoleToGroupBody
from .assign_role_to_user_body import AssignRoleToUserBody
from .async_replication_status import AsyncReplicationStatus
from .backup_config import BackupConfig
from .backup_config_compression_level import BackupConfigCompressionLevel
from .backup_create_request import BackupCreateRequest
from .backup_create_response import BackupCreateResponse
from .backup_create_response_status import BackupCreateResponseStatus
from .backup_create_status_response import BackupCreateStatusResponse
from .backup_create_status_response_status import BackupCreateStatusResponseStatus
from .backup_list_response_item import BackupListResponseItem
from .backup_list_response_item_status import BackupListResponseItemStatus
from .backup_restore_request import BackupRestoreRequest
from .backup_restore_request_node_mapping import BackupRestoreRequestNodeMapping
from .backup_restore_response import BackupRestoreResponse
from .backup_restore_response_status import BackupRestoreResponseStatus
from .backup_restore_status_response import BackupRestoreStatusResponse
from .backup_restore_status_response_status import BackupRestoreStatusResponseStatus
from .batch_delete import BatchDelete
from .batch_delete_match import BatchDeleteMatch
from .batch_delete_response import BatchDeleteResponse
from .batch_delete_response_match import BatchDeleteResponseMatch
from .batch_delete_response_results import BatchDeleteResponseResults
from .batch_delete_response_results_objects_item import BatchDeleteResponseResultsObjectsItem
from .batch_delete_response_results_objects_item_status import BatchDeleteResponseResultsObjectsItemStatus
from .batch_objects_create_body import BatchObjectsCreateBody
from .batch_objects_create_body_fields_item import BatchObjectsCreateBodyFieldsItem
from .batch_reference import BatchReference
from .batch_reference_response import BatchReferenceResponse
from .batch_reference_response_result import BatchReferenceResponseResult
from .batch_reference_response_result_status import BatchReferenceResponseResultStatus
from .batch_stats import BatchStats
from .bm25_config import BM25Config
from .c11y_extension import C11YExtension
from .c11y_nearest_neighbors_item import C11YNearestNeighborsItem
from .c11y_vector_based_question_item import C11YVectorBasedQuestionItem
from .c11y_vector_based_question_item_class_props_item import C11YVectorBasedQuestionItemClassPropsItem
from .c11y_words_response import C11YWordsResponse
from .c11y_words_response_concatenated_word import C11YWordsResponseConcatenatedWord
from .c11y_words_response_concatenated_word_single_words_item import C11YWordsResponseConcatenatedWordSingleWordsItem
from .c11y_words_response_individual_words_item import C11YWordsResponseIndividualWordsItem
from .c11y_words_response_individual_words_item_info import C11YWordsResponseIndividualWordsItemInfo
from .class_ import Class
from .class_module_config import ClassModuleConfig
from .class_sharding_config import ClassShardingConfig
from .class_vector_config import ClassVectorConfig
from .class_vector_index_config import ClassVectorIndexConfig
from .classification import Classification
from .classification_filters import ClassificationFilters
from .classification_meta import ClassificationMeta
from .classification_settings import ClassificationSettings
from .classification_status import ClassificationStatus
from .cluster_statistics_response import ClusterStatisticsResponse
from .create_user_body import CreateUserBody
from .db_user_info import DBUserInfo
from .db_user_info_db_user_type import DBUserInfoDbUserType
from .deactivate_user_body import DeactivateUserBody
from .deprecation import Deprecation
from .distributed_task import DistributedTask
from .distributed_task_payload import DistributedTaskPayload
from .distributed_tasks import DistributedTasks
from .error_response import ErrorResponse
from .error_response_error_item import ErrorResponseErrorItem
from .geo_coordinates import GeoCoordinates
from .get_roles_for_user_user_type import GetRolesForUserUserType
from .get_users_for_role_response_200_item import GetUsersForRoleResponse200Item
from .get_well_known_openid_configuration_response_200 import GetWellKnownOpenidConfigurationResponse200
from .graph_ql_error import GraphQLError
from .graph_ql_error_locations_item import GraphQLErrorLocationsItem
from .graph_ql_query import GraphQLQuery
from .graph_ql_query_variables import GraphQLQueryVariables
from .graph_ql_response import GraphQLResponse
from .graph_ql_response_data import GraphQLResponseData
from .inverted_index_config import InvertedIndexConfig
from .json_object import JsonObject
from .link import Link
from .meta import Meta
from .meta_modules import MetaModules
from .multi_tenancy_config import MultiTenancyConfig
from .nested_property import NestedProperty
from .nested_property_tokenization import NestedPropertyTokenization
from .node_shard_status import NodeShardStatus
from .node_shard_status_compressed import NodeShardStatusCompressed
from .node_shard_status_vector_indexing_status import NodeShardStatusVectorIndexingStatus
from .node_stats import NodeStats
from .node_status import NodeStatus
from .node_status_status import NodeStatusStatus
from .nodes_status_response import NodesStatusResponse
from .object_ import Object
from .objects_get_response import ObjectsGetResponse
from .objects_get_response_result import ObjectsGetResponseResult
from .objects_get_response_result_status import ObjectsGetResponseResultStatus
from .objects_list_response import ObjectsListResponse
from .patch_document_action import PatchDocumentAction
from .patch_document_action_op import PatchDocumentActionOp
from .patch_document_action_value import PatchDocumentActionValue
from .patch_document_object import PatchDocumentObject
from .patch_document_object_op import PatchDocumentObjectOp
from .patch_document_object_value import PatchDocumentObjectValue
from .peer_update import PeerUpdate
from .permission import Permission
from .permission_action import PermissionAction
from .permission_aliases import PermissionAliases
from .permission_backups import PermissionBackups
from .permission_collections import PermissionCollections
from .permission_data import PermissionData
from .permission_nodes import PermissionNodes
from .permission_nodes_verbosity import PermissionNodesVerbosity
from .permission_replicate import PermissionReplicate
from .permission_roles import PermissionRoles
from .permission_roles_scope import PermissionRolesScope
from .permission_tenants import PermissionTenants
from .permission_users import PermissionUsers
from .phone_number import PhoneNumber
from .principal import Principal
from .property_ import Property
from .property_module_config import PropertyModuleConfig
from .property_schema import PropertySchema
from .property_tokenization import PropertyTokenization
from .raft_statistics import RaftStatistics
from .raft_statistics_latest_configuration import RaftStatisticsLatestConfiguration
from .reference_meta_classification import ReferenceMetaClassification
from .remove_permissions_body import RemovePermissionsBody
from .replication_config import ReplicationConfig
from .replication_config_deletion_strategy import ReplicationConfigDeletionStrategy
from .replication_delete_replica_request import ReplicationDeleteReplicaRequest
from .replication_disable_replica_request import ReplicationDisableReplicaRequest
from .replication_replicate_details_replica_response import ReplicationReplicateDetailsReplicaResponse
from .replication_replicate_details_replica_response_type import ReplicationReplicateDetailsReplicaResponseType
from .replication_replicate_details_replica_status import ReplicationReplicateDetailsReplicaStatus
from .replication_replicate_details_replica_status_error import ReplicationReplicateDetailsReplicaStatusError
from .replication_replicate_details_replica_status_state import ReplicationReplicateDetailsReplicaStatusState
from .replication_replicate_force_delete_request import ReplicationReplicateForceDeleteRequest
from .replication_replicate_force_delete_response import ReplicationReplicateForceDeleteResponse
from .replication_replicate_replica_request import ReplicationReplicateReplicaRequest
from .replication_replicate_replica_request_type import ReplicationReplicateReplicaRequestType
from .replication_replicate_replica_response import ReplicationReplicateReplicaResponse
from .replication_shard_replicas import ReplicationShardReplicas
from .replication_sharding_state import ReplicationShardingState
from .replication_sharding_state_response import ReplicationShardingStateResponse
from .restore_config import RestoreConfig
from .restore_config_roles_options import RestoreConfigRolesOptions
from .restore_config_users_options import RestoreConfigUsersOptions
from .revoke_role_from_group_body import RevokeRoleFromGroupBody
from .revoke_role_from_user_body import RevokeRoleFromUserBody
from .role import Role
from .schema import Schema
from .schema_cluster_status import SchemaClusterStatus
from .schema_history import SchemaHistory
from .shard_status import ShardStatus
from .shard_status_get_response import ShardStatusGetResponse
from .single_ref import SingleRef
from .statistics import Statistics
from .statistics_candidates import StatisticsCandidates
from .statistics_leader_address import StatisticsLeaderAddress
from .statistics_leader_id import StatisticsLeaderId
from .statistics_status import StatisticsStatus
from .stopword_config import StopwordConfig
from .tenant import Tenant
from .tenant_activity_status import TenantActivityStatus
from .user_api_key import UserApiKey
from .user_own_info import UserOwnInfo
from .user_type_input import UserTypeInput
from .user_type_output import UserTypeOutput
from .vector import Vector
from .vector_config import VectorConfig
from .vector_config_vector_index_config import VectorConfigVectorIndexConfig
from .vector_config_vectorizer import VectorConfigVectorizer
from .vector_weights import VectorWeights
from .vectors import Vectors
from .weaviate_root_response_200 import WeaviateRootResponse200
from .where_filter import WhereFilter
from .where_filter_geo_range import WhereFilterGeoRange
from .where_filter_geo_range_distance import WhereFilterGeoRangeDistance
from .where_filter_operator import WhereFilterOperator

__all__ = (
    "AdditionalProperties",
    "AdditionalPropertiesAdditionalProperty",
    "AddPermissionsBody",
    "Alias",
    "AliasesUpdateBody",
    "AliasResponse",
    "AssignRoleToGroupBody",
    "AssignRoleToUserBody",
    "AsyncReplicationStatus",
    "BackupConfig",
    "BackupConfigCompressionLevel",
    "BackupCreateRequest",
    "BackupCreateResponse",
    "BackupCreateResponseStatus",
    "BackupCreateStatusResponse",
    "BackupCreateStatusResponseStatus",
    "BackupListResponseItem",
    "BackupListResponseItemStatus",
    "BackupRestoreRequest",
    "BackupRestoreRequestNodeMapping",
    "BackupRestoreResponse",
    "BackupRestoreResponseStatus",
    "BackupRestoreStatusResponse",
    "BackupRestoreStatusResponseStatus",
    "BatchDelete",
    "BatchDeleteMatch",
    "BatchDeleteResponse",
    "BatchDeleteResponseMatch",
    "BatchDeleteResponseResults",
    "BatchDeleteResponseResultsObjectsItem",
    "BatchDeleteResponseResultsObjectsItemStatus",
    "BatchObjectsCreateBody",
    "BatchObjectsCreateBodyFieldsItem",
    "BatchReference",
    "BatchReferenceResponse",
    "BatchReferenceResponseResult",
    "BatchReferenceResponseResultStatus",
    "BatchStats",
    "BM25Config",
    "C11YExtension",
    "C11YNearestNeighborsItem",
    "C11YVectorBasedQuestionItem",
    "C11YVectorBasedQuestionItemClassPropsItem",
    "C11YWordsResponse",
    "C11YWordsResponseConcatenatedWord",
    "C11YWordsResponseConcatenatedWordSingleWordsItem",
    "C11YWordsResponseIndividualWordsItem",
    "C11YWordsResponseIndividualWordsItemInfo",
    "Class",
    "Classification",
    "ClassificationFilters",
    "ClassificationMeta",
    "ClassificationSettings",
    "ClassificationStatus",
    "ClassModuleConfig",
    "ClassShardingConfig",
    "ClassVectorConfig",
    "ClassVectorIndexConfig",
    "ClusterStatisticsResponse",
    "CreateUserBody",
    "DBUserInfo",
    "DBUserInfoDbUserType",
    "DeactivateUserBody",
    "Deprecation",
    "DistributedTask",
    "DistributedTaskPayload",
    "DistributedTasks",
    "ErrorResponse",
    "ErrorResponseErrorItem",
    "GeoCoordinates",
    "GetRolesForUserUserType",
    "GetUsersForRoleResponse200Item",
    "GetWellKnownOpenidConfigurationResponse200",
    "GraphQLError",
    "GraphQLErrorLocationsItem",
    "GraphQLQuery",
    "GraphQLQueryVariables",
    "GraphQLResponse",
    "GraphQLResponseData",
    "InvertedIndexConfig",
    "JsonObject",
    "Link",
    "Meta",
    "MetaModules",
    "MultiTenancyConfig",
    "NestedProperty",
    "NestedPropertyTokenization",
    "NodeShardStatus",
    "NodeShardStatusCompressed",
    "NodeShardStatusVectorIndexingStatus",
    "NodesStatusResponse",
    "NodeStats",
    "NodeStatus",
    "NodeStatusStatus",
    "Object",
    "ObjectsGetResponse",
    "ObjectsGetResponseResult",
    "ObjectsGetResponseResultStatus",
    "ObjectsListResponse",
    "PatchDocumentAction",
    "PatchDocumentActionOp",
    "PatchDocumentActionValue",
    "PatchDocumentObject",
    "PatchDocumentObjectOp",
    "PatchDocumentObjectValue",
    "PeerUpdate",
    "Permission",
    "PermissionAction",
    "PermissionAliases",
    "PermissionBackups",
    "PermissionCollections",
    "PermissionData",
    "PermissionNodes",
    "PermissionNodesVerbosity",
    "PermissionReplicate",
    "PermissionRoles",
    "PermissionRolesScope",
    "PermissionTenants",
    "PermissionUsers",
    "PhoneNumber",
    "Principal",
    "Property",
    "PropertyModuleConfig",
    "PropertySchema",
    "PropertyTokenization",
    "RaftStatistics",
    "RaftStatisticsLatestConfiguration",
    "ReferenceMetaClassification",
    "RemovePermissionsBody",
    "ReplicationConfig",
    "ReplicationConfigDeletionStrategy",
    "ReplicationDeleteReplicaRequest",
    "ReplicationDisableReplicaRequest",
    "ReplicationReplicateDetailsReplicaResponse",
    "ReplicationReplicateDetailsReplicaResponseType",
    "ReplicationReplicateDetailsReplicaStatus",
    "ReplicationReplicateDetailsReplicaStatusError",
    "ReplicationReplicateDetailsReplicaStatusState",
    "ReplicationReplicateForceDeleteRequest",
    "ReplicationReplicateForceDeleteResponse",
    "ReplicationReplicateReplicaRequest",
    "ReplicationReplicateReplicaRequestType",
    "ReplicationReplicateReplicaResponse",
    "ReplicationShardingState",
    "ReplicationShardingStateResponse",
    "ReplicationShardReplicas",
    "RestoreConfig",
    "RestoreConfigRolesOptions",
    "RestoreConfigUsersOptions",
    "RevokeRoleFromGroupBody",
    "RevokeRoleFromUserBody",
    "Role",
    "Schema",
    "SchemaClusterStatus",
    "SchemaHistory",
    "ShardStatus",
    "ShardStatusGetResponse",
    "SingleRef",
    "Statistics",
    "StatisticsCandidates",
    "StatisticsLeaderAddress",
    "StatisticsLeaderId",
    "StatisticsStatus",
    "StopwordConfig",
    "Tenant",
    "TenantActivityStatus",
    "UserApiKey",
    "UserOwnInfo",
    "UserTypeInput",
    "UserTypeOutput",
    "Vector",
    "VectorConfig",
    "VectorConfigVectorIndexConfig",
    "VectorConfigVectorizer",
    "Vectors",
    "VectorWeights",
    "WeaviateRootResponse200",
    "WhereFilter",
    "WhereFilterGeoRange",
    "WhereFilterGeoRangeDistance",
    "WhereFilterOperator",
)
