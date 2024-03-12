"""
This file is only used for local development
and overrides some of the default values from the plugin.
"""

import getpass

from jupyterhub.auth import DummyAuthenticator
from tljh.configurer import apply_config, load_config
from tljh_repo2docker import tljh_custom_jupyterhub_config
import sys

c.JupyterHub.services = []

tljh_config = load_config()

# set default limits in the TLJH config in memory
# tljh_config["limits"]["memory"] = "2G"
# tljh_config["limits"]["cpu"] = 2

# set CPU and memory based on machine profiles
tljh_config["limits"]["machine_profiles"] = [
    {"label": "Small", "cpu": 2, "memory": 2},
    {"label": "Medium", "cpu": 4, "memory": 4},
    {"label": "Large", "cpu": 8, "memory": 8},
]

apply_config(tljh_config, c)

tljh_custom_jupyterhub_config(c)

c.JupyterHub.authenticator_class = DummyAuthenticator

user = getpass.getuser()
c.Authenticator.admin_users = {user, "alice"}
c.JupyterHub.allow_named_servers = True
c.JupyterHub.ip = "0.0.0.0"

c.JupyterHub.services.extend(
    [
        {
            "name": "tljh_repo2docker",
            "url": "http://127.0.0.1:6789",
            "command": [
                sys.executable,
                "-m",
                "tljh_repo2docker",
                "--ip",
                "127.0.0.1",
                "--port",
                "6789",
            ],
            "oauth_no_confirm": True,
        }
    ]
)

c.JupyterHub.load_roles = [
    {
        "description": "Role for tljh_repo2docker service",
        "name": "tljh_repo2docker_role",
        "scopes": ["read:users", "read:servers", "read:roles:users"],
        "services": ["tljh_repo2docker"],
    },
    {
        "name": "env-user",
        "scopes": [
            # access to the env page
            "access:services"
        ],
        "users": ["trung"],
    },
]
