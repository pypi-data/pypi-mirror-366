import os
os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_az_vm_controller_xethhung12 as project
from j_vault_http_client_xethhung12 import client

import time
def main():
    client.load_to_env()
    tenantId = os.getenv("tenantId")
    clientId = os.getenv("clientId")
    clientSecret = os.getenv("clientSecret")
    subscriptionId = os.getenv("subscriptionId")
    resourceGroupName = os.getenv("resourceGroupName")
    vmName = os.getenv("vmName")
    print(tenantId, clientId, clientSecret, subscriptionId, resourceGroupName, vmName)
    azOAuth = project.AzOAuth(tenantId)
    session = azOAuth.get_session(clientId, clientSecret)
    vm = session.vm(subscriptionId, resourceGroupName, vmName)
    if vm.isVMStopped():
        print("Try power on the machine")
        vm.powerOn()
    while(True):
        time.sleep(5)
        print(vm.instanceState())
        if vm.isVMRunning():
            print("running finally")
            break
        
    time.sleep(10)

    print("stopping machine")
    vm.powerOff()
    while(True):
        time.sleep(5)
        print(vm.instanceState())
        if vm.isVMStopped():
            print("stopped finally")
            break



