import aiohttp
from .models import PowerPlan

class ApiClient:        
    def __init__(self, base_url: str, api_key: str, ssl: bool = True) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.ssl = ssl
        
    async def get_schedules(self):
        url = self.base_url + "/api/scheme/?token=" + self.api_key
        resp = await self.__get(url)
        json = await resp.json()
        return json["schedules"]
    
    async def authenticate(self) -> bool:
        url = self.base_url + "/api/scheme/?token=" + self.api_key
        resp = await self.__get(url, False)
        return resp.status == 200        
    
    async def get_plans(self) -> list[PowerPlan]:
        url = self.base_url + "/api/plan/list/?token=" + self.api_key
        resp = await self.__get(url)
        json = await resp.json()
        plans = [PowerPlan(item["name"], item["id"], item["enabled"],item["dynamicProperties"]) for item in json]
        return plans;
    
    async def toggle_plan(self, plan_id: str, enabled: bool) -> aiohttp.ClientResponse:
        url = self.base_url + "/api/plan/" + plan_id +"/toggle/?token=" + self.api_key        
        resp = await self.__post_bool(url, enabled)
        return resp
    
    async def set_plan_property(self, plan_id: str, property_key: str, value: any) -> aiohttp.ClientResponse:
        url = self.base_url + "/api/plan/" + plan_id +"/property/" + property_key +"/?token=" + self.api_key
        resp = await self.__post_str(url, value)
        return resp
    
    async def __post_bool(self, url: str, data: bool, read: bool = True) -> aiohttp.ClientResponse:
        data_bool = str(data).lower();
        return await self.__post(url, data_bool, read)
    
    async def __post_str(self, url: str, data: str, read: bool = True) -> aiohttp.ClientResponse:
        data_str = "\""+str(data)+"\""         
        return await self.__post(url, data_str, read)
    
    async def __get(self, url: str, read: bool = True) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session, session.get(url) as resp:
            if read:
                await resp.read()
            return resp
    
    async def __post(self, url: str, data: any, read: bool = True) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            resp = await session.post(url, data=data, headers={"Content-Type": "application/json"})
            if read:
                await resp.read()
            return resp