# Inference

This documentation describes how Raspberry Pi Zero W1.1 can be configured 
to run .tflite Keras Sequential NN

The goal is to expose the input and output tensors via Python IPC Sockets 
much like the Tensorflow Serving gRPC/REST API

## Model compatibility

In order to use a neural network with TFLite Runtime, you must convert the trained model to .tflite file

Example:
```
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)
```

## Getting started on Raspberry Pi

### Install

First install Python 3.7 to have a compatible version for TFLite Runtime Package

```bash
# Essentials
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

# Download, Unpack and Compile Python 3.7
cd ~/Downloads
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz`
sudo tar zxf Python-3.7.0.tgz
cd Python-3.7.0
sudo ./configure --enable-optimizations
sudo make altinstall
```

After the Python 3.7 has compiled you should reboot with `sudo reboot`

Then create a virtual environment for the required python modules and install packages from requirements.txt
```bash
python3 -m venv tfenv
source tfenv/bin/activate
pip install -r requirements.txt
```

### How to use

Now you should be able to run tflite compatible programs from the venv using Python 3.7:

```bash
sudo nano test.py
```

```python
# test.py
import tflite_runtime.interpreter as tflite

model_path = "model.tflite"
interpreter = tflite.Interpreter(model_path)
interpreter.allocate_tensors()

print(interpreter.get_input_details())
print(interpreter.get_output_details())

```

```bash
source tfenv/bin/activate
python3.7 test.py
```

## IPC Socket

The IPC Socket aims to communicate between the 2 main threads running on the device:
The Python 3.9 program main.py that orchestrates
- 1 thread asynchronously handling USB Sensor connection, GPIO Events, Measurements & States, and more...
- 1 thread running the Bluetooth GATT UART Service

IPC Socket reads the measurements made by the Nirone Sensor S2.0
and runs the pre-treated 512 measurement point results to the interpreter
Returning the results as output shape -> [ 0, 0, ...]


The BSD Server runs on startup to create 2 files for sockets
- /tmp/model-ipc-get.socket
- /tmp/model-ipc-post.socket

if BSD_Server fails with an error the socket file has to be deleted, before restarting the socket server.
```bash
sudo rm /tmp/model-ipc-post.socket
```

