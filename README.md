# NIRSO

## Purpose

Identify textile materials based on measurements with a portable handheld device.

> **Client** in this case refers to a single embedded device, which takes NIR measurements from the real objects. </br>
> [Client documentation](client/README.md)
- Designed for Raspberry Pi Zero W1.1 Microcontroller
- Connected with a Nirone S2.0 Spectrometer
- Independent Python program that monitors for button presses, configuration changes and other asynchronous tasks.
- Installation instructions and example configuration

> **Server** or backend in this case takes the measurements and uses given algorithms to detect material. </br>
> [Server documentation](server/README.md)
- Code for frontend (statically hosted website) and backend (js routing and proxy config)
- Configuration instructions
- Instructions for Tensorflow Serving hosting on cloud services
  
> **Model** covers the aspects of training the Sequential neural network, interpretation of its details, and exporting the model. </br>
> [Model documentation](model/README.md)
- Jupyter Notebook files used in creating a small model which predicts 3 textile materials based on the input features
- Designed for data obtained using a Nirone S2.0 Spectrometer
- No dataset provided, but .gitkeep empty data folder should be filled with appropriate data

> **Android** goes into detail about development of Android compatible application that can communicate with Client. </br>
> [Anrdoid documentation](android/README.md)
- Based on Android Open Source samples
- Retrofitted to have a polling based Bluetooth communication with a compatible GATT server
