from typing import Any, Dict, Optional

from nornir.core.configuration import Config

from netbane import NetBane as nb

CONNECTION_NAME = "netbane"


class NetBane:
    """Open connection to device with NetBane"""

    def open(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        extras = extras or {}

        parameters: Dict[str, Any] = {
            "host": hostname,
            "username": username,
            "password": password,
            "platform": platform,
            "optional_args": {},
        }

        try:
            parameters["optional_args"][
                "ssh_config_file"
            ] = configuration.ssh.config_file  # type: ignore
        except AttributeError:
            pass

        parameters.update(extras)

        if port and "port" not in parameters["optional_args"]:
            parameters["optional_args"]["port"] = port

        connection = nb(**parameters)
        connection.open()
        self.connection = connection

    def close(self) -> None:
        self.connection.close()
