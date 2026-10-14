"""UniFi Toolkit: installiert die gleichnamige App ueber den Supervisor."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Nichts zu tun, die Arbeit erledigt der Config Flow."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernen der Integration laesst die App unberuehrt."""
    return True
