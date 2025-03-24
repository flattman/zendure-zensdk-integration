"""Sensor platform for Zendure ZenSDK Integration."""
from .const import (
    CONF_MODEL,
    CONF_SERIAL_NUMBER,
    DEVICE_MANUFACTURER,
    DOMAIN,
    MODEL_SOLARFLOW800,
)
from .entity import ZendureZensdkIntegrationEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([ZendureZensdkIntegrationSensor(coordinator, entry)])
    serial_number = entry.data[CONF_SERIAL_NUMBER]
    model = entry.data[CONF_MODEL]

    entities = {}
    if coordinator.data:
        for property_name in coordinator.data["properties"]:
            entities.append(
                ZendureSolarFlowSensor(
                    coordinator, serial_number, model, property_name
                )
            )
    async_add_devices(entities)


class ZendureZensdkIntegrationSensor(ZendureZensdkIntegrationEntity):
    """zendure_zensdk_integration Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._property_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("body")
    
    @property
    def native_value(self) -> Any:
        """Gibt den Status des Sensors zurück."""
        if self.coordinator.data and "properties" in self.coordinator.data:
            return self.coordinator.data["properties"].get(self._property_name)
        return None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "zendure_zensdk_integration__custom_device_class"



class ZendureSolarFlowSensor(CoordinatorEntity, SensorEntity):
    """Definiert einen Zendure SolarFlow Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator, serial_number: str, model: str, property_name: str
    ) -> None:
        """Initialisiere den Zendure SolarFlow Sensor."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        self._model = model
        self._property_name = property_name
        self._attr_unique_id = f"{serial_number}-{property_name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": f"{model} ({serial_number[-4:]})",
            "model": model,
            "manufacturer": DEVICE_MANUFACTURER,
        }

    @property
    def name(self) -> str:
        """Gibt den Namen des Sensors zurück."""
        return self._property_name.replace("Power", " Leistung").replace("Volt", " Spannung").replace("Tmp", " Temperatur").replace("State", " Status").replace("Level", " Füllstand").replace("Time", " Zeit").replace("Num", " Anzahl").replace("Mode", " Modus").replace("Limit", " Limit").replace("Standard", " Standard").replace("Reverse", " Rückwärts").replace("Max", " Maximal").replace("Switch", " Schalter").replace("Ready", " Bereit").replace("Wakeup", " Aufwecken").replace("Zone", " Zone").replace("Rsp", " Antwort")

