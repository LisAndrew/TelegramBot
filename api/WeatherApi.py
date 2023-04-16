import aiohttp

async def getWeather(city):
    async with aiohttp.ClientSession() as session:
        query = {
            'q': city,
            'appid': 'a3993f31ef3974d66a2454e5c9bd9590',
            'lang': 'ru',
            'cnt': 40,
            'units': 'metric'
        }

        BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast'

        async with session.get(url=BASE_URL, params=query) as response:
            return await response.json()
