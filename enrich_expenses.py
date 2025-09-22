import csv
import json
import requests
from datetime import datetime

def geocode_city(city, country_code):
    """Get latitude & longitude for a city."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&country={country_code}&count=1"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if "results" in data and data["results"]:
        r = data["results"][0]
        return r["latitude"], r["longitude"]
    return None, None

def get_weather(lat, lon):
    """Get current weather from coordinates."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if "current_weather" in data:
        cw = data["current_weather"]
        return cw["temperature"], cw["windspeed"]
    return None, None

def convert_to_usd(currency, amount):
    """Convert from local currency to USD."""
    url = f"https://api.exchangerate.host/convert?from={currency}&to=USD&amount={amount}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if data.get("success"):
        return data["info"]["rate"], data["result"]
    return None, None

def enrich_expenses(input_csv, output_json):
    enriched = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            city = row["city"]
            country = row["country_code"]
            currency = row["currency"]
            amount = float(row["amount"])

            lat, lon = geocode_city(city, country)
            temp, wind = (None, None)
            if lat and lon:
                temp, wind = get_weather(lat, lon)

            rate, usd = convert_to_usd(currency, amount)

            row.update({
                "latitude": lat,
                "longitude": lon,
                "temperature_c": temp,
                "wind_speed_mps": wind,
                "fx_rate_to_usd": rate,
                "amount_usd": usd,
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            })
            enriched.append(row)

    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(enriched, out, indent=2)
    print(f"Wrote {len(enriched)} records to {output_json}")

if __name__ == "__main__":
    enrich_expenses("expenses.csv", "enriched_expenses.json")


