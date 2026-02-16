# LDAP configuration - loaded when LDAP_SERVER_URI is set (see base.py)
# All secrets from environment; do not commit credentials.
import ldap
from django_auth_ldap.config import LDAPSearch

# Server
AUTH_LDAP_SERVER_URI = __import__("os").environ.get("LDAP_SERVER_URI", "")

# Bind (service account that searches for users)
AUTH_LDAP_BIND_DN = __import__("os").environ.get("LDAP_BIND_DN", "")
AUTH_LDAP_BIND_PASSWORD = __import__("os").environ.get("LDAP_BIND_PASSWORD", "")

# User search
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    __import__("os").environ.get("LDAP_USER_BASE", "ou=users,dc=example,dc=com"),
    ldap.SCOPE_SUBTREE,
    "(uid=%(user)s)",
)

# Map LDAP attributes to User fields
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# Optional: mirror LDAP groups to Django groups
# AUTH_LDAP_GROUP_SEARCH = ...
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
# AUTH_LDAP_FIND_GROUP_PERMS = True

# Create user in Django on first LDAP login
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_CREATE_USER_PROFILE = False  # We use our own UserProfile
