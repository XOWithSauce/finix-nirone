#!/usr/bin/env python

import subprocess

def start_pairing_agent():
    
    commands = [
      "sudo btmgmt power off",
      "sudo btmgmt discov on",
      "sudo btmgmt connectable on",
      "sudo btmgmt pairable on",
      "sudo btmgmt power on",
      "bluetoothctl power on",
      "bluetoothctl agent on",
      "bluetoothctl pairable on",
      "bluetoothctl discoverable on"
    ]
    
    for command in commands:
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        print(result.stdout.decode())
        
if __name__ == '__main__':
    start_pairing_agent()
