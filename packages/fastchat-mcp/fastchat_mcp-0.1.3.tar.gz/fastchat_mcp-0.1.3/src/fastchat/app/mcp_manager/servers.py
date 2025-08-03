import os
import json
from mcp_oauth import OAuthClient


class Servers:
    """
    Extrae las credenciales de cada uno de los servers en la configuracion `.config.json`. Aternativamente puede pasarse otro archivo `.json`
    como argumento `config_file_path`
    """

    def __init__(
        self, config_file_path: str = "config.json", app_name: str = "fastchat-mcp"
    ):
        # self.config_file_path: str = config_file_path
        self.json_config: dict = self.__load_config_file(
            config_file_path=config_file_path
        )
        self.app_name = (
            self.json_config["app_name"] if "app_name" in self.json_config else app_name
        )
        self.mcp_servers: dict[str, dict] | None = {}
        self.__load_servers()

    def __load_config_file(self, config_file_path: str):
        with open(f"{os.getcwd()}{os.path.sep}{config_file_path}", "r") as file:
            json_config: dict = json.loads(file.read())
        return json_config

    def __load_servers(self):
        """Carga cada uno de los credenciales de los servidores que se le conectan desde el `.config`"""
        self.mcp_servers = self.json_config["mcp_servers"]

        for server in self.mcp_servers.values():
            self.__create_oauth_client(server=server)

    def __create_oauth_client(self, server: dict[str, dict]) -> None:
        """Genera un oauth client para este servidor, usando los datos proporcionados en `config.json`"""
        oauth_client: OAuthClient | None = None

        server_url: str | None = (
            server["httpstream-url"] if "httpstream-url" in server else None
        )

        if "auth" in server.keys() and (
            "required" in server["auth"].keys() and server["auth"]["required"]
        ):
            auth: dict = server["auth"]
            post_body = auth["post_body"]
            oauth_client = OAuthClient(
                client_name=self.app_name,
                mcp_server_url=server_url,
                body=post_body,
            )

        server["oauth_client"] = oauth_client
