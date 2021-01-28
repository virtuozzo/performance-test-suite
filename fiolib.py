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

import os
import glob
import uuid
import time
import configparser
from testutils import systemExec
from vmtestlib import Testvm

CONFIG_FILE_ENDING = ".fio"
CONFIG_FILE_DIR = "/fio/"

class FioConfig():
    def __init__(self, file_path=None):
        self.file_path = str(file_path)
        self.cfg = configparser.ConfigParser()
        self.cfg.add_section("global")

    def read_file(self, file_path):
        self.cfg.read(file_path)
    
    def write_file(self, file_path):
        with open(file_path, "w") as configfile:
            self.cfg.write(configfile, space_around_delimiters=False)
    
    def write(self):
        with open(self.file_path, "w") as configfile:
            self.cfg.write(configfile, space_around_delimiters=False)
    
    def read(self):
        self.cfg.read(self.file_path)

    def add_job(self, job_name, params={}):
        self.cfg.read_dict({job_name:params})

    def __str__(self):
        result = ""
        for section in self.cfg:
            if str(section).startswith("DEFAULT"):
                continue

            result += "[" + str(section) +"]\n"
            for item in self.cfg[section]:
                result += " " * 4 + str(item) + "=" + str(self.cfg[section][item]) + "\n"
        
        return result

    def delete_file(self):
        systemExec(["rm", "-f", self.file_path])

class Fio:
    def __init__(self, test_device="/dev/zero"):
        self.conf_dir = str(os.path.dirname(__file__)) + CONFIG_FILE_DIR
        self.test_device = test_device
        self.test_uuid = str(uuid.uuid4().hex)

    def list_configs(self):
        return list(map(lambda x: os.path.basename(x)[:-4], glob.glob("%s*%s" % (self.conf_dir, CONFIG_FILE_ENDING)))) 

    def get_config(self, config_name):
        config_path = self.conf_dir + str(config_name) + CONFIG_FILE_ENDING
        if os.path.exists(config_path):
            result = FioConfig(config_path)
            result.read()
            return result

        return None

    def prepare_config(self, config_name, dev=None):
        config = self.get_config(config_name)
        if config is None:
            print("Trying to run not existen Test sequence %s" % str(config_name))
            return None

        if dev is None:
            dev = str(self.test_device)

        if "global" in config.cfg:
            config.cfg.set("global", "filename", dev)
        else:
            print("Warning no global section in config can not use specified device %s" % dev)

        tmp_config_path = self.conf_dir + self.test_uuid + CONFIG_FILE_ENDING
        config.write_file(tmp_config_path)
        return tmp_config_path

    def run_test(self, config_name):
        tmp_config_path = self.prepare_config(config_name)
        if tmp_config_path is None:
            return None, None

        out, err =  systemExec(["fio", tmp_config_path, "--output-format=json"])
        systemExec(["rm", "-f", tmp_config_path])
        return out, err
    
    def run_test_config(self, config):
        try:
            tmp_config_path = self.conf_dir + self.test_uuid + CONFIG_FILE_ENDING
            config.write_file(tmp_config_path)
        except Exception as e:
            return None, ("Failed to write tmp config Exception %s" % str(e))

        out, err =  systemExec(["fio", tmp_config_path, "--output-format=json"])
        systemExec(["rm", "-f", tmp_config_path])
        return out, err

    def run_test_at_vm(self, config_name, vm):
        vm = Testvm(test_dev_name=str(self.test_device))
        vm.start()
        tmp_config_path = self.prepare_config(config_name, dev=vm.get_dev_name_inside_vm())
        if tmp_config_path is None:
            return None

        remote_config_path = "/root/" + os.path.basename(tmp_config_path)
        vm.send_file(tmp_config_path, remote_config_path)
        out, err = vm.run_command("fio %s --output-format=json" % remote_config_path)
        systemExec(["rm", "-f", tmp_config_path])
        return out, err

    def get_result_file_path(self, config_name="fio"):
        return str(os.path.dirname(__file__)) + "/" + config_name + time.strftime("%Y%m%d-%H%M%S") +\
            self.test_uuid + ".result"
    
    def add_config(self, config_name, params, writefile=True):
        config_path = self.conf_dir + str(config_name) + CONFIG_FILE_ENDING
        if os.path.exists(config_path):
            self.del_config(config_name)
        
        config = FioConfig(config_path)
        config.add_job(config_name, params)
        if writefile:
            config.write()

        return config

    def del_config(self, config_name):
        config = self.get_config(config_name)
        if config is None:
            return

        config.delete_file()