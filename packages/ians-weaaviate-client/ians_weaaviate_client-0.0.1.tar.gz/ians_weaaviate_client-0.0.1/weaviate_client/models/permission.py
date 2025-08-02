from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.permission_action import PermissionAction
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.permission_aliases import PermissionAliases
    from ..models.permission_backups import PermissionBackups
    from ..models.permission_collections import PermissionCollections
    from ..models.permission_data import PermissionData
    from ..models.permission_nodes import PermissionNodes
    from ..models.permission_replicate import PermissionReplicate
    from ..models.permission_roles import PermissionRoles
    from ..models.permission_tenants import PermissionTenants
    from ..models.permission_users import PermissionUsers


T = TypeVar("T", bound="Permission")


@_attrs_define
class Permission:
    """permissions attached to a role.

    Attributes:
        action (PermissionAction): allowed actions in weaviate.
        backups (Union[Unset, PermissionBackups]): resources applicable for backup actions
        data (Union[Unset, PermissionData]): resources applicable for data actions
        nodes (Union[Unset, PermissionNodes]): resources applicable for cluster actions
        users (Union[Unset, PermissionUsers]): resources applicable for user actions
        tenants (Union[Unset, PermissionTenants]): resources applicable for tenant actions
        roles (Union[Unset, PermissionRoles]): resources applicable for role actions
        collections (Union[Unset, PermissionCollections]): resources applicable for collection and/or tenant actions
        replicate (Union[Unset, PermissionReplicate]): resources applicable for replicate actions
        aliases (Union[Unset, PermissionAliases]): Resource definition for alias-related actions and permissions. Used
            to specify which aliases and collections can be accessed or modified.
    """

    action: PermissionAction
    backups: Union[Unset, "PermissionBackups"] = UNSET
    data: Union[Unset, "PermissionData"] = UNSET
    nodes: Union[Unset, "PermissionNodes"] = UNSET
    users: Union[Unset, "PermissionUsers"] = UNSET
    tenants: Union[Unset, "PermissionTenants"] = UNSET
    roles: Union[Unset, "PermissionRoles"] = UNSET
    collections: Union[Unset, "PermissionCollections"] = UNSET
    replicate: Union[Unset, "PermissionReplicate"] = UNSET
    aliases: Union[Unset, "PermissionAliases"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action.value

        backups: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.backups, Unset):
            backups = self.backups.to_dict()

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        nodes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.nodes, Unset):
            nodes = self.nodes.to_dict()

        users: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.users, Unset):
            users = self.users.to_dict()

        tenants: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tenants, Unset):
            tenants = self.tenants.to_dict()

        roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles.to_dict()

        collections: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.collections, Unset):
            collections = self.collections.to_dict()

        replicate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.replicate, Unset):
            replicate = self.replicate.to_dict()

        aliases: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = self.aliases.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
            }
        )
        if backups is not UNSET:
            field_dict["backups"] = backups
        if data is not UNSET:
            field_dict["data"] = data
        if nodes is not UNSET:
            field_dict["nodes"] = nodes
        if users is not UNSET:
            field_dict["users"] = users
        if tenants is not UNSET:
            field_dict["tenants"] = tenants
        if roles is not UNSET:
            field_dict["roles"] = roles
        if collections is not UNSET:
            field_dict["collections"] = collections
        if replicate is not UNSET:
            field_dict["replicate"] = replicate
        if aliases is not UNSET:
            field_dict["aliases"] = aliases

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission_aliases import PermissionAliases
        from ..models.permission_backups import PermissionBackups
        from ..models.permission_collections import PermissionCollections
        from ..models.permission_data import PermissionData
        from ..models.permission_nodes import PermissionNodes
        from ..models.permission_replicate import PermissionReplicate
        from ..models.permission_roles import PermissionRoles
        from ..models.permission_tenants import PermissionTenants
        from ..models.permission_users import PermissionUsers

        d = dict(src_dict)
        action = PermissionAction(d.pop("action"))

        _backups = d.pop("backups", UNSET)
        backups: Union[Unset, PermissionBackups]
        if isinstance(_backups, Unset):
            backups = UNSET
        else:
            backups = PermissionBackups.from_dict(_backups)

        _data = d.pop("data", UNSET)
        data: Union[Unset, PermissionData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PermissionData.from_dict(_data)

        _nodes = d.pop("nodes", UNSET)
        nodes: Union[Unset, PermissionNodes]
        if isinstance(_nodes, Unset):
            nodes = UNSET
        else:
            nodes = PermissionNodes.from_dict(_nodes)

        _users = d.pop("users", UNSET)
        users: Union[Unset, PermissionUsers]
        if isinstance(_users, Unset):
            users = UNSET
        else:
            users = PermissionUsers.from_dict(_users)

        _tenants = d.pop("tenants", UNSET)
        tenants: Union[Unset, PermissionTenants]
        if isinstance(_tenants, Unset):
            tenants = UNSET
        else:
            tenants = PermissionTenants.from_dict(_tenants)

        _roles = d.pop("roles", UNSET)
        roles: Union[Unset, PermissionRoles]
        if isinstance(_roles, Unset):
            roles = UNSET
        else:
            roles = PermissionRoles.from_dict(_roles)

        _collections = d.pop("collections", UNSET)
        collections: Union[Unset, PermissionCollections]
        if isinstance(_collections, Unset):
            collections = UNSET
        else:
            collections = PermissionCollections.from_dict(_collections)

        _replicate = d.pop("replicate", UNSET)
        replicate: Union[Unset, PermissionReplicate]
        if isinstance(_replicate, Unset):
            replicate = UNSET
        else:
            replicate = PermissionReplicate.from_dict(_replicate)

        _aliases = d.pop("aliases", UNSET)
        aliases: Union[Unset, PermissionAliases]
        if isinstance(_aliases, Unset):
            aliases = UNSET
        else:
            aliases = PermissionAliases.from_dict(_aliases)

        permission = cls(
            action=action,
            backups=backups,
            data=data,
            nodes=nodes,
            users=users,
            tenants=tenants,
            roles=roles,
            collections=collections,
            replicate=replicate,
            aliases=aliases,
        )

        permission.additional_properties = d
        return permission

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
