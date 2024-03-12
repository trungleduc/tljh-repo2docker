from inspect import isawaitable

from tornado import web
from .base import BaseHandler
from .docker import list_containers, list_images


class EnvironmentsHandler(BaseHandler):
    """
    Handler to show the list of environments as Docker images
    """

    @web.authenticated
    async def get(self):
        user = self.current_user

        if not user["admin"]:
            raise web.HTTPError(status_code=404, reason="Unauthorized.")
        images = await list_images()
        containers = await list_containers()
        result = self.render_template(
            "images.html",
            images=images + containers,
            default_mem_limit=self.settings.get("default_mem_limit"),
            default_cpu_limit=self.settings.get("default_cpu_limit"),
            machine_profiles=self.settings.get("machine_profiles", []),
        )
        if isawaitable(result):
            self.write(await result)
        else:
            self.write(result)
