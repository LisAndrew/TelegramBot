import aiohttp

async def getWeather(city):
    async with aiohttp.ClientSession() as session:
        query = {
            'q': city,
            'appid': 'token',
            'lang': 'ru',
            'cnt': 40,
            'units': 'metric'
        }

        BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast'

        async with session.get(url=BASE_URL, params=query) as response:
            return await response.json()
