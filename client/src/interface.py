# src/interface.py
import json
import requests
from datetime import datetime, timezone
from typing import Optional
from env import ENV
from hmac_auth import HmacAuth
class APIClient:

    def __init__(self, event_manager):
        self.url = str(ENV.API_URL)
        self.headers = {"Content-Type": "application/json"}
        self.__auth_method = HmacAuth()
        self.status_active = self.__notify_server()
        self.event_manager = event_manager

    async def __send_data(self, data: dict) -> Optional[str]:
        print(f"Sending data to {self.url}")
        result = ""
        if (self.status_active):
            payload = json.dumps(data)
            try:
                response = requests.post(self.url, payload, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    result = response.text
                else:
                    result = "HTTP Error"
                    raise Exception(f"HTTP error: {response.status_code}")
            except Exception as e:
                result = "HTTP Timeout"
                print(f"Error sending data to API: {e}")
        return result

    async def send_data_to_api(self, data: dict) -> None:
        if data:
            # Send the measurement values to API
            response = await self.__send_data(data)
            if response:
                print("API Response: ", response)
                if data.get("type") == "m":
                    try:
                        parsed_data = json.loads(response)
                        decoded_response = self.decode_labels(parsed_data)
                        self.event_manager.server_response = decoded_response
                    except Exception as e:
                        print(f"Error parsing API response: {e}")
                        self.event_manager.server_response = response
        return None

    def __notify_server(self) -> bool:
        success = False
        time = int(datetime.now(tz=timezone.utc).timestamp())
        hmac_headers = self.__auth_method.ask_for_headers(str(time))
        data = {
                'id': int(str(ENV.DEVICE_ID)),
                'time': time,
            }
        payload = json.dumps(data)
        try:
            response = requests.post(self.url + "/notify", payload, headers=hmac_headers, timeout=(5, 10))
            if response.status_code == 200:
                success = True
                print(f"Succesfully initiated server object of Device ID:{str(ENV.DEVICE_ID)}")
            else:
                success = False
                raise Exception(f"HTTP error: {response.status_code}")
        except Exception as e:
            print(f"Error sending data to API: {e}")
            success = False
        print(f"Finished initializing APIClient, with status: {'Success' if success else 'Failed'}")
        return success

    def decode_labels(self, data) -> str:
        if not isinstance(data, dict) or "outputs" not in data:
            return "Invalid data format"

        try:
            probabilities = data["outputs"][0]
            decoded_labels = []

            material_names = ["Polyester", "Cotton", "Wool"]

            for i, prob in enumerate(probabilities):
                if i >= 0 and i < len(material_names):
                    decoded_labels.append({"material": material_names[i], "probability": prob})
                else:
                    print(f"Warning: Invalid index for material name: {i}")

                decoded_labels.sort(key=lambda label: label["probability"], reverse=True)
                formatted_string = "".join([f"{label['material']}: {int(label['probability'] * 100)}%\n" for label in decoded_labels])
            return formatted_string

        except Exception as e:
            print(f"Error decoding labels: {e}")
            return "Unknown"