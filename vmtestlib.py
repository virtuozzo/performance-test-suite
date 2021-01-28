#!/usr/bin/python3

# MIT License
# 
# Copyright (c) 2020 Andrii Melnyk andriy.melnyk@onapp.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# builds VM with given parameters RAM, VCPU, bridge name...
# Use stored image with preinstaled static test binnaries

import os
import time
import glob
import uuid
import xml.etree.ElementTree as ET
from testutils import systemExec

BRIDGE_NAME="testbridge"

class Testvm:
    def __init__(self, test_dev_name="/dev/zero", ram_size="1024000", vcpu_count="1", vm_ip="10.201.133.2",
        bridge_ip="10.201.133.1", timeout=60, dev_name_inside_vm="vda"):

        self.vm_uuid = uuid.uuid4()
        self.dev_name = test_dev_name
        self.ram_size = ram_size
        self.vcpu_count = vcpu_count
        self.vm_ip = vm_ip
        self.bridge_ip = bridge_ip
        self.timeout = timeout
        self.dev_name_inside_vm = dev_name_inside_vm

    def get_defult_config(self):
        self.vm_config_tree = ET.parse(os.path.dirname(__file__) + "/fio/default.xml")
        return self.vm_config_tree.getroot()


    def write_config(self):
        self.vm_config_tree.write(str(self.config_path))
    
    def get_vm_name(self):
        return str(self.vm_uuid.hex[:10].lower())
    
    def get_dev_name_inside_vm(self):
        return "/dev/" + self.dev_name_inside_vm
    
    def setup_network(self):
        bridges = {}
        try:
            paths = glob.glob("/sys/class/net/*/bridge")
            for path in paths:
                key = path.split('/')[4]
                val = []
                intfs = glob.glob('/sys/class/net/%s/brif/*' % key)
                for intf in intfs:
                    intf = os.path.basename(intf)
                    val.append(intf)
                bridges[key] = val
        except Exception as e:
            print("Failed to list bridges Exception %s" % str(e))
        
        if BRIDGE_NAME not in bridges:
            print("Add bridge %s" % BRIDGE_NAME)
            systemExec(["brctl", "addbr", BRIDGE_NAME])
        
        systemExec(["brctl", "stp", BRIDGE_NAME, "off"])
        systemExec(["ifconfig", BRIDGE_NAME, self.bridge_ip, "netmask", "255.255.255.0"])
        systemExec(["ifconfig", BRIDGE_NAME, "up"])
        # Before adding conntrack entry to ignore traffic, delete existing one
        systemExec(["iptables", "-t", "raw", "-D", "PREROUTING", "-i", BRIDGE_NAME, "-j", "NOTRACK"])
        systemExec(["iptables", "-t", "raw", "-D", "OUTPUT", "-o", BRIDGE_NAME, "-j", "NOTRACK"])
        # Tell conntrack to ignore traffic on this subnet
        systemExec(["iptables", "-t", "raw", "-A", "PREROUTING", "-i", BRIDGE_NAME, "-j", "NOTRACK"])
        systemExec(["iptables", "-t", "raw", "-A", "OUTPUT", "-o", BRIDGE_NAME, "-j", "NOTRACK"])

    def generate_vm_config(self, config_path=None):
        if config_path is None:
            vm_config = self.get_defult_config()
        else:
            self.vm_config_tree = ET.parse(config_path)
            vm_config = self.vm_config_tree.getroot()

        for ud in vm_config.findall('uuid'):
            ud.text = str(self.vm_uuid)

        for name in vm_config.findall('name'):
            name.text = self.get_vm_name()
        
        for memory in vm_config.findall('memory'):
            memory.text = self.ram_size

        for vcpu in vm_config.findall('vcpu'):
            vcpu.text = self.vcpu_count

        base_dir = os.path.dirname(__file__)
        cmdline_string = "rootfstype=ramfs selinux=0 dbsize=128 ip_address=%s netmask=255.255.255.0 gw=%s mtu=9000\
            channel=224.3.28.4 unicastmode=0 hostid=1 controller_mode=B console=ttyS0" % (str(self.vm_ip), str(self.bridge_ip))
        for os_elem in vm_config.findall('os'):
            for kernel in os_elem.findall('kernel'):
                kernel.text = str(base_dir + "/fio/vmlinuz-kvm")
            
            for initrd in os_elem.findall('initrd'):
                initrd.text = str(base_dir + "/fio/testinitrd.img")
    
            for cmdline in os_elem.findall('cmdline'):
                cmdline.text = str(cmdline_string)

        new_mac = "02:00:00:%s:%s:%s" % (self.vm_uuid.hex[:2], self.vm_uuid.hex[2:4], self.vm_uuid.hex[4:6])
        for devices in vm_config.findall('devices'):
            for interface in devices.findall('interface'):
                for mac in interface.findall('mac'):
                    mac.set("address", new_mac)
                
                for target in interface.findall('target'):
                    target.set("dev", self.get_vm_name())
                
                for source in interface.findall('source'):
                    source.set("bridge", BRIDGE_NAME)

            for disk in devices.findall('disk'):
                for source in disk.findall('source'):
                    source.set("dev", self.dev_name)
                
                for target in disk.findall('target'):
                    target.set("dev", self.dev_name_inside_vm)
                    
        self.config_path = "%s/fio/%s.xml" % (base_dir, self.get_vm_name())
        #print("\n%s\n" % ET.dump(vm_config))
        self.write_config()

    def run_command(self, cmd, verbouse=False):
        out, err = systemExec(["ssh", "-oStrictHostKeyChecking=no ", "-oHostKeyAlgorithms=+ssh-dss",
            "root@" + str(self.vm_ip), cmd], verbouse=verbouse)

        return out, err

    def send_file(self, local_file, remote_file=None, verbouse=False):
        if remote_file is None:
            remote_file = local_file

        systemExec(['scp', "-oHostKeyAlgorithms=+ssh-dss", "-oStrictHostKeyChecking=no", str(local_file),
            "root@%s:/%s" % (str(self.vm_ip), str(remote_file))], verbouse=verbouse)

    def start(self, vm_config_path=None):
        self.setup_network()
        self.generate_vm_config(vm_config_path)

        systemExec(["virsh", "define", self.config_path])
        systemExec(["virsh", "start", self.get_vm_name()])
        timeout = self.timeout
        while(timeout > 0):
            out, _ = self.run_command("echo 1")
            if out is not None and out.startswith("1"):
                print("VM %s Booted" % self.get_vm_name())
                break

            timeout-=1
            time.sleep(1)
    
    def stop(self):
        systemExec(["virsh", "destroy", self.get_vm_name()])

    def __del__(self):
        systemExec(["virsh", "destroy", self.get_vm_name()])
        systemExec(["virsh", "undefine", self.get_vm_name()])
        systemExec(["rm", "-f", self.config_path])