from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.statistics_status import StatisticsStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.raft_statistics import RaftStatistics
    from ..models.statistics_candidates import StatisticsCandidates
    from ..models.statistics_leader_address import StatisticsLeaderAddress
    from ..models.statistics_leader_id import StatisticsLeaderId


T = TypeVar("T", bound="Statistics")


@_attrs_define
class Statistics:
    """The definition of node statistics.

    Attributes:
        name (Union[Unset, str]): The name of the node.
        status (Union[Unset, StatisticsStatus]): Node's status. Default: StatisticsStatus.HEALTHY.
        bootstrapped (Union[Unset, bool]):
        db_loaded (Union[Unset, bool]):
        initial_last_applied_index (Union[Unset, float]):
        last_applied_index (Union[Unset, float]):
        is_voter (Union[Unset, bool]):
        leader_id (Union[Unset, StatisticsLeaderId]):
        leader_address (Union[Unset, StatisticsLeaderAddress]):
        open_ (Union[Unset, bool]):
        ready (Union[Unset, bool]):
        candidates (Union[Unset, StatisticsCandidates]):
        raft (Union[Unset, RaftStatistics]): The definition of Raft statistics.
    """

    name: Union[Unset, str] = UNSET
    status: Union[Unset, StatisticsStatus] = StatisticsStatus.HEALTHY
    bootstrapped: Union[Unset, bool] = UNSET
    db_loaded: Union[Unset, bool] = UNSET
    initial_last_applied_index: Union[Unset, float] = UNSET
    last_applied_index: Union[Unset, float] = UNSET
    is_voter: Union[Unset, bool] = UNSET
    leader_id: Union[Unset, "StatisticsLeaderId"] = UNSET
    leader_address: Union[Unset, "StatisticsLeaderAddress"] = UNSET
    open_: Union[Unset, bool] = UNSET
    ready: Union[Unset, bool] = UNSET
    candidates: Union[Unset, "StatisticsCandidates"] = UNSET
    raft: Union[Unset, "RaftStatistics"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        bootstrapped = self.bootstrapped

        db_loaded = self.db_loaded

        initial_last_applied_index = self.initial_last_applied_index

        last_applied_index = self.last_applied_index

        is_voter = self.is_voter

        leader_id: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.leader_id, Unset):
            leader_id = self.leader_id.to_dict()

        leader_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.leader_address, Unset):
            leader_address = self.leader_address.to_dict()

        open_ = self.open_

        ready = self.ready

        candidates: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.candidates, Unset):
            candidates = self.candidates.to_dict()

        raft: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.raft, Unset):
            raft = self.raft.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if bootstrapped is not UNSET:
            field_dict["bootstrapped"] = bootstrapped
        if db_loaded is not UNSET:
            field_dict["dbLoaded"] = db_loaded
        if initial_last_applied_index is not UNSET:
            field_dict["initialLastAppliedIndex"] = initial_last_applied_index
        if last_applied_index is not UNSET:
            field_dict["lastAppliedIndex"] = last_applied_index
        if is_voter is not UNSET:
            field_dict["isVoter"] = is_voter
        if leader_id is not UNSET:
            field_dict["leaderId"] = leader_id
        if leader_address is not UNSET:
            field_dict["leaderAddress"] = leader_address
        if open_ is not UNSET:
            field_dict["open"] = open_
        if ready is not UNSET:
            field_dict["ready"] = ready
        if candidates is not UNSET:
            field_dict["candidates"] = candidates
        if raft is not UNSET:
            field_dict["raft"] = raft

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.raft_statistics import RaftStatistics
        from ..models.statistics_candidates import StatisticsCandidates
        from ..models.statistics_leader_address import StatisticsLeaderAddress
        from ..models.statistics_leader_id import StatisticsLeaderId

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, StatisticsStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = StatisticsStatus(_status)

        bootstrapped = d.pop("bootstrapped", UNSET)

        db_loaded = d.pop("dbLoaded", UNSET)

        initial_last_applied_index = d.pop("initialLastAppliedIndex", UNSET)

        last_applied_index = d.pop("lastAppliedIndex", UNSET)

        is_voter = d.pop("isVoter", UNSET)

        _leader_id = d.pop("leaderId", UNSET)
        leader_id: Union[Unset, StatisticsLeaderId]
        if isinstance(_leader_id, Unset):
            leader_id = UNSET
        else:
            leader_id = StatisticsLeaderId.from_dict(_leader_id)

        _leader_address = d.pop("leaderAddress", UNSET)
        leader_address: Union[Unset, StatisticsLeaderAddress]
        if isinstance(_leader_address, Unset):
            leader_address = UNSET
        else:
            leader_address = StatisticsLeaderAddress.from_dict(_leader_address)

        open_ = d.pop("open", UNSET)

        ready = d.pop("ready", UNSET)

        _candidates = d.pop("candidates", UNSET)
        candidates: Union[Unset, StatisticsCandidates]
        if isinstance(_candidates, Unset):
            candidates = UNSET
        else:
            candidates = StatisticsCandidates.from_dict(_candidates)

        _raft = d.pop("raft", UNSET)
        raft: Union[Unset, RaftStatistics]
        if isinstance(_raft, Unset):
            raft = UNSET
        else:
            raft = RaftStatistics.from_dict(_raft)

        statistics = cls(
            name=name,
            status=status,
            bootstrapped=bootstrapped,
            db_loaded=db_loaded,
            initial_last_applied_index=initial_last_applied_index,
            last_applied_index=last_applied_index,
            is_voter=is_voter,
            leader_id=leader_id,
            leader_address=leader_address,
            open_=open_,
            ready=ready,
            candidates=candidates,
            raft=raft,
        )

        statistics.additional_properties = d
        return statistics

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
