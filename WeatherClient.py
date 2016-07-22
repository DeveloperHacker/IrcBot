import re
import requests


class WeatherClient:

    def __init__(self, key: str):
        self.__key = key
        self.__data = {}

    def update(self, city: str):
        url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + self.__key
        self.__data[city] = str(requests.get(url).json())

    def summary(self, city: str) -> str:
        if city not in self.__data: self.update(city)
        return self.__data[city]

    def temperature(self, city: str) -> float:
        summary = self.summary(city)
        return float(re.findall(r"'temp':\s(\d+\.*\d*)", summary)[0]) - 273

    def wind(self, city: str) -> [float, float]:
        summary = self.summary(city)
        speed = float(re.findall(r"'speed':\s(\d+\.*\d*)", summary)[0])
        deg = float(re.findall(r"'deg':\s(\d+\.*\d*)", summary)[0])
        return [deg, speed]

    @staticmethod
    def format_wind(wind: [float, float]) -> [str, float]:
        deg = wind[0]
        desc = deg
        if 22.5 > deg or deg >= 337.5: desc = "южный"
        elif 22.5 < deg <= 67.5: desc = "юго-западный"
        elif 67.5 < deg <= 112.5: desc = "западный"
        elif 112.5 < deg <= 157.5: desc = "северо-западный"
        elif 157.5 < deg <= 202.5: desc = "северный"
        elif 202.5 < deg <= 247.5: desc = "северо-восточный"
        elif 247.5 < deg <= 292.5: desc = "восточный"
        elif 292.5 < deg <= 337.5: desc = "юго-восточный"
        return [desc, wind[1]]

    def pressure(self, city: str) -> float:
        summary = self.summary(city)
        return float(re.findall(r"'pressure':\s(\d+\.*\d*)", summary)[0])

    def humidity(self, city: str) -> int:
        summary = self.summary(city)
        return float(re.findall(r"'humidity':\s(\d+\.*\d*)", summary)[0])

    def description(self, city: str) -> str:
        summary = self.summary(city)
        return re.findall(r"'description':\s'([\w\s]+)'", summary)[0]
