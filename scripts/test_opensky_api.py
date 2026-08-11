import requests
import pandas as pd


def main():

    url = "https://opensky-network.org/api/states/all"

    try:
        response = requests.get(url, timeout=30)

        print("Status Code:", response.status_code)

        data = response.json()

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return

    print("Number of aircraft:", len(data["states"]))

    columns = [
        "icao24",
        "callsign",
        "origin_country",
        "time_position",
        "last_contact",
        "longitude",
        "latitude",
        "baro_altitude",
        "on_ground",
        "velocity",
        "true_track",
        "vertical_rate",
        "sensors",
        "geo_altitude",
        "squawk",
        "spi",
        "position_source",
    ]

    df = pd.DataFrame(data["states"], columns=columns)

    print("\nDataFrame:")
    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    df["time_position"] = pd.to_datetime(
        df["time_position"],
        unit="s",
        utc=True
    )

    df["last_contact"] = pd.to_datetime(
        df["last_contact"],
        unit="s",
        utc=True
    )

    df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")

    print(
        df[
            [
                "icao24",
                "callsign",
                "time_position",
                "last_contact",
                "ingestion_timestamp",
            ]
        ].head()
    )

    df.to_csv("data/raw/opensky_raw.csv", index=False)

    print("\nRaw data saved successfully.")
    print("File: data/raw/opensky_raw.csv")


if __name__ == "__main__":
    main()