import requests
import pandas as pd
from datetime import datetime, timezone

POCKETWORLD_URL = "https://pocketworld.org/api/flights"

LOCAL_FILE = "/opt/airflow/scripts/opensky_raw.csv"


def main():

    print("Requesting aircraft data from PocketWorld...")

    try:
        response = requests.get(
            POCKETWORLD_URL,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"PocketWorld request failed: {e}")

    flights = data.get("flights", [])

    print("Number of aircraft:", len(flights))

    if not flights:
        raise ValueError("No aircraft data received.")

    columns = [
        "icao24",
        "callsign",
        "country",
        "lng",
        "lat",
        "alt",
        "velocity",
        "heading",
        "vertical_rate",
        "squawk",
        "on_ground",
        "registration",
        "model",
        "typecode",
        "source",
        "last_seen",
        "last_contact",
        "category",
        "transport_kind",
    ]

    df = pd.DataFrame(flights)

    available_columns = [
        column for column in columns
        if column in df.columns
    ]

    df = df[available_columns]

    df = df.rename(
        columns={
            "country": "origin_country",
            "lng": "longitude",
            "lat": "latitude",
            "alt": "baro_altitude",
            "heading": "true_track",
        }
    )

    if "last_contact" in df.columns:
        df["last_contact"] = pd.to_datetime(
            df["last_contact"],
            unit="s",
            utc=True
        )

    df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")

    print("\nDataFrame:")
    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    df.to_csv(
        LOCAL_FILE,
        index=False
    )

    print(f"\nSuccessfully created local file:")
    print(LOCAL_FILE)


if __name__ == "__main__":
    main()
