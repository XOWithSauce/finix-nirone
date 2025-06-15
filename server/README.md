# nirso-server: Proxy API

API designed for handling communication between the nirso-client and Tensorflow Serving server in a subnet. 

## Virtual machine setup
Create a new virtual machine in Microsoft Azure. Preferrably set the username as nirapi to avoid conflicts when configuring systemd files.

VM Specs:
```
Operating system: Linux
Image: Ubuntu Server 20.04 LTS - x64 Gen2
VM architecture: x64
Size: Standard_B1s - 1vcpu - 1GiB memory
OS disk type: Premium SSD
Virtual Network: (VN)
Subnet: (VN Subnet Range)
```
Once you have access to the virtual machine, proceed to with:
```
sudo apt update && sudo apt upgrade -y
sudo apt install nginx -y
```
Configure firewall and confirm that it is active (Status: active):
```
sudo ufw allow "OpenSSH"
sudo ufw allow "Nginx Full"
sudo ufw enable
sudo ufw status
```
(Optional) Change the default (nginx) served website:
```
sudo nano /var/www/html/index.html
```
Get the latest compatible Node.js from https://github.com/nodesource/distributions
```
cd ~
curl -fsSL https://deb.nodesource.com/setup_21.x | sudo -E bash - &&\
sudo apt-get install -y nodejs
```
Confirm that node, npm, npx are succesfully installed:
```
node -v
npm -v
npx -v
```
Now move the repository folder to the virtual machine using SCP or other method.
```
scp -r server machine@12.34.56.78:
```
On the virtual machine, navigate to the server/backend/ directory and install dependencies using:
```
npm i
```
Now create a systemd service to automatically start the Node.js server on startup:
```
sudo nano /lib/systemd/system/nirapi.service
```
```
[Unit]
Description=REST API router
After=network.target

[Service]
Type=simple
User=nirapi
WorkingDirectory=/home/nirapi/server/backend
ExecStart=/usr/bin/node /home/nirapi/server/backend/src/main.js

[Install]
WantedBy=multi-user.target
```
Now reload using:
```
sudo systemctl daemon-reload
```
And start / status / enable the service with:
```
sudo systemctl start nirapi.service
sudo systemctl status nirapi.service
sudo systemctl enable nirapi
```
Configure Nginx reverse proxy:
```
sudo nano /etc/nginx/sites-enabled/default
```
Locate `server_name _;` and under it add:
```
location /api {
	proxy_pass http://localhost:3000/;
}
```
Confirm syntax and reload nginx:
```
sudo nginx -t
sudo nginx -s reload
```
## API Configuration
Before the server can start, you need to make a .env file in the backend directory with following content:
```
PROTOCOL=http
PORT=3000
HOST=127.0.0.1
BASE_HREF=empty
SHARED_KEY=<string>
TF_PROXY_PROTOCOL=http
TF_PROXY_PORT=8001
TF_PROXY_IP=10.0.0.12
TF_PROXY_HREF=/v1/models/resnet:predict
```
#### NOTE:

TF_PROXY address depends on the setup architecture of the virtual network in Microsoft Azure. Remember to confirm the virtual subnet IP Address of the TFS VM and specify the correct port and path used in the server serving your model(s). This example has the default configuration.

The SHARED_KEY Environment value should be 32 characters in length, with a combination of alphabetic characters, numbers and symbols like !, ? and - 

The SHARED_KEY must be equal between the Client Environment and Server Environment.

## Frontend configuration

The frontend directory in server folder contains all files that are designed to be public accessible. These files are meant to communicate with backend, in order to visualize latest measurement predictions and timestamps based on device ID (DID). Do not place any sensitive data or credentials in these files.

Navigate to the frontend directory.

Before you can serve the static webpage with Nginx, you must specify the backend API URL in app.js, so proceed with:
```sudo nano app.js```
Now change the parameter in first lines: `const BASE_URL = "http://example.com/data";`
to match your virtual machine IP Address and proxy route. Example:
```
const BASE_URL = "http://12.34.56.78/api";
```

Start by moving the files to Nginx publicly served files directory:
```
sudo cp app.js /var/www/html/
sudo cp nirso.html /var/www/html/
sudo cp nirso.css /var/www/html/
```

#### NOTE:

Make sure that there are no pre-existing files in /var/www/html/ with the same names as in the frontend directory, as they will be replaced.
After you have moved the files, the static website can be accessed via:
Example (nirso.html): `http://12.34.56.78/nirso.html`

## API Documentation

### Base URL

The base URL for all API requests is:

`http://12.34.56.78/api`
##### NOTE: The Specific IP is the address of the virtual machine.

### Endpoints

### `POST /data`

Returns the predicted label for fabric.

### Parameters

- `data`: Array of 512 floating point measurement values
- `timestamp`: Date and time in UNIX UTC format
- `type`: Character that represents the type of measurement performed
- `id`: Unique identifier that specifies the sender / measurement

### Response:
Returns a JSON object with the following properties:
- `response.text`: Holds the entire response body as a string, after parsed, you can access the following:
	- `outputs`: An array of predicted labels
		- integer: 1 or 0, (true / false) for all predicted labels

### Errors:

1. HTTP Status Code: 400:
- Request packet validation failed:
	- Invalid json parsing
	- Missing headers, or body elements
	- Incorrect or malformed body elements

2. HTTP Status Code: 500:
- Unknown json parsing
- Proxy request failed, Internal server errors from proxy

3. HTTP Status Code: 422:
- Hex conversion failed due to malformed input data

4. HTTP Status Code: 404:
- Not Found


### `POST /data/notify`

Initiates device objects based on the device ID

### Parameters

- `id`: Unique identifier that specifies the sender
- `X-Hmac-Sig`: Header field that is used to verify client

### Response:
Returns a JSON object with the following properties:
- `response.text`: Holds the response of initialization status
	- `msg`: Status of the initialization

### Errors:

1. HTTP Status Code: 400:
- Request packet validation failed:
	- Invalid json parsing
	- Missing headers, or body elements
	- Incorrect or malformed body elements
	- Client HMAC key was invalid

2. HTTP Status Code: 500:
- Initialization of device object failed

3. HTTP Status Code: 200:
- Succesful initialization of Device object


### `GET /data/get-by-did`

GET Route to display latest measurement->prediction status based on device ID, on the public index.html.
Returns latest predicted label and timestamp, based on device id (DID).

### Parameters

- `did`: Integer, has to match an instance of deviceConfig in order to fetch data.

### Response:

Always returns a status code 200 and a JSON object with the following properties:
- `response.text`: 
	- `label`: Latest predicted label from deviceConfig.
		- string: Truncated to length of 10 characters.
		- Optional: "0", incase of errors.
	- `time`: Latest timestamp of prediction from deviceConfig.
		- string: Date and time in UNIX Finland time format.
		- Optional: "0", incase of errors.

### Errors:

1. Route has 2 layers for error handling:
	- Errors that might result in label & time being displayed as 0:
		* Failed to parse integer from req.query.did
		* Requested DID does not match any deviceConfig instance DID
		* Failed to run get methods for deviceConfig
		* Other unknown errors in try-catch block
	- HTTP Status Codes
		* 400: Input validation failed
		* 500: Input validation had an error in try-catch block

### `GET /data/get-devices`

GET Route to fetch statistics of the currently online devices
Returns a dictionary that contains count and array of ids.

### Parameters

- None

### Response:

Always returns a status code 200 and a JSON object with the following properties:
- `response.text`: 
	- `count`: Amount of devices online
		- integer: Amount of devices in map.
		- Optional: 0, incase of errors.
	- `ids`: An array of integers, Device IDs
		- integer: Device ID
		- Optional: "0", incase of errors.

## Tests

To run all tests (except proxy), run `npm run test`

Note: .env file must be present and filled with correct values
