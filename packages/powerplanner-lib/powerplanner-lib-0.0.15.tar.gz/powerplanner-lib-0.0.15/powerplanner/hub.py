"""The hub  for powerplanner."""
from datetime import datetime
import aiozoneinfo

from .api_client import ApiClient

class PowerplannerHub:
    """Hub for powerplanner."""

    manufacturer = "NomKon AB"
    url = "https://api.powerplanner.se"

    def __init__(self, api_key: str, url: str = None) -> None:        
        self.time_zone = aiozoneinfo.get_time_zone("Europe/Stockholm")
        self.use_ssl = True
        
        if(url is not None):
            self.url = url
            self.use_ssl = False
        
        self.api_client = ApiClient(self.url, api_key, self.use_ssl)
        self.api_key = api_key
        self.schedules = None
        self.plans = None
        self.plan_names = None
        self.updated: datetime
        self.plans_changed = False
        self.change_callback = None
        self.add_sensor_callback  = None
        self.remove_sensor_callback = None
        self.sensors: list[any] = []
        self.old_plans: list[str] = []
        self.new_plans: list[str] = []

    async def update(self) -> None:
        """Update all schedules."""        
        self.schedules = await self.api_client.get_schedules()
        self.updated = datetime.now()
        updated_plans = list(self.schedules)
        self.new_plans = self._get_new_plans(updated_plans, self.plan_names)
        self.old_plans = self._get_removed_plans(updated_plans, self.plan_names)
        self.plans_changed = self.old_plans is not [] or self.new_plans is not []
        self.plan_names = updated_plans
        if(self.plans_changed):
            self.plans = await self.api_client.get_plans()
    
    async def toggle(self, plan_id: str, enabled: bool) -> None:
        await self.api_client.toggle_plan(plan_id, enabled)
        await self.update()
    
    async def set_property(self, plan_id: str, property_key: str, value: any) -> None:
        await self.api_client.set_plan_property(plan_id, property_key, value)
        await self.update()
    
    def get_next_change(self, name: str) -> datetime | None:
        """Get the time the next change is with the plan."""
        if name not in self.plan_names:
            return None

        current_value = self._current_value(name)
        next_value = self._next_value(name, not current_value)

        if next_value is None:
            return None

        current_time = self._current_time()
        return self._parse_time(next_value["startTime"], current_time.tzinfo)

    def add_sensor(self, sensor):
        self.sensors.append(sensor)
        self.add_sensor_callback([sensor])

    async def remove_sensor(self, sensor_name: str):
        found = None
        for sensor in self.sensors:
            if sensor.schedule_name == sensor_name:
                found = sensor
                break

        if found is None:
            return

        await found.async_remove()
        self.sensors.remove(found)

    def time_to_change(self, name) -> int:
        change_time = self.get_next_change(name)
        if(change_time is datetime.max or change_time is None):
            return 0
        
        delta = change_time - self._current_time()

        return delta.seconds

    def is_on(self, name) -> bool:
        if self.schedules is None or name not in self.plan_names:
            return False

        now_str = self._current_time_str()
        schedule = list(self.schedules[name])

        filtered = list(filter(lambda x: x["enabled"] is True, schedule))
        filtered = list(filter(lambda x: x["startTime"] <= now_str, filtered))
        filtered = list(filter(lambda x: x["endTime"] > now_str, filtered))
        return len(filtered) > 0

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        return await self.api_client.authenticate()        

    def _get_new_plans(self, new_plans, old_plans) -> list[str]:
        return self._get_missing(new_plans, old_plans)

    def _get_removed_plans(self, new_plans, old_plans):
        return self._get_missing(old_plans, new_plans)

    def _get_missing(self, a, b) -> list[str]:
        result = []

        if a is None:
            return []

        if b is None:
            return a

        for x in a:
            found = False
            for y in b:
                if x == y:
                    found = True

            if found is False:
                result.append(x)

        return result

    def _current_value(self, name) -> bool:
        now_str = self._current_time_str()
        schedule = list(self.schedules[name])

        filetered = list(filter(lambda x: x["startTime"] <= now_str, schedule))
        filetered = list(filter(lambda x: x["endTime"] > now_str, filetered))
        if len(filetered) == 0:
            return False
        return filetered[0]["enabled"]

    def _next_value(self, name, value: bool):
        now_str = self._current_time_str()
        schedule = list(self.schedules[name])

        filetered = list(filter(lambda x: x["enabled"] == value, schedule))
        filetered = list(filter(lambda x: x["startTime"] > now_str, filetered))
        if len(filetered) == 0:
            return None
        return filetered[0]

    def _current_time(self):        
        return datetime.now(tz=self.time_zone)

    def _current_time_str(self):
        now_str = self._current_time().strftime("%Y-%m-%dT%H:%M:%S")
        return now_str

    async def _init_time_zone(self):
        return await aiozoneinfo.async_get_time_zone("Europe/Stockholm")
    
    def _parse_time(self, string: str, tz_info):
        time = datetime.fromisoformat(string)
        return datetime(
            time.year,
            time.month,
            time.day,
            time.hour,
            time.minute,
            time.second,
            tzinfo=tz_info,
        )
