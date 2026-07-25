from enum import Enum


class Permission(str, Enum):
    STORE_SETTINGS_VIEW = "store_settings.view"
    STORE_SETTINGS_EDIT = "store_settings.edit"
    STAFF_VIEW = "staff.view"
    STAFF_MANAGE = "staff.manage"
    PRODUCTS_VIEW = "products.view"
    PRODUCTS_EDIT = "products.edit"
    ORDERS_VIEW = "orders.view"
    ORDERS_MANAGE = "orders.manage"
    BILLING_VIEW = "billing.view"
    BILLING_MANAGE = "billing.manage"


# Roles are just named bundles of permissions — add/adjust a role by editing
# its permission set here, no schema or endpoint changes needed.
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "owner": set(Permission),
    "manager": {
        Permission.STORE_SETTINGS_VIEW,
        Permission.STORE_SETTINGS_EDIT,
        Permission.STAFF_VIEW,
        Permission.PRODUCTS_VIEW,
        Permission.PRODUCTS_EDIT,
        Permission.ORDERS_VIEW,
        Permission.ORDERS_MANAGE,
        Permission.BILLING_VIEW,
    },
    "staff": {
        Permission.PRODUCTS_VIEW,
        Permission.PRODUCTS_EDIT,
        Permission.ORDERS_VIEW,
        Permission.ORDERS_MANAGE,
    },
    "support": {
        Permission.ORDERS_VIEW,
        Permission.ORDERS_MANAGE,
    },
}

# Roles assignable to staff via the API — "owner" is set only at store creation time.
ASSIGNABLE_ROLES = frozenset(ROLE_PERMISSIONS.keys() - {"owner"})
