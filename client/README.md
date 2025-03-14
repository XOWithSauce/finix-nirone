# nirso-client: Sensor data collection and textile prediction

Embedded program for Raspberry Pi Zero that collects and sends Nirone sensor data to an API or Local inference neural network.

## Description:

This embedded program for Raspberry Pi Zero collects and sends Nirone S2.0 sensor data to an API using a single thread. It uses asynchronous programming to efficiently manage sensor readings, network communication, and button events. It exposes a bluetooth service that allows the user to operate the device using NIRScanner Android application. The program also features a separate thread for IPC Socket handling and .tflite neural network inference.

## Getting started

### Dependencies

```
sudo apt update && apt upgrade -y

sudo apt install python3-gi
```

```
Raspberry Pi Zero W 1.1
Linux 6.1.21+ armv6l
Distributor ID: Raspbian
Description:    Raspbian GNU/Linux 11 (bullseye)
Release:        11
Codename:       bullseye
Python Version: Python 3.9.2
```

### Installation

1. Copy the files to your Raspberry Pi's filesystem.
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies:
```bash
pip install -r requirements.txt
```
3. If missing, create / modify parameters in the .env file to match specifications.
    - NOTE: The SHARED_KEY Environment value should be 32 characters in length, with a combination of alphabetic characters, numbers and symbols like !, ? and -. The SHARED_KEY must be equal between the Client Environment and Server Environment.
    - NOTE: The SHARED_SIGN_KEY and SHARED_DECR_KEY Environment value should be 32 characters in length, with a combination alphabetic characters. The values must be equal between the Client Environment and the Android Application Build Properties. These are used in Encryption of BLE Communication

4. To Enable local inference with .tflite neural network, see -> [Inference documentation](client/src/inference/README.md) , for instructions on how to install.

### Usage

1. Power on the device.
2. Take a fully lambertadian sample, using the white side cover the lens and perform white reference measurement
3. Then cover the lens using the other side (black) of the sample and perform the background radiation reference measurement
4. Take a fabric of your choosing and perform the normal measurement. Results should appear in the Android application (if connected).

## Bluetooth

The program operates a Bluetooth UART Service with exposed Rx Characteristic that has write and read permission. 
This is used to communicate between the android device and Raspberry to toggle reference measurements, read sensor temp., and fetch prediction results.
In order to have the Bluetooth service work correctly, you must configure systemd services.

For detailed information about the Bluetooth functionality, refer to the dedicated Bluetooth documentation.
### [Bluetooth documentation](src/bt/README.md)

## TFLite

Enabling Local Inference with TFLite Neural Network

This program optionally supports on-device inference using a TFLite neural network model. Local inference allows the Raspberry Pi to process sensor data directly, potentially reducing reliance on an external server and improving responsiveness.

For detailed instructions on setting up local inference, including TFLite runtime installation, model conversion, and IPC socket communication, refer to the dedicated documentation.
### [Inference documentation](src/inference/README.md).
