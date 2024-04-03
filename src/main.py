import psycopg2
from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import os
import time

class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # Configuration via des variables d'environnement
        self.HOST = os.getenv("HOST", "http://159.203.50.162")
        self.TOKEN = os.getenv("TOKEN", "9730b385b193edd1e758")
        self.T_MAX = int(os.getenv("T_MAX", 60))
        self.T_MIN = int(os.getenv("T_MIN", 40))
        self.DB_NAME = os.getenv("DB_NAME", "db02eq6")
        self.DB_HOST = os.getenv("DB_HOST", "157.230.69.113")
        self.DB_USER = os.getenv("DB_USER", "user02eq6")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "hh11IRZulzXFkPiU")
        self.DB_PORT = os.getenv("DB_PORT", "5432")

    def __del__(self):
        if self._hub_connection:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if temperature >= self.T_MAX:
            self.send_action_to_hvac("TurnOnAc")
        elif temperature <= self.T_MIN:
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        print("SENDING TO DATABASE")

        conn = psycopg2.connect(database=self.DB_NAME,
                                host=self.DB_HOST,
                                user=self.DB_USER,
                                password=self.DB_PASSWORD,
                                port=self.DB_PORT)
        try:
            print("CONNECT TO DATABASE")
            cur = conn.cursor()

            cur.execute("""CREATE TABLE IF NOT EXISTS sensor_data (
                        id SERIAL PRIMARY KEY,
                        timestamp VARCHAR (50) NOT NULL,
                        temperature FLOAT NOT NULL
                        );
                        """)

            print("CREATING TABLE")

            cur.execute("INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s)", (timestamp, temperature))
            print("INSERT DATA")

            conn.commit()

            cur.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")

if __name__ == "__main__":
    app = App()
    app.start()
