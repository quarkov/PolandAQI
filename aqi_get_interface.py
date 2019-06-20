from collections import defaultdict
import requests


class AQI:
    stations_token = "http://api.gios.gov.pl/pjp-api/rest/station/findAll"
    sensors_token = "http://api.gios.gov.pl/pjp-api/rest/station/sensors/"
    magnitudes_token = "http://api.gios.gov.pl/pjp-api/rest/data/getData/"

    def __init__(self):
        self._country_stations = self.get_country_stations()
        self._cities = self.get_cities_names()
        self._extended_reports = defaultdict(dict)
        self._short_reports = defaultdict(dict)

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
        return sorted(self._country_stations.keys())

    def get_city_stations(self, city):
        return self._country_stations[city]

    def get_station_data(self, station_id):
        sensors = requests.get(f"{self.sensors_token}{station_id}").json()
        sensors_id = [s["id"] for s in sensors]
        data = {}
        for id in sensors_id:
            magnitudes = requests.get(f"{self.magnitudes_token}{id}").json()
            chems = magnitudes["key"]
            value = 0
            for m in magnitudes["values"]:
                if m["value"]:
                    value = m["value"]
                    break
            data.update({chems: round(value, 2)})
        return data

    def get_report_extended(self, city_name):
        city_name = " ".join([chunk.capitalize() for chunk in city_name.split()])
        if city_name not in self._cities:
            return "Can't find data for this city. Check spelling and/or try another city"

        if city_name not in self._extended_reports:
            for station in self._country_stations[city_name]:
                self._country_stations[city_name][station]["data"] = self.get_station_data(station)
                street = self._country_stations[city_name][station]["address"]
                values = self._country_stations[city_name][station]["data"]
                self._extended_reports[city_name].update({street: values})
        return self._extended_reports[city_name]

    def get_report_short(self, city_name):
        if city_name in self._short_reports:
            return self._short_reports[city_name]
        else:
            extended = self.get_report_extended(city_name)

        data = defaultdict(dict)
        for item in extended.values():
            for mol in item:
                data[mol] = item[mol] if not data[mol] else max(data[mol], item[mol])
        self._short_reports[city_name] = data
        return data


report = AQI()
