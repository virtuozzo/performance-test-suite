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

import logging
import logging.handlers
import csv
from re import VERBOSE
from subprocess import Popen, PIPE


class DefaultLogger():
    def debug(self, msg):
        print(msg)

    def info(self, msg):
        print(msg)
    
    def warn(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    def exception(self, msg):
        print(msg)
    
    def critical(self, msg):
        print(msg)

#class CsvLogger(logging.NullHandler):
class CsvLogger(logging.Logger):
    def __init__(self, logtype, log_file_name):
        super(CsvLogger, self).__init__(logtype)
        self.file = log_file_name
        with open(log_file_name, mode='w') as csv_file:
            csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def csv(self, msg):
        with open(self.file, mode='a+') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(msg)

DEFULT_LOGGER=DefaultLogger()
LOGTYPE_DICT={
    0:logging.CRITICAL,
    1:logging.FATAL,
    2:logging.ERROR,
    3:logging.WARNING,
    4:logging.WARN,
    5:logging.INFO,
    6:logging.DEBUG,
    7:logging.NOTSET
}

LOG_TYPE_SILENT = 1
LOG_TYPE_SYSLOG = 2
LOG_TYPE_VERBOSE = 3
LOG_TYPE_FILE = 4
LOG_TYPE_FILE_CSV = 5

def setup_log(type=LOG_TYPE_VERBOSE, level=3, log_file_name="/tmp/ptest_log.log"):
    logger = DEFULT_LOGGER
    try:
        logger = logging.getLogger(str(type))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        if type == LOG_TYPE_SYSLOG:
            handler = logging.handlers.SysLogHandler()
        elif type == LOG_TYPE_VERBOSE:
            handler = logging.StreamHandler()
        elif type == LOG_TYPE_FILE:
            handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=1000000, backupCount=5)
        elif type == LOG_TYPE_FILE_CSV:
            logger = CsvLogger(str(type), log_file_name)
            handler = logging.StreamHandler()
        else:
            handler = logging.NullHandler()

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOGTYPE_DICT[level])
    except Exception as e:
        print("Error during logger setup %s" % str(e))

    return logger

def systemExec(cmd, shell=False, verbouse=False, logger=DEFULT_LOGGER):
    try:
        if verbouse:
            logger.debug("command %s" % str(cmd))
        process = Popen(cmd, shell=shell, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            if verbouse:
                logger.debug("o None e %s" % str(err))
            return None, str(err)

        if verbouse:
            logger.debug("o %s e %s" % (str(out, 'utf-8'), str(err, 'utf-8')))
        return str(out, 'utf-8'), str(err, 'utf-8')
    except EnvironmentError as e:
        logger.error("Failed to execute command %s exception: %s" % (str(cmd), str(e)))

    if verbouse:
        logger.debug("o None e None")
    return None, None
