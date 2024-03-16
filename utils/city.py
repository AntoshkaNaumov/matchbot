import aiohttp


async def check_city(city_name: str) -> bool:
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={city_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data and isinstance(data, list):
                return True
            return False
