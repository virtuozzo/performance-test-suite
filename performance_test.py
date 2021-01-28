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

import sys
import json
from testutils import DEFULT_LOGGER
from fiolib import Fio

def print_help_exit():
    print("Options:\n"\
        "list - list all fio tests available for run (stored in fio folder with .fio ending)\n"\
        "show <test name> - show fio test configuration by name (stored in fio folder with .fio ending)\n"\
        "runlocal <test name> dev=<block device path> [output=<filename>] - run test at block device at current device\n"\
        "run <test name> dev=<block device path> [output=<filename>]- run test at block device at VM\n"\
        "add <test name> params=[] - add test to lib\n"\
        "del <test name> - delete test from lib\n"\
        "runcustom <test name> params=[] - run test with params without adding to lib\n")
    sys.exit(0)

def list_tests():
    fio_obj = Fio()
    print("Tests :\n")
    for test in fio_obj.list_configs():
        print(str(test))

def show_test(seq):
    fio_obj = Fio()
    cfg = fio_obj.get_config(seq)
    print("Test:\n")
    print(str(cfg))

def run_test(args_dict, local=True):
    if len(args_dict) < 4 or len(str(args_dict[3]).split("=")) < 2:
        print_help_exit()
    
    sequence = str(args_dict[2])
    dev = str(args_dict[3]).split("=")[1]
    print("Start performance testing")
    fio_obj = Fio(dev)
    result, err = fio_obj.run_test(sequence) if local else fio_obj.run_test_at_vm(sequence, dev)
    if result is None:
        print("FIO error %s" % str(err))
        return

    if len(args_dict) > 4:
        result_file =  str(args_dict[4]).split("=")[1]
        with open(result_file, "w+") as file_result:
            file_result.write(result)

    result_json = json.loads('{"result":"FAILURE"}')
    try:
        result_json = json.loads(result)
        read_bw = str(result_json["jobs"][0]["read"]["bw"])
        read_iops = str(int(round(float(result_json["jobs"][0]["read"]["iops"]))))
        read_lat = str(int(round(float(result_json["jobs"][0]["read"]["lat_ns"]["mean"]))))
        print("read: bw %s KiB/s lat %s ns iops %s" % (read_bw, read_lat, read_iops))
        write_bw = str(result_json["jobs"][0]["write"]["bw"])
        write_iops = str(int(round(float(result_json["jobs"][0]["write"]["iops"]))))
        write_lat = str(int(round(float(result_json["jobs"][0]["write"]["lat_ns"]["mean"]))))
        print("write: bw %s KiB/s lat %s ns iops %s" % (write_bw, write_lat, write_iops))
    except Exception as e:
        print("Failed to parse fio output %s Exception %s" % (str(result), str(e)))

    print("End performance testing")
    return result_json

def del_test(seq):
    fio_obj = Fio()
    fio_obj.del_config(seq)
    print("Test %s deleted\n" % str(seq))

def add_test(args_dict):
    if len(args_dict) < 4 or len(str(args_dict[3]).split("=")) < 2:
        print_help_exit()

    test_name = str(args_dict[2])
    fio_obj = Fio()
    try:
        json_params = json.loads(str(args_dict[3]).split("=")[1])
    except Exception as e:
        print("failed to parse json params for adding config Exception %s" % str(e))
        return

    fio_obj.add_config(test_name, json_params)

def runcustom(args_dict, logger=DEFULT_LOGGER):
    if len(args_dict) < 4 or len(str(args_dict[3]).split("=")) < 2:
        raise Exception("Incorrect parameters for runcustom %s" % str(args_dict))
    
    test_name = str(args_dict[2])
    fio_obj = Fio()
    try:
        logger.debug(str(args_dict[3]).split("=")[1])
        json_params = json.loads(str(args_dict[3]).split("=")[1])
    except Exception as e:
        raise Exception("failed to parse json params for adding config Exception %s" % str(e))
    
    config = fio_obj.add_config(test_name, json_params, writefile=False)
    logger.debug("Start performance testing")
    result, err = fio_obj.run_test_config(config)
    if result is None:
        raise Exception("FIO error %s" % str(err))

    result_json = json.loads('{"result":"FAILURE"}')
    try:
        result_json = json.loads(result)
        read_bw = str(result_json["jobs"][0]["read"]["bw"])
        read_iops = str(int(round(float(result_json["jobs"][0]["read"]["iops"]))))
        read_lat = str(int(round(float(result_json["jobs"][0]["read"]["lat_ns"]["mean"]))))
        logger.debug("read: bw %s KiB/s lat %s ns iops %s" % (read_bw, read_lat, read_iops))
        write_bw = str(result_json["jobs"][0]["write"]["bw"])
        write_iops = str(int(round(float(result_json["jobs"][0]["write"]["iops"]))))
        write_lat = str(int(round(float(result_json["jobs"][0]["write"]["lat_ns"]["mean"]))))
        logger.debug("write: bw %s KiB/s lat %s ns iops %s" % (write_bw, write_lat, write_iops))
    except Exception as e:
        raise Exception("Failed to parse fio output %s Exception %s" % (str(result), str(e)))

    logger.debug("End performance testing")
    return {"result":str(result_json), "read_bw":read_bw, "read_iops":read_iops, "read_lat":read_lat,
        "write_bw":write_bw, "write_iops":write_iops, "write_lat":write_lat}

def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == "help":
            print_help_exit()
            return
        elif sys.argv[1] == "list":
            list_tests()
            return
        elif sys.argv[1] == "show":
            show_test(sys.argv[2])
            return
        elif sys.argv[1] == "run":
            run_test(sys.argv, local=False)
            return
        elif sys.argv[1] == "runlocal":
            run_test(sys.argv)
            return
        elif sys.argv[1] == "add":
            add_test(sys.argv)
            return
        elif sys.argv[1] == "del":
            del_test(sys.argv[2])
            return
        elif sys.argv[1] == "runcustom":
            try:
                runcustom(sys.argv)
            except Exception as e:
                print("Failed to run custom test with parameters %s Exception %s" % (str(sys.argv), str(e)))
                print_help_exit()
            return
    
    print("Unsupported command or parameters %s" % str(sys.argv[1:]))
    print_help_exit()

if __name__ == "__main__":
    main()