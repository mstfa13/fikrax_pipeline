import requests
import json
import psycopg2
from datetime import datetime

def get_recent_earthquakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    return response.json()

def connect_db():
    return psycopg2.connect(
        host="aws-1-eu-west-2.pooler.supabase.com",
        database="postgres",
        user="postgres.ehdzhysoryzyxiqmbqzk",
        password="lr52c8z3@fikrax_pipeline"
    )

def insert_earthquakes(conn, earthquakes):
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0

    for quake in earthquakes:
        props = quake["properties"]
        coords = quake["geometry"]["coordinates"]
        
        try:
            cursor.execute("""
                INSERT INTO raw.earthquakes (
                    id, mag, place, time, updated, tz, url, detail,
                    felt, cdi, mmi, alert, status, tsunami, sig,
                    net, code, ids, sources, types, nst, dmin, rms,
                    gap, mag_type, type, title, longitude, latitude, depth
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
                ON CONFLICT (id) DO NOTHING
            """, (
                quake["id"],
                props.get("mag"),
                props.get("place"),
                props.get("time"),
                props.get("updated"),
                props.get("tz"),
                props.get("url"),
                props.get("detail"),
                props.get("felt"),
                props.get("cdi"),
                props.get("mmi"),
                props.get("alert"),
                props.get("status"),
                props.get("tsunami"),
                props.get("sig"),
                props.get("net"),
                props.get("code"),
                props.get("ids"),
                props.get("sources"),
                props.get("types"),
                props.get("nst"),
                props.get("dmin"),
                props.get("rms"),
                props.get("gap"),
                props.get("magType"),
                props.get("type"),
                props.get("title"),
                coords[0],
                coords[1],
                coords[2]
            ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting {quake['id']}: {e}")
            skipped += 1

    conn.commit()
    cursor.close()
    print(f"Done. Inserted: {inserted}, Skipped: {skipped}")

def main():
    data = get_recent_earthquakes()
    if not data:
        return
    
    conn = connect_db()
    insert_earthquakes(conn, data["features"])
    conn.close()

if __name__ == "__main__":
    main()