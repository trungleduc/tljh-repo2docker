import os
from typing import Dict
from tornado import web
from jupyterhub.utils import url_path_join
from jupyterhub.services.auth import HubOAuthenticated
from jinja2 import Template
from .model import UserModel
from httpx import AsyncClient
import json

JUPYTERHUB_API_URL = os.environ.get("JUPYTERHUB_API_URL", "")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", None)
print("JUPYTERHUB_API_URL", JUPYTERHUB_API_URL)


class BaseHandler(HubOAuthenticated, web.RequestHandler):
    """
    Base handler for tljh_repo2docker service
    """
    _client = None

    @property
    def client(self):
        if not BaseHandler._client:
            BaseHandler._client = AsyncClient(
                base_url=JUPYTERHUB_API_URL,
                headers={f"Authorization": f"Bearer {API_TOKEN}"},
            )
        return BaseHandler._client

    async def fetch_user(self) -> UserModel:
        user = self.current_user
        url = url_path_join("users", user["name"])
        response = await self.client.get(url + "?include_stopped_servers")
        user_model = response.json()
        return UserModel.from_dict(user_model)

    def get_template(self, name: str) -> Template:
        """Return the jinja template object for a given name
        Args:
            name: Template name
        Returns:
            jinja2.Template object
        """
        return self.settings["jinja2_env"].get_template(name)

    def render_template(self, name: str, **kwargs) -> str:
        """Render the given template with the provided arguments
        Args:
            name: Template name
            **kwargs: Template arguments
        Returns:
            The generated template
        """
        user = self.current_user
        template_ns = dict(
            service_prefix=self.settings.get("service_prefix", "/"),
            hub_prefix=self.settings.get("hub_prefix", "/"),
            base_url=self.settings.get("base_url", "/"),
            static_url=self.static_url,
            xsrf_token=self.xsrf_token.decode("ascii"),
            user=user,
            admin_access=user["admin"],
        )
        template_ns.update(kwargs)
        template = self.get_template(name)
        return template.render(**template_ns)

    def get_json_body(self):
        """Return the body of the request as JSON data."""
        if not self.request.body:
            return None
        body = self.request.body.strip().decode("utf-8")
        try:
            model = json.loads(body)
        except Exception:
            self.log.debug("Bad JSON: %r", body)
            self.log.error("Couldn't parse JSON", exc_info=True)
            raise web.HTTPError(400, "Invalid JSON in body of request")
        return model
