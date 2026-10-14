"""Config Flow: App-Repository hinzufuegen, App installieren und starten."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohasupervisor import SupervisorError
from aiohasupervisor.models import AddonsOptions, StoreAddRepository

from homeassistant.components.hassio import (
    AddonError,
    AddonManager,
    AddonState,
    get_supervisor_client,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.hassio import is_hassio

from .const import APP_NAME, APP_SLUG_SUFFIX, DOMAIN, REPOSITORY_URL

_LOGGER = logging.getLogger(__name__)


def _same_repo(source: str) -> bool:
    return source.rstrip("/").removesuffix(".git").lower() == REPOSITORY_URL.lower()


class UnifiToolkitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Einrichtung in einem Schritt mit Fortschrittsanzeige."""

    VERSION = 1

    def __init__(self) -> None:
        self._install_task: asyncio.Task[str] | None = None
        self._app_slug: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if not is_hassio(self.hass):
            return self.async_abort(reason="not_hassio")

        if self._install_task is None:
            self._install_task = self.hass.async_create_task(self._async_install())

        if not self._install_task.done():
            return self.async_show_progress(
                step_id="user",
                progress_action="install_app",
                progress_task=self._install_task,
            )

        try:
            self._app_slug = await self._install_task
        except (AddonError, SupervisorError) as err:
            _LOGGER.error("Installation von %s fehlgeschlagen: %s", APP_NAME, err)
            return self.async_show_progress_done(next_step_id="install_failed")
        finally:
            self._install_task = None

        return self.async_show_progress_done(next_step_id="finish")

    async def async_step_install_failed(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_abort(reason="install_failed")

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_create_entry(
            title=APP_NAME, data={"app_slug": self._app_slug}
        )

    async def _async_install(self) -> str:
        """Repository registrieren, App installieren und starten. Gibt den Slug zurueck."""
        client = get_supervisor_client(self.hass)

        repos = await client.store.repositories_list()
        if not any(_same_repo(repo.source) for repo in repos):
            await client.store.add_repository(
                StoreAddRepository(repository=REPOSITORY_URL)
            )
            repos = await client.store.repositories_list()

        repo = next(repo for repo in repos if _same_repo(repo.source))
        slug = f"{repo.slug}_{APP_SLUG_SUFFIX}"

        manager = AddonManager(self.hass, _LOGGER, APP_NAME, slug)
        info = await manager.async_get_addon_info()
        if info.state == AddonState.NOT_INSTALLED:
            await manager.async_install_addon()
            info = await manager.async_get_addon_info()
        # Seitenleisten-Eintrag und Watchdog, beides ist bei neuen Apps aus
        await client.addons.set_addon_options(
            slug, AddonsOptions(ingress_panel=True, watchdog=True)
        )
        if info.state != AddonState.RUNNING:
            await manager.async_start_addon()
        return slug
