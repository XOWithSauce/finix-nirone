import serial

class CONF:
    COM_PORT="/dev/ttyACM0"
    BAUD_RATE=115200
    BYTESIZE=serial.EIGHTBITS
    PARITY=serial.PARITY_NONE
    STOPBITS=serial.STOPBITS_ONE
