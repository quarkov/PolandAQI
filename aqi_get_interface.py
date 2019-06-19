from collections import defaultdict
import requests


class AQI:
    stations_token = "http://api.gios.gov.pl/pjp-api/rest/station/findAll"
    sensors_token = "http://api.gios.gov.pl/pjp-api/rest/station/sensors/"
    magnitudes_token = "http://api.gios.gov.pl/pjp-api/rest/data/getData/"

    def __init__(self):
        self.country_stations = self.get_country_stations()
        self.cities = self.get_cities_names()

    def get_country_stations(self):
        response = requests.get(self.stations_token).json()
        country_stations = defaultdict(dict)
        for record in response:
            if record["city"]:
                city_name = record["city"]["name"]
                station = {record["id"]: {"address": record["addressStreet"], "data": None}}
                country_stations[city_name].update(station)
        return country_stations

    def get_cities_names(self):
        return sorted(self.country_stations.keys())

    def get_city_stations(self, city):
        return self.country_stations[city]

    def get_station_data(self, station_id):
        sensors = requests.get(f"{self.sensors_token}{station_id}").json()
        sensors_id = [s["id"] for s in sensors]
        data = {}
        for id in sensors_id:
            magnitudes = requests.get(f"{self.magnitudes_token}{id}").json()
            chems = magnitudes["key"]
            value = magnitudes["values"][1]["value"]
            data.update({chems: round(value, 2)})
        return data

    def get_city_report(self, city_name):
        city_name = " ".join([chunk.capitalize() for chunk in city_name.split()])
        if city_name not in self.cities:
            return "Can't find data for this city. Check spelling and/or try another city"

        for station in self.country_stations[city_name]:
            self.country_stations[city_name][station]["data"] = self.get_station_data(station)
        return self.country_stations[city_name]


report = AQI()
gdansk = report.get_city_report("Gdańsk")
[print(f"{e['address']} {e['data']}") for e in gdansk.values()]
