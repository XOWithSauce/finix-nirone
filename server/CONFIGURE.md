## Info
This document describes the needed infrastructure on Microsoft Azure services for Tensorflow Serving VM and nirso-server Proxy API. The goal is to isolate Tensorflow Serving VM from public internet and only allow access to the served models from nirso-server on a specified port on the subnet.

This document does not go into detail about the creation of nirso-server VM (can be found from server directory), but covers the creation and configuration of Tensorflow Serving VM and Microsoft Azure Infrastructure.
##


### How to interpret
For now, we will use nirso-server as the name of the virtual machine delegated to the nirso-server proxy API Linux machine and we will use the name TFServingVM as the name for the virtual machine (bitnami packaged Tensorflow Serving) that serves models. We will call the Virtual Network NIR-API. Publicfacing subnet will mean, that it should / can be accessed from public network, and this will be assigned to the nirso-server in order to allow access from nirso-client. TFS subnet will be a subnet address space delegated for TFServingVM.
These names can vary depending on your naming conventions, but make sure that the subnets and security groups are correctly assigned to each individual machine.

### Virtual Network (NIR-API)
Setup the address space for the Virtual Network, make sure that it has space for two subnets.
```
Address space            Address range                Address count
10.0.0.0/28              10.0.0.0 - 10.0.0.15         16
```

Setup a Virtual network with the following subnets:
```
Name            IPv4          IPv6   Available IPs    Security group
publicfacing    10.0.0.0/29   -      2                nirso-server-nsg
TFS             10.0.0.8/29   -      2                TFServingVM-nsg
```

### Tensorflow Serving Virtual Machine
We will use the bitnami packaged version of Tensorflow Serving for this virtual machine.

Create a new virtual machine in Microsoft Azure. Preferrably set the Virtual Machine Name as TFServingVM to avoid conflicts and confusion while following the documentation. Remember to attach this virtual machine to the same resource group as nirso-server.

VM Specs:
```
Operating system: Linux
Image: Bitnami package for TensorFlow Serving - x64 Gen1
VM architecture: x64
Size: Standard_B1s - 1vcpu - 1GiB memory
OS disk type: Premium SSD
Virtual Network: NIR-API
Subnet: TFS
```

After you have created the virtual machine and have logged into it using SSH or other method, proceed with updating:
```
sudo apt update && sudo apt upgrade -y
```

For this repository to work, you will need to change the default served model to your desired MLL / NN.

To do this, proceed with removing the default ResNet model from the machine:
```
sudo rm -rf /opt/bitnami/model-data/1538687457/variables
sudo rm -rf /opt/bitnami/model-data/1538687457/saved_model.pb
```
Now move / replace those with your desired files. You must have downloaded / transferred your variables folder and saved_model.pb to the virtual machine. To get these files, see the model directory and familiarize yourself with model exporting with Jupyter Notebook.

Run the following commands from the same directory as your files. 
```
sudo mv saved_model.pb /opt/bitnami/model-data/1538687457/
sudo mv variables /opt/bitnami/model-data/1538687457/
```

To start the tensorflow-serving model server, you can use:
```
sudo opt/bitnami/tensorflow-serving/bin/tensorflow_model_server --rest_api_port=8001 --model_name=resnet --model_base_path=/opt/bitnami/model-data
Or sometimes if the command has been compiled + configured, you dont have to specify path:
tensorflow_model_server --rest_api_port=8001 --model_name=resnet --model_base_path=/opt/bitnami/model-data
```

### TFServingVM-nsg
You will need to have created the TFServingVM and nirso-server by now. Make sure that you have assigned the TFServingVM to TFS. Now navigate yourself to the TFServingVM Overview and select "Properties". Look for the tab "Networking" and find the "Private IP Address". This Address will be your "Destination", we will call this TFS-PIP. Do the same for nirso-server, this address will be your "Source", we will call this NS-PIP.

Configure the Tensorflow Serving virtual machine network security group, to only allow connections from the publicfacing subnet.

The port 8001 is the Tensorflow Serving HTTP REST API Port which we will allow to be accessed from nirso-server. Make sure that Priority takes precedence over any other blocking inbound rule.
```
Inbound Security Rules
Priority    Name              Port     Protocol    Source     Destination    Action
1000        TfApiPortAllow    8001     TCP         NS-PIP     TFS-PIP        Allow
```
