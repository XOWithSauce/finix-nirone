import struct
from serial import Serial, tools
from conf import CONF
from time import sleep
import time
import serial.tools.list_ports # Needs to be implicitly imported
import asyncio
CMDS = {
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

def write_command(ser: Serial, cmd: str) -> None:
    # Convert the command string to a bytearray
    cmd_bytes = bytes(cmd, "utf-8")
    ser.write(cmd_bytes)
    if cmd_bytes.find(b"\r") < 0:
        pass
    else:
        ser.write(b"\r")

    return None

def read_response(ser: Serial, btBbt: bool, output: bool) -> str:
    """
    Reads the response from the serial port.

    Args:
        ser (serial.Serial): The serial port object.
        btBbt (bool): True for Byte by Byte printing, False (default) for no Byte by Byte printing
        output (bool): True for output printing, False for no output

    Returns:
        str: The received data from the serial port.
    """
    dataBuffer: str = ""
    while True:
        byte = ser.read(1)
        if byte == b'\r':
            break
        elif byte != b'\n':
            try:
                dataBuffer += byte.decode(errors='ignore')
                if btBbt:
                    print(f"Received byte: {byte.decode()}")
            except UnicodeDecodeError:
                pass
    if output:
        print(f"Received data: {dataBuffer}")
    return dataBuffer

def serialFlush(ser: Serial, IO: bool) -> None:
    if IO:
        ser.reset_output_buffer()
    else:
        ser.reset_input_buffer()
    return None

def sensorMeasureWavelengths(ser: Serial, measurement_count: int, min_wl: float, max_wl: float):
    """
    Performs wavelength measurements.
    Args:
        ser (serial.Serial): The serial connection object. (Nirone)
        measurement_count (int): The number of measurements to perform.
        min_wl (float): The minimum wavelength.
        max_wl (float): The maximum wavelength.
    Returns:
        list: A list of measurement points.
    Raises:
        ValueError: If the minimum wavelength is larger than the maximum wavelength.
    """
    cmd = ""
    current_wl = min_wl
    if min_wl > max_wl:
        raise Exception("Error: MinWL is larger than MaxWL")
    gap = (max_wl - min_wl) / (measurement_count - 1)
    # Sending commands from index 0 to measurement_count-1
    for i in range(measurement_count):
        # Command format: "W0,123.0"
        cmd = "W{0},{1:.1f}\r".format(i, current_wl)
        write_command(ser, cmd)
        current_wl += gap
        # Reading command response
        ser.readline()

    # Sending the final command # FIXME why -1?
    cmd = "W{0},{1:.1f}\r".format(measurement_count - 1, max_wl)
    write_command(ser, cmd)
    ser.readline()
    return

def measureGet(ser, verbose: bool) -> list:
    data_vec: list = []
    sensor_data = ser.read(128)
    # FIRST BYTE ISSUE 0a CONVERTED TO 43
    hexdump = sensor_data.hex()
    index = hexdump.find("0a")
    if index != -1:
        hexdump = hexdump[:index] + "43" + hexdump[index + 2:]
    sensor_data = bytes.fromhex(hexdump)
    while sensor_data:
        if verbose:
            print(f"{len(sensor_data)} bytes read")
            print(f"Hexdump of data received from sensor: {sensor_data.hex()}")
        for i in range(0, len(sensor_data) - 3, 4):
            float_value = struct.unpack('>f', sensor_data[i:i+4])[0]
            data_vec.append(float_value)
        # Check if data_vec contains the expected number of elements (2048/4 = 512)
        # modulo 512?
        if len(data_vec) >= 512:
            break
        sensor_data = ser.read(128)
    return data_vec

def connectNIR() -> Serial:
    """
    Initializes the serial connection and returns the serial port object.

    Returns:
        serial.Serial: The initialized serial port object.
    """
    # Get the list of available serial ports
    com_ports = tools.list_ports.comports()
    for port, description, _ in com_ports:
        print(f"Port: {port} Description: {description}")
    # Initialize the serial port with the specified settings
    connection = Serial(
        port=CONF.COM_PORT,
        baudrate=CONF.BAUD_RATE,
        bytesize=CONF.BYTESIZE,
        parity=CONF.PARITY,
        stopbits=CONF.STOPBITS,
        timeout=1,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    # Delay for a short period to allow the serial port to initialize
    sleep(1)
    # TODO confirm with serial command test: echo <=> reply
    return connection
