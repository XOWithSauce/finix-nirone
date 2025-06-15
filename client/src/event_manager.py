# src/event_manager.py
import asyncio
from datetime import datetime, timezone
from interface import APIClient
from serial_device import SerialDevice
from hardware_class import LedControl
from bt.bt_auth import BTAuth
from bsd_client import BSDClient
from env import ENV

class EventManager():
    def __init__(self) -> None:
        
        
        # Networking utility
        self.api_client = APIClient(self)
        self.send_measurement = asyncio.Event()
        self.received_data = asyncio.Queue()
        self.server_response = "No measurements"
        
        # Hardware utility
        self.serial_device = SerialDevice(self)
        self.previous_event = ""
        self.in_progress = False
        self.led_control = LedControl()
        
        
        # Sensor measurement utility
        self.measure_event = asyncio.Event()
        self.white_ref_event = asyncio.Event()
        self.backgr_rad_event = asyncio.Event()
        self.white_ref_values = []
        self.backgr_rad_values = []
        self.measure_history = []
        
        # Bluetooth utility
        self.bt_auth = BTAuth((str(ENV.SHARED_SIGN_KEY)), (str(ENV.SHARED_ENCR_KEY)))
        self.white_ref_calibrated = False
        self.backgr_rad_calibrated = False
        self.uart_rx_reader_field: bytearray
        
        # Local inference utility
        self.bsd_client = BSDClient()
        
    async def clear_events(self):
        self.measure_event.clear()
        self.white_ref_event.clear()
        self.backgr_rad_event.clear()

    async def start_measurement(self, type: str):
        await self.led_control.on()
        self.in_progress = True
        await self.serial_device.shared_objects(self.received_data, self.send_measurement)
        await self.serial_device.measure(type)
        await self.send_measurement.wait()
        await self.clear_events()
        self.in_progress = False
        await self.led_control.off()
        print("Done meas")

    async def hw_event_handler(self):
        # Main measure button pressed
        if self.measure_event.is_set():
            # If calibration event was set
            if self.white_ref_event.is_set():
                print("MEASURE WHITEREF")
                self.previous_event = "w"
                await self.start_measurement("w")
                self.white_ref_calibrated = True
                return
            elif self.backgr_rad_event.is_set():
                print("MEASURE BACKGR RAD")
                self.previous_event = "b"
                await self.start_measurement("b")
                self.backgr_rad_calibrated = True
                return
            # Else Normal measurement
            else:
                if (self.white_ref_calibrated & self.backgr_rad_calibrated):
                    print("MEASURE NORMAL")
                    self.previous_event = "m"
                    await self.start_measurement("m")
                else:
                    print("---\nNON-CALIBRATED\nCALIBRATE BEFORE MEASURE NORMAL\n---")
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.led_control.blink_red())
                    self.previous_event = ""
                    await self.clear_events()

    def ev_done_callback(self, task):
        history_length = len(self.measure_history)
        if history_length > 5:
            self.measure_history.pop(history_length-1)
        self.measure_history.insert(0,
            {
            "time": int(datetime.now(tz=timezone.utc).timestamp()),
            "labels": self.server_response,
            }
        )

    async def api_event_handler(self):
        # We check first if API Client has initiated succesfully
        # and server is reachable
        if (self.api_client.status_active):
            if not self.received_data.empty():
                data = await self.received_data.get()
                packet = {
                    'data': data,
                    'time': int(datetime.now(tz=timezone.utc).timestamp()), 
                    'id': int(str(ENV.DEVICE_ID)),
                    'type': self.previous_event,
                }
                await asyncio.wait_for(self.api_client.send_data_to_api(packet), timeout=5000)
                self.send_measurement.clear()
                self.previous_event = ""
            else:
                pass
        # As a fallback method, we can run inference on local model
        # Also handling any mathematical operations needed.
        else:
            if not self.received_data.empty():
                data = await self.received_data.get()
                print("RECV DATA: ", data)
                print("DATA TYPE: ", type(data))
                if (self.previous_event == "w"):
                    print("White Reference values saved")
                    self.white_ref_values = data
                elif (self.previous_event == "b"):
                    print("Background Reference values saved")
                    self.backgr_rad_values = data
                elif (self.previous_event == "m"): # We are currently running measurement that we want to predict
                    # This is dependant on reference values.
                    print("Calculating Reflectance")
                    print(type(self.white_ref_values))
                    print("WHITE REF LIST", len(self.white_ref_values), "BACKGR RAD LIST: ", len(self.backgr_rad_values))
                    if (self.white_ref_calibrated & self.backgr_rad_calibrated):
                        try: 
                            reflectance = [(m - d) / (w - d) for m, w, d in zip(data, self.white_ref_values, self.backgr_rad_values)]
                            print("minmax")
                            min_reflectance = min(reflectance)
                            max_reflectance = max(reflectance)
                            print("Scaling to 0... 1 ...")
                            scaled_reflectance = [(a - min_reflectance) / (max_reflectance - min_reflectance) for a in reflectance]
                            # Todo: Apply savgol filter (simplify based on https://github.com/scipy/scipy/blob/v1.15.3/scipy/signal/_savitzky_golay.py)
                            # use Params from Model / ThesisBase
                            self.server_response = self.bsd_client.local_inference(scaled_reflectance)
                        except Exception as e:
                            print("Failed to pre-treat sensor data: ", e)
                
                # Then we reset objects for next measurement
                self.send_measurement.clear()
                self.previous_event = ""
    
    async def wait_for_events(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.led_control.startup_notification())
        print("Falling into event loop")
        while True:
            await asyncio.sleep(1)
            if not self.in_progress:
                loop.create_task(self.hw_event_handler())

            if self.send_measurement.is_set():
                task = loop.create_task(self.api_event_handler())
                task.add_done_callback(self.ev_done_callback)
                await task

    def messager(self, message: str) -> None:
        print("Messager: ", message)
        result = self.bt_auth.decrypt_message(message)
        print("Parse result: ", result)
        if (result != ""):
            print("Creating task...")
            try:
                self.parser(result)
            except Exception as e:
                print("Error while starting: ", e)
        return

    def reader(self, message: str) -> None:
        # Define default on exceptions
        try:
            encrypted_message = self.bt_auth.encrypt_message(message)
            result = bytearray(encrypted_message.encode())
            print("Setting to result: ", result)
            self.uart_rx_reader_field = result
        except:
            pass
        return
    
    def parser(self, msg: str):
        if (msg == "poll_Label"):
            print("LabelPoll")
            self.reader(self.server_response)
        
        elif (msg == "m_Whiteref"):
            print("PARSED WHITE REF!")
            if not (self.white_ref_calibrated):
                self.white_ref_event.set()
            
        elif (msg == "m_Darkref"):
            if not (self.backgr_rad_calibrated):
                self.backgr_rad_event.set()
            
        elif (msg == "b_Calibrated"):
            if (self.backgr_rad_calibrated & self.white_ref_calibrated):
                self.reader("True")
                print("bCalibrated true")
            else:
                self.reader("False")
                print("bCalibrated false")
        
        elif (msg == "i_Sertemp"):
            print("SERIAL TEMP")
            # Add logic to automatically measure sensor temp periodically / after each measurement
            try:
                temp = self.serial_device.sensor_temp
            except Exception as e:
                print("Failed to get temp: ", e)
                temp = "0"
            print("Setting temp to rx: ", temp)
            self.reader(temp)
            
        elif (msg == "list_History"):
            print("Listing history")
            try:
                print("To be done")
                # TODO:
                # Make self.measure_history format to string from dict list and return in server response
                # Check for string length boundaries
            except Exception as e:
                print("Failed to return history list: ", e)
            