import asyncio
import serial
from copy import deepcopy
import struct

class SerialDevice():

    def __init__(self, event_manager) -> None:
        self.event_manager = event_manager
        self.received_data: asyncio.Queue
        self.send_measurement: asyncio.Event
        self.data_queue = []
        self.measurement_points: list[float]
        self.sensor_temp: str = "0"
        self.ser: serial.Serial
        self.serial_init()
        self.CMDS = {
            "Sensor Type": "h0\r",
            "Hardware Version": "h1\r",
            "Serial Number": "h2\r",
            "Minimum Wavelength": "h3\r",
            "Maximum Wavelength": "h4\r",
            "Firmware Version (?)": "i\r",
            "Number Of Wavelengths": "m\r",
            "Measurement Time 1": "E0\r",
            "Measurement Time 2": "E1\r",
            "Measurement Time 3": "E2\r",
            "Light Source Power Level 0": "LI0\r",
            "Light Source Power Level 100": "LI100\r",
            "Light Source Warm-Up Time": "Lt\r",
            "Automatic Dark Value": "Pa\r",
            "Dark Subtraction Value": "Pb\r",
            "Divide Value": "Pc\r",
            "Log Value": "Pd\r",
            "Scaling Function Value": "Pe\r",
            "Smoothing Function Value, Parameter Value": "Pf\r",
            "Derivative Order Value": "Pg\r",
            "PLS Mode Value": "Pi\r",
            "Slope Value, Bias Value": "Pj\r",
            "Default": "Pn\r",
            "Index Value, Coefficient Value": "Px\r",
            "PLS Offset Value": "Po\r",
            "Save Parameters To Index": "PS{index}\r",
            "Load Parameters From Index": "PL{index}\r",
            "Load Default Parameters": "PR\r",
            "Measurement Ready": "XM\r",
            "Result Value": "Xp\r",
            "Temperature Value": "St\r",
            "Current1 (mA), Current2 (mA)": "Sc\r",
            "Set Secondary I2C Address (Hex)": "A{address}\r",
            "Get Secondary I2C Address or Disabled Value": "a\r",
            "Get Measurement Float Values": "Xm0,{datalength}\r",
            "Set Measurement on Wavelength": "W0,{wavelength}\r",
        }
        pass
        
    async def shared_objects(self, queue: asyncio.Queue, event: asyncio.Event) -> None:
        self.received_data = queue
        self.send_measurement = event
        return None

    def write_command(self, cmd: str) -> None:
        for byte in cmd.encode():
            self.ser.write(byte.to_bytes(1, byteorder='big', signed=True))
            if byte == ord('\r'):
                break

    def read_response(self) -> None:
        while True:
            byte = self.ser.read(1)
            if byte == b'\r':
                break
            elif byte != b'\n':
                pass
        return None

    def measure_get(self) -> None:
        while self.ser.in_waiting != 0:
            self.ser.read(1)
            pass
        data_vec = []
        ba = bytearray()
        total_bytes_to_read = 2048
        sensor_data = self.ser.read(1)
        while len(ba) < total_bytes_to_read:
            ba.extend(sensor_data)
            del sensor_data
            sensor_data = self.ser.read(1)
        for i in range(0, len(ba)-3, 4):
            float_value = struct.unpack('<f', ba[i:i+4])[0]
            data_vec.append(float_value)
        if len(data_vec) == 512:
            self.received_data.put_nowait(deepcopy(data_vec))
            data_vec.clear()
        return None

    def serial_init(self) -> None:
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyACM0"
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 2
        self.ser.xonxoff = False
        self.ser.dsrdtr = False
        self.ser.rtscts = False
        self.ser.dtr = True
        self.ser.rts = True
        try:
            self.ser.open()
            self.sensor_wl_read(self.ser, 512, 1550.0, 1950.0)
        except:
            print("Failed to open serial port.")
        return None

    def sensor_wl_read(self, ser: serial.Serial, measurement_count: int, min_wl: float, max_wl: float) -> None:
        measurement_points = []
        cmd = ""
        current_wl = min_wl
        gap = (max_wl - min_wl) / (measurement_count - 1)
        for i in range(measurement_count - 1):
            cmd = "W{0},{1:.1f}\r".format(i, current_wl)
            self.write_command(cmd)
            measurement_points.append(current_wl)
            current_wl += gap
            self.read_response()
        cmd = "W{0},{1:.1f}\r".format(measurement_count - 1, max_wl)
        self.write_command(cmd)
        self.read_response()
        measurement_points.append(max_wl)
        self.measurement_points = measurement_points
        return None

    def serial_flush(self):
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        while self.ser.in_waiting != 0:
            self.ser.read(1)
    
    async def measure(self, type: str) -> bool:
        try:
            print("STARTING MEAS")
            if not type == "b":
                cmd = "LI100\n" #turn on lamp
                self.write_command(cmd)
                self.read_response()
                self.serial_flush()
                print("LAMP ON!")
            cmd = "XM\n"
            self.write_command(cmd)
            self.read_response()
            self.serial_flush()
            print("MEAS READY!")
            cmd = "Xm0,512\n"
            self.write_command(cmd)
            print("READ READY!")
            self.measure_get()
            self.serial_flush()
            print("READ DONE")
            self.send_measurement.set()
            if not type == "b":
                cmd = "LI0\n"
                self.write_command(cmd)
                self.read_response()
                self.serial_flush()
                print("LAMP OFF!")
        except Exception as e:
            print("SerialDevice class had an exception at method measure(): \n",e)
            pass
        finally:
            # Update sensor temperature
            self.get_sensor_temp()
            pass
        return True
    
    def get_sensor_temp(self):
        if (self.ser.is_open):
            print("RETURNING SER TEMP")
            ba = bytearray()
            result = ""
            try:
                cmd = self.CMDS["Temperature Value"]
                self.write_command(cmd)
                while True:
                    byte = self.ser.read(1)
                    ba.extend(byte)
                    if byte == b'\r':
                        break
                    elif byte != b'\n':
                        pass
                result = ba.decode("utf-8")
                print("RESULT: ", result)
                temperature_str = result.split(":")[1].strip()
                try:
                    # Try parsing as float first
                    temperature_value = int(float(temperature_str))
                except ValueError:
                    # If parsing as float fails, remove scientific notation (e.g., "3.20e+01") and convert to int
                    temperature_value = int(temperature_str.split("e")[0])
                print("PARSED TEMP: ", str(temperature_value))
                self.sensor_temp = str(temperature_value)
                self.serial_flush()
            except Exception as e:
                print("SerialDevice class had an exception at method measure(): \n",e)
                self.sensor_temp = "err"
                pass
        return