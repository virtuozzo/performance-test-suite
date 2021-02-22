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
import csv
import argparse
import testutils
import performance_test


def compare_results(result, compare, test_name):
    for k in result:
        if k == "result": # skip json result from test output
            continue

        if int(result[k]) - compare[k]["val"] > compare[k]["div"]:
            raise(Exception(f"{test_name} result {result[k]} {k} divergates from comparsion {compare[k]['val']} {k}"))

def rand_read(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randread"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["rand_read", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"])])


    if compare is not None:
        compare_results(result, compare, "rand_read")
        return result

    if int(result["read_bw"]) < 500000:
        raise(Exception("rand_read bandwidth less than 500 MB/s"))

    if int(result["read_iops"]) < 150000:
        raise(Exception("rand_read iops less than 150000 "))

    if int(result["read_lat"]) > 10000:
        raise(Exception("rand_read latency bigger than 10 us"))

    return result


def seq_read(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "read"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["seq_read", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"])])

    if compare is not None:
        compare_results(result, compare, "seq_read")
        return result
    
    if int(result["read_bw"]) < 500000:
        raise(Exception("seq_read bandwidth less than 500 MB/s"))
    
    if int(result["read_iops"]) < 150000:
        raise(Exception("seq_read iops less than 150000 "))
    
    if int(result["read_lat"]) > 10000:
        raise(Exception("seq_read bigger than 10 us"))

    return result

def rand_write(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randwrite"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["rand_write","","","", int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "rand_write")
        return result

    if int(result["write_bw"]) < 500000:
        raise(Exception("rand_write bandwidth less than 500 MB/s"))
    
    if int(result["write_iops"]) < 130000:
        raise(Exception("rand_write iops less than 130000 "))
    
    if int(result["write_lat"]) > 10000:
        raise(Exception("rand_write latency bigger than 10 us"))

    return result

def seq_write(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "write"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["seq_write","","","", int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "seq_write")
        return result

    if int(result["write_bw"]) < 500000:
        raise(Exception("seq_write bandwidth less than 500 MB/s"))
    
    if int(result["write_iops"]) < 130000:
        raise(Exception("seq_write iops less than 130000 "))
    
    if int(result["write_lat"]) > 10000:
        raise(Exception("seq_write latency bigger than 10 us"))

    return result

def rand_R70_W30(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randrw"
    params["rwmixread"] = "70"
    params["rwmixwrite"] = "30"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["rand_R70_W30", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"]),
            int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "rand_R70_W30")
        return result

    if int(result["write_bw"]) < 150000:
        raise(Exception("rand_R70_W30 write bandwidth less than 150 MB/s"))
    
    if int(result["write_iops"]) < 40000:
        raise(Exception("rand_R70_W30 write iops less than 40000 "))
    
    if int(result["write_lat"]) > 10000:
        raise(Exception("rand_R70_W30 write latency bigger than 10 us"))
    
    if int(result["read_bw"]) < 400000:
        raise(Exception("rand_R70_W30 read bandwidth less than 400 MB/s"))
    
    if int(result["read_iops"]) < 90000:
        raise(Exception("rand_R70_W30 read iops less than 90000 "))
    
    if int(result["read_lat"]) > 10000:
        raise(Exception("rand_R70_W30 read latency bigger than 10 us"))

    return result

def seq_R70_W30(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "rw"
    params["rwmixread"] = "70"
    params["rwmixwrite"] = "30"
    result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)

    if hasattr(logger, 'csv'):
        logger.csv(["seq_R70_W30", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"]),
            int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "seq_R70_W30")
        return result
    
    if int(result["write_bw"]) < 150000:
        raise(Exception("seq_R70_W30 write bandwidth less than 150 MB/s"))
    
    if int(result["write_iops"]) < 40000:
        raise(Exception("seq_R70_W30 write iops less than 40000 "))
    
    if int(result["write_lat"]) > 10000:
        raise(Exception("seq_R70_W30 write latency bigger than 10 us"))
    
    if int(result["read_bw"]) < 400000:
        raise(Exception("seq_R70_W30 read bandwidth less than 400 MB/s"))
    
    if int(result["read_iops"]) < 90000:
        raise(Exception("seq_R70_W30 read iops less than 90000 "))
    
    if int(result["read_lat"]) > 10000:
        raise(Exception("seq_R70_W30 read latency bigger than 10 us"))

    return result

def thread_scaling_common(params, threads=1, logger=testutils.DEFULT_LOGGER):
    result = dict()
    params["group_reporting"] = 1
    params["numjobs"] = 1
    one_thread_result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)
    params["numjobs"] = str(threads)
    many_threads_result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)
    if int(one_thread_result["read_bw"]) != 0:
        result["read_bw"] = ((int(many_threads_result["read_bw"]) - int(one_thread_result["read_bw"]))*100)//int(one_thread_result["read_bw"])
        result["read_iops"] = ((int(many_threads_result["read_iops"]) - int(one_thread_result["read_iops"]))*100)//int(one_thread_result["read_iops"])
        result["read_lat"] = ((int(many_threads_result["read_lat"]) - int(one_thread_result["read_lat"]))*100)//int(one_thread_result["read_lat"])

    if int(one_thread_result["write_bw"]) != 0:
        result["write_bw"] = ((int(many_threads_result["write_bw"]) - int(one_thread_result["write_bw"]))*100)//int(one_thread_result["write_bw"])
        result["write_iops"] = ((int(many_threads_result["write_iops"]) - int(one_thread_result["write_iops"]))*100)//int(one_thread_result["write_iops"])
        result["write_lat"] = ((int(many_threads_result["write_lat"]) - int(one_thread_result["write_lat"]))*100)//int(one_thread_result["write_lat"])
    return result

def thread_rand_read_scaling3(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randread"
    result = thread_scaling_common(params, 3, logger)
    logger.debug("scale bw %d" % int(result["read_bw"]))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_read_scaling3", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_read_scaling3")
        return result

    if int(result["read_bw"]) < 80:
        raise(Exception("thread_rand_read_scaling3 read bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["read_iops"]))
    if int(result["read_iops"]) < 80:
        raise(Exception("thread_rand_read_scaling3 read iops less than 80%"))

    logger.debug("scale lat %d" % int(result["read_lat"]))
    if int(result["read_lat"]) > 70:
        raise(Exception("thread_rand_read_scaling3 read latency bigger than 80%"))

    return result

def thread_rand_read_scaling30(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randread"
    result = thread_scaling_common(params, 30, logger)
    logger.debug("scale bw %d" % int(result["read_bw"]))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_read_scaling30", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_read_scaling30")
        return result

    if int(result["read_bw"]) < 180:
        raise(Exception("thread_rand_read_scaling30 read bandwidth less than 180%"))
    
    logger.debug("scale iops %d" % int(result["read_iops"]))
    if int(result["read_iops"]) < 180:
        raise(Exception("thread_rand_read_scaling30 read iops less than 180%"))

    logger.debug("scale lat %d" % int(result["read_lat"]))
    if int(result["read_lat"]) > 900:
        raise(Exception("thread_rand_read_scaling30 read latency bigger than 900%"))

    return result

def thread_rand_write_scaling3(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randwrite"
    result = thread_scaling_common(params, 3, logger)
    logger.debug("scale bw %d" % int(result["write_bw"]))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_write_scaling3", "","","", int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_write_scaling3")
        return result

    if int(result["write_bw"]) < 80:
        raise(Exception("thread_rand_write_scaling3 write bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["write_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_write_scaling3 write iops less than 80%"))

    logger.debug("scale lat %d" % int(result["write_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_write_scaling3 write latency bigger than 80%"))

    return result

def thread_rand_write_scaling30(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randwrite"
    result = thread_scaling_common(params, 30, logger)
    logger.debug("scale bw %d" % int(result["write_bw"]))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_write_scaling30", "","","", int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_write_scaling30")
        return result

    if int(result["write_bw"]) < 80:
        raise(Exception("thread_rand_write_scaling30 write bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["write_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_write_scaling30 write iops less than 80%"))

    logger.debug("scale lat %d" % int(result["write_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_write_scaling30 write latency bigger than 80%"))

    return result

def thread_rand_R70_W30_scaling3(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randrw"
    params["rwmixread"] = "70"
    params["rwmixwrite"] = "30"
    result = thread_scaling_common(params, 3, logger)
    logger.debug("scale read bw %d write bw %d" % (int(result["write_bw"]), int(result["write_bw"])))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_R70_W30_scaling3", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"]),
            int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_R70_W30_scaling3")
        return result

    if int(result["read_bw"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling3 read bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["read_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling3 read iops less than 80%"))

    logger.debug("scale lat %d" % int(result["read_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_R70_W30_scaling3 read latency bigger than 80%"))

    if int(result["write_bw"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling3 write bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["write_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling3 write iops less than 80%"))

    logger.debug("scale lat %d" % int(result["write_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_R70_W30_scaling3 write latency bigger than 80%"))

    return result

def thread_rand_R70_W30_scaling30(params, logger=testutils.DEFULT_LOGGER, compare=None):
    params["rw"] = "randrw"
    params["rwmixread"] = "70"
    params["rwmixwrite"] = "30"
    result = thread_scaling_common(params, 30, logger)
    logger.debug("scale read bw %d write bw %d" % (int(result["write_bw"]), int(result["write_bw"])))
    if hasattr(logger, 'csv'):
        logger.csv(["thread_rand_R70_W30_scaling30", int(result["read_bw"]), int(result["read_iops"]), int(result["read_lat"]),
            int(result["write_bw"]), int(result["write_iops"]), int(result["write_lat"])])

    if compare is not None:
        compare_results(result, compare, "thread_rand_R70_W30_scaling30")
        return result

    if int(result["read_bw"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling30 read bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["read_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling30 read iops less than 80%"))

    logger.debug("scale lat %d" % int(result["read_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_R70_W30_scaling30 read latency bigger than 80%"))

    if int(result["write_bw"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling30 write bandwidth less than 80%"))
    
    logger.debug("scale iops %d" % int(result["write_iops"]))
    if int(result["write_iops"]) < 80:
        raise(Exception("thread_rand_R70_W30_scaling30 write iops less than 80%"))

    logger.debug("scale lat %d" % int(result["write_lat"]))
    if int(result["write_lat"]) > 70:
        raise(Exception("thread_rand_R70_W30_scaling30 write latency bigger than 80%"))

    return result


def main(filename, logger, nofail, compare_result):
    common_params = json.loads('{"filename":"%s", "size":"4GB", "runtime":"5", "time_based":"1", "direct":"1", \
        "ioengine":"libaio", "bs":"4k", "numjobs":"1"}' % filename)
    
    test_suite = [
        rand_read,
        seq_read,
        rand_write,
        seq_write,
        rand_R70_W30,
        seq_R70_W30,
        thread_rand_read_scaling3,
        thread_rand_read_scaling30,
        thread_rand_write_scaling3,
        thread_rand_write_scaling30,
        thread_rand_R70_W30_scaling3,
        thread_rand_R70_W30_scaling30,
    ]

    if hasattr(logger, 'csv'):
        logger.csv(["Test Name", "read bw KiB/s", "read iops", "read lat ns", "write bw KiB/s", "write iops", "write lat ns"])

    for test in test_suite:
        try:
            result = test(common_params, logger, compare_result[test.__name__] if test.__name__ in compare_result else None)
            logger.info("test %s passed" % test.__name__)
        except Exception as e:
            err = "test %s failed reason %s" % (test.__name__, str(e))
            if nofail:
                logger.error(err)
            else:
                raise Exception(err)

def get_percentage(val, percents):
    return (int(val) * int(percents))//100


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Performance test suite parameters:")
    parser.add_argument('-d', dest='dev', action='store', type=str, required=True, help='Test device path')
    parser.add_argument('-n', dest='nofail', action='store_true', default=False, help='Run all tests not stop after one fail')
    parser.add_argument('-t', dest='log_type', action='store', type=int, default=3, choices=range(1, 6), help='Log type 1:silent 2:syslog 3:print 4:file 5:file csv default 3')
    parser.add_argument('-f', dest='log_file_path', action='store', type=str, default='/tmp/ptest_log.log', help='Log file path default file path /tmp/ptest_log.log')
    parser.add_argument('-l', dest='log_level', action='store', type=int, default=5, choices=range(0, 8), help='Log level CRITICAL: 0, FATAL: 1, ERROR: 2, WARNING: 3, WARN: 4, INFO: 5, DEBUG: 6, NOTSET: 7 by default 5')
    parser.add_argument('-c', dest='compare_file_path', action='store', type=str, default=None, help='compare file path. File with what we will compare results')
    parser.add_argument('-w', dest='compare_percents', action='store', type=int, default=10, choices=range(0, 100), help='compare divergence in 0-100 percents how much can result be different from compare file default 10')
    args = parser.parse_args()
    logger = testutils.setup_log(args.log_type, args.log_level, args.log_file_path)
    compare_result = dict()
    if args.compare_file_path is not None:
        logger.info("Got file for comparsion %s " % args.compare_file_path)
        try:
            with open(args.compare_file_path) as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    if str(row[0]) == "Test Name":
                        continue

                    for i in range(len(row)):
                        if row[i] == "":
                            row[i] = 0

                    test_compare = {
                        "read_bw":{"val":int(row[1]), "div":get_percentage(int(row[1]), args.compare_percents)},
                        "read_iops":{"val":int(row[2]), "div":get_percentage(int(row[2]), args.compare_percents)},
                        "read_lat":{"val":int(row[3]), "div":get_percentage(int(row[3]), args.compare_percents)}
                    }
                    if len(row) > 4:
                        test_compare["write_bw"] = {"val":int(row[4]), "div":get_percentage(int(row[4]), args.compare_percents)}
                        test_compare["write_iops"] = {"val":int(row[5]), "div":get_percentage(int(row[5]), args.compare_percents)}
                        test_compare["write_lat"] = {"val":int(row[6]), "div":get_percentage(int(row[6]), args.compare_percents)}
                    else:
                        test_compare["write_bw"] = {"val":0, "div":0}
                        test_compare["write_iops"] = {"val":0, "div":0}
                        test_compare["write_lat"] = {"val":0, "div":0}

                    compare_result[str(row[0])] = test_compare
        except Exception as e:
            logger.error("Unable to parse csv comparsion file %s error %s" %  (args.compare_file_path, str(e)))
            sys.exit(1)

    try:
        main(args.dev, logger, args.nofail, compare_result)
    except Exception as e:
        logger.error("Testing failed %s" % str(e))