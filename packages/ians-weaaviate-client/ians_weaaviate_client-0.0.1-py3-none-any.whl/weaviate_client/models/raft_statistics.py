from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.raft_statistics_latest_configuration import RaftStatisticsLatestConfiguration


T = TypeVar("T", bound="RaftStatistics")


@_attrs_define
class RaftStatistics:
    """The definition of Raft statistics.

    Attributes:
        applied_index (Union[Unset, str]):
        commit_index (Union[Unset, str]):
        fsm_pending (Union[Unset, str]):
        last_contact (Union[Unset, str]):
        last_log_index (Union[Unset, str]):
        last_log_term (Union[Unset, str]):
        last_snapshot_index (Union[Unset, str]):
        last_snapshot_term (Union[Unset, str]):
        latest_configuration (Union[Unset, RaftStatisticsLatestConfiguration]): Weaviate Raft nodes.
        latest_configuration_index (Union[Unset, str]):
        num_peers (Union[Unset, str]):
        protocol_version (Union[Unset, str]):
        protocol_version_max (Union[Unset, str]):
        protocol_version_min (Union[Unset, str]):
        snapshot_version_max (Union[Unset, str]):
        snapshot_version_min (Union[Unset, str]):
        state (Union[Unset, str]):
        term (Union[Unset, str]):
    """

    applied_index: Union[Unset, str] = UNSET
    commit_index: Union[Unset, str] = UNSET
    fsm_pending: Union[Unset, str] = UNSET
    last_contact: Union[Unset, str] = UNSET
    last_log_index: Union[Unset, str] = UNSET
    last_log_term: Union[Unset, str] = UNSET
    last_snapshot_index: Union[Unset, str] = UNSET
    last_snapshot_term: Union[Unset, str] = UNSET
    latest_configuration: Union[Unset, "RaftStatisticsLatestConfiguration"] = UNSET
    latest_configuration_index: Union[Unset, str] = UNSET
    num_peers: Union[Unset, str] = UNSET
    protocol_version: Union[Unset, str] = UNSET
    protocol_version_max: Union[Unset, str] = UNSET
    protocol_version_min: Union[Unset, str] = UNSET
    snapshot_version_max: Union[Unset, str] = UNSET
    snapshot_version_min: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    term: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        applied_index = self.applied_index

        commit_index = self.commit_index

        fsm_pending = self.fsm_pending

        last_contact = self.last_contact

        last_log_index = self.last_log_index

        last_log_term = self.last_log_term

        last_snapshot_index = self.last_snapshot_index

        last_snapshot_term = self.last_snapshot_term

        latest_configuration: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_configuration, Unset):
            latest_configuration = self.latest_configuration.to_dict()

        latest_configuration_index = self.latest_configuration_index

        num_peers = self.num_peers

        protocol_version = self.protocol_version

        protocol_version_max = self.protocol_version_max

        protocol_version_min = self.protocol_version_min

        snapshot_version_max = self.snapshot_version_max

        snapshot_version_min = self.snapshot_version_min

        state = self.state

        term = self.term

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if applied_index is not UNSET:
            field_dict["appliedIndex"] = applied_index
        if commit_index is not UNSET:
            field_dict["commitIndex"] = commit_index
        if fsm_pending is not UNSET:
            field_dict["fsmPending"] = fsm_pending
        if last_contact is not UNSET:
            field_dict["lastContact"] = last_contact
        if last_log_index is not UNSET:
            field_dict["lastLogIndex"] = last_log_index
        if last_log_term is not UNSET:
            field_dict["lastLogTerm"] = last_log_term
        if last_snapshot_index is not UNSET:
            field_dict["lastSnapshotIndex"] = last_snapshot_index
        if last_snapshot_term is not UNSET:
            field_dict["lastSnapshotTerm"] = last_snapshot_term
        if latest_configuration is not UNSET:
            field_dict["latestConfiguration"] = latest_configuration
        if latest_configuration_index is not UNSET:
            field_dict["latestConfigurationIndex"] = latest_configuration_index
        if num_peers is not UNSET:
            field_dict["numPeers"] = num_peers
        if protocol_version is not UNSET:
            field_dict["protocolVersion"] = protocol_version
        if protocol_version_max is not UNSET:
            field_dict["protocolVersionMax"] = protocol_version_max
        if protocol_version_min is not UNSET:
            field_dict["protocolVersionMin"] = protocol_version_min
        if snapshot_version_max is not UNSET:
            field_dict["snapshotVersionMax"] = snapshot_version_max
        if snapshot_version_min is not UNSET:
            field_dict["snapshotVersionMin"] = snapshot_version_min
        if state is not UNSET:
            field_dict["state"] = state
        if term is not UNSET:
            field_dict["term"] = term

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.raft_statistics_latest_configuration import RaftStatisticsLatestConfiguration

        d = dict(src_dict)
        applied_index = d.pop("appliedIndex", UNSET)

        commit_index = d.pop("commitIndex", UNSET)

        fsm_pending = d.pop("fsmPending", UNSET)

        last_contact = d.pop("lastContact", UNSET)

        last_log_index = d.pop("lastLogIndex", UNSET)

        last_log_term = d.pop("lastLogTerm", UNSET)

        last_snapshot_index = d.pop("lastSnapshotIndex", UNSET)

        last_snapshot_term = d.pop("lastSnapshotTerm", UNSET)

        _latest_configuration = d.pop("latestConfiguration", UNSET)
        latest_configuration: Union[Unset, RaftStatisticsLatestConfiguration]
        if isinstance(_latest_configuration, Unset):
            latest_configuration = UNSET
        else:
            latest_configuration = RaftStatisticsLatestConfiguration.from_dict(_latest_configuration)

        latest_configuration_index = d.pop("latestConfigurationIndex", UNSET)

        num_peers = d.pop("numPeers", UNSET)

        protocol_version = d.pop("protocolVersion", UNSET)

        protocol_version_max = d.pop("protocolVersionMax", UNSET)

        protocol_version_min = d.pop("protocolVersionMin", UNSET)

        snapshot_version_max = d.pop("snapshotVersionMax", UNSET)

        snapshot_version_min = d.pop("snapshotVersionMin", UNSET)

        state = d.pop("state", UNSET)

        term = d.pop("term", UNSET)

        raft_statistics = cls(
            applied_index=applied_index,
            commit_index=commit_index,
            fsm_pending=fsm_pending,
            last_contact=last_contact,
            last_log_index=last_log_index,
            last_log_term=last_log_term,
            last_snapshot_index=last_snapshot_index,
            last_snapshot_term=last_snapshot_term,
            latest_configuration=latest_configuration,
            latest_configuration_index=latest_configuration_index,
            num_peers=num_peers,
            protocol_version=protocol_version,
            protocol_version_max=protocol_version_max,
            protocol_version_min=protocol_version_min,
            snapshot_version_max=snapshot_version_max,
            snapshot_version_min=snapshot_version_min,
            state=state,
            term=term,
        )

        raft_statistics.additional_properties = d
        return raft_statistics

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
