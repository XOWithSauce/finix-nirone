## Setup


### nirbt.service
Create a service to start the uart peripheral. This service has to run the bt_agent.py pre-start so that the connection works without issues.
```bash
sudo nano /lib/systemd/system/nirbt.service

[Unit]
Description=NIRScanner Bluetooth UART service
Requires=hciuart.service bluetooth.service
After=multi-user.target bluetooth.target hciuart.target network.target
Wants=multi-user.target
StartLimitIntervalSec=10

[Service]
WorkingDirectory=/home/nirbt/client/src
ExecStartPre=/bin/python3 /home/nirbt/client/src/bt/bt_agent.py
Type=simple
Restart=always
User=nirbt
ExecStart=/bin/python3 /home/nirbt/client/src/main.py

[Install]
WantedBy=multi-user.target
```

### bluetooth.service
Update existing bluetooth service to add flag for --noplugin
```bash
sudo nano /lib/systemd/system/bluetooth.service

[Unit]
Description=Bluetooth service
Documentation=man:bluetoothd(8)
ConditionPathIsDirectory=/sys/class/bluetooth

[Service]
Type=dbus
BusName=org.bluez
ExecStart=/usr/libexec/bluetooth/bluetoothd --noplugin=sap
NotifyAccess=main
#WatchdogSec=10
Restart=on-failure
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
LimitNPROC=1
ProtectHome=true
ProtectSystem=full

[Install]
WantedBy=bluetooth.target
Alias=dbus-org.bluez.service
```

### bthelper@.service
Then update bthelper service and add short sleep before start
```bash
sudo nano /lib/systemd/system/bthelper@.service

[Unit]
Description=Raspberry Pi bluetooth helper
Requires=hciuart.service bluetooth.service
After=hciuart.service
Before=bluetooth.service

[Service]
Type=simple
ExecStart=/bin/sleep 2
ExecStart=/usr/bin/bthelper %I
ExecStartPost=/etc/init.d/bluetooth restart
RemainAfterExit=yes
```

### Finally
Reload after changes
```bash
sudo systemctl daemon-reload
```

Enable the service
```bash
sudo systemctl enable nirbt
```


### DEBUG

To help debug, open these on separate terminal

```bash
bluetootctl
sudo busctl monitor org.bluez
sudo btmon
sudo journalctl -f -u nirbt
```