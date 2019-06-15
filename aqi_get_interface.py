from collections import defaultdict
import requests


stations_token = "http://api.gios.gov.pl/pjp-api/rest/station/findAll"
sensors_token = "http://api.gios.gov.pl/pjp-api/rest/station/sensors/"
magnitudes_token = "http://api.gios.gov.pl/pjp-api/rest/data/getData/"


def get_all_stations():
    return requests.get(stations_token).json()


def get_city_names():
    all_stations = get_all_stations()
    cities = set()
    for station in all_stations:
        if station["city"]: cities |= {station["city"]["name"]}
    return sorted(list(cities))


def get_stations(city_name):
    all_stations = get_all_stations()
    stations_id = []
    for chunk in all_stations:
        if chunk["city"] and chunk["city"]["name"].lower() == city_name.lower():
            stations_id.append(chunk["id"])
    return stations_id


def get_sensors(station_id):
    sensors = requests.get(f"{sensors_token}{station_id}").json()
    sensors_id = [s["id"] for s in sensors]
    return sensors_id


def get_magnitudes(sensor_id):
    magnitudes = requests.get(f"{magnitudes_token}{sensor_id}").json()
    value = magnitudes["values"][0]["value"]
    if not value: value = magnitudes["values"][1]["value"]
    return (magnitudes["key"], value) if value else (magnitudes["key"], 0)


def get_report(city_name):
    try:
        print(city_name)
        stations = get_stations(city_name)
        report = defaultdict(int)
        for station in stations:
            sensors = get_sensors(station)
            for sensor in sensors:
                mol, value = get_magnitudes(sensor)
                report[mol] = max(report[mol], value)
        return "\n".join(sorted([f"{k}: {v}" for k, v in report.items()]))
    except Exception:
        return "Something went wrong, try again"
