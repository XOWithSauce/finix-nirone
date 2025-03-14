import sys
import os
import asyncio

import dbus, dbus.mainloop.glib
from gi.repository import GLib
from bt.bt_adv import Advertisement
from bt.bt_adv import register_ad_cb, register_ad_error_cb
from bt.bt_gatt import Service, Characteristic
from bt.bt_gatt import register_service_cb, register_service_error_cb
from event_manager import EventManager

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '00002222-0000-1000-8000-00805f9b34fb'
UART_RX_CHARACTERISTIC_UUID =  '00001111-0000-1000-8000-00805f9b34fb'
UART_TX_CHARACTERISTIC_UUID =  '00001112-0000-1000-8000-00805f9b34fb'
LOCAL_NAME =                   'rpi-gatt-server'
mainloop = None

class TxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        # Only support for notify actions, no r / w
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        # Watch for device console input
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)

    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True

    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        # Write value into the 
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False

class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service, event_manager: EventManager):
        self.event_manager = event_manager
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write', 'read', 'notify'], service)

    # Write to Server Characteristic interface with mobile app
    # This function Reads Value (message) that client sent
    def WriteValue(self, value, options):
        data_string = ''.join([chr(b) for b in value])
        print(f"UART RX: {data_string}")
        self.event_manager.messager(data_string)
        
    # Read Characteristics button Interface with mobile app
    # This Sends to Client
    def ReadValue(self, options):
        print("Client reading characteristic: ", self.event_manager.uart_rx_reader_field)
        return self.event_manager.uart_rx_reader_field
    
    
class UartService(Service):
    def __init__(self, bus, index, event_manager):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self, event_manager))

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response

class UartApplication(Application):
    def __init__(self, bus, event_manager):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0, event_manager))
        self.agent_path = '/com/example/agent'
        self.agent_capability = 'KeyboardDisplay'

    @dbus.service.method(DBUS_OM_IFACE, in_signature='os', out_signature='')
    def RequestConfirmation(self, device_path, passkey):
        print('RequestConfirmation:', device_path, passkey)
        agent = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, self.agent_path),
                               'org.bluez.Agent1')
        agent.ConfirmModeChange(True)

    @dbus.service.method(DBUS_OM_IFACE, in_signature='o', out_signature='s')
    def RequestPinCode(self, device_path):
        print('RequestPinCode:', device_path)
        return '0000'

    @dbus.service.method(DBUS_OM_IFACE, in_signature='ou', out_signature='')
    def AuthorizeService(self, device_path, uuid):
        print('AuthorizeService:', device_path, uuid)
        agent = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, self.agent_path),
                               'org.bluez.Agent1')
        agent.ConfirmModeChange(True)

class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.local_name = LOCAL_NAME
        self.include_tx_power = True

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    try:
        objects = remote_om.GetManagedObjects()
        for o, props in objects.items():
            if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
                return o
    except:
        pass
    return None
    

async def uart_main(event_manager: EventManager):
    global mainloop
    mainloop = GLib.MainLoop()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    if not adapter:
        print('BLE adapter not found')
        return
    print("Adapter: ", adapter)
    
    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    app = UartApplication(bus, event_manager)
    adv = UartAdvertisement(bus, 0)

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_service_cb,
                                        error_handler=register_service_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)
    
    agent_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, '/org/bluez'),
        'org.bluez.AgentManager1'
    )
    agent_manager.RegisterAgent(app.agent_path, app.agent_capability)
    agent_manager.RequestDefaultAgent(app.agent_path)
    try:
        mainloop.run()
    except KeyboardInterrupt:
        adv.Release()
