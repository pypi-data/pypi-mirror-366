from enum import Enum


class PermissionAction(str, Enum):
    ASSIGN_AND_REVOKE_USERS = "assign_and_revoke_users"
    CREATE_ALIASES = "create_aliases"
    CREATE_COLLECTIONS = "create_collections"
    CREATE_DATA = "create_data"
    CREATE_REPLICATE = "create_replicate"
    CREATE_ROLES = "create_roles"
    CREATE_TENANTS = "create_tenants"
    CREATE_USERS = "create_users"
    DELETE_ALIASES = "delete_aliases"
    DELETE_COLLECTIONS = "delete_collections"
    DELETE_DATA = "delete_data"
    DELETE_REPLICATE = "delete_replicate"
    DELETE_ROLES = "delete_roles"
    DELETE_TENANTS = "delete_tenants"
    DELETE_USERS = "delete_users"
    MANAGE_BACKUPS = "manage_backups"
    READ_ALIASES = "read_aliases"
    READ_CLUSTER = "read_cluster"
    READ_COLLECTIONS = "read_collections"
    READ_DATA = "read_data"
    READ_NODES = "read_nodes"
    READ_REPLICATE = "read_replicate"
    READ_ROLES = "read_roles"
    READ_TENANTS = "read_tenants"
    READ_USERS = "read_users"
    UPDATE_ALIASES = "update_aliases"
    UPDATE_COLLECTIONS = "update_collections"
    UPDATE_DATA = "update_data"
    UPDATE_REPLICATE = "update_replicate"
    UPDATE_ROLES = "update_roles"
    UPDATE_TENANTS = "update_tenants"
    UPDATE_USERS = "update_users"

    def __str__(self) -> str:
        return str(self.value)
