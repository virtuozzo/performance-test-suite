# Performance test suite for Integrated Storage
​
### Preface:
This test suite has been built for block devices performance and latency testing.
First, we tried to use FIO with preconfigured tests in config files (you can find them under this repo's FIO folder), but as our needs increased, we examined better options.
Accordingly, we built a Python Wrapper on top of FIO to easily create new tests and get output in a format that suits our requirements.

### Structure of test suite:
This test suite consists of four main parts:
FIO wrapper (fiolib.py configs under FIO folder)
Virtual server setup and run primitives (vmtestlib.py fio/testinitrd.img fio/vmlinuz-kvm fio/default.xml)
FIO test generator and runner (performance_test.py)
Set of tests for the automated testing and iterations (ptest.py)

### Requirements:
Assuming RHEL or centos7 installation
To use this test, you should install Python >= 3.6
```ssh
yum install python3
```
Then, install FIO according to your distro
```ssh
yum install fio
```
If you want to run tests inside virtual servers, you should have installed a KVM environment with libvirt and default networking.
​
## Usage:
Before running tests on block devices, make sure they are not used anywhere, not mounted, or passed through to virtual servers.
Please note that all tests that run directly on the block device (-d /dev/sda , dev=/dev/sda) destroys the file system and you will lose all data stored there.
To avoid data loss, configure tests for writing to files (-d /mnt/mountpoint/testfile , dev=/mnt/mountpoint/testfile)
​
### Simple test suite run:
1) Ensure you have outbound internet access from your compute resource.
2) Clone the framework repo or scp archive with all scripts to the compute resource
```sh
git clone git@bitbucket.org:onappcore/storage-performance-testsuit.git
``` 
3) Go to tests directory
```sh
cd storage-performance-testsuite/
```
4) Run tests:
```sh
./ptest.py -n -d /dev/sde
```
Results:
```sh
ERROR - main - test rand_read failed reason rand_read bandwidth less than 500 MB/s
ERROR - main - test seq_read failed reason seq_read bandwidth less than 500 MB/s
ERROR - main - test rand_write failed reason rand_write bandwidth less than 500 MB/s
ERROR - main - test seq_write failed reason seq_write bandwidth less than 500 MB/s
ERROR - main - test rand_R70_W30 failed reason rand_R70_W30 write bandwidth less than 150 MB/s
ERROR - main - test seq_R70_W30 failed reason seq_R70_W30 write bandwidth less than 150 MB/s
INFO - main - test thread_rand_read_scaling3 passed
INFO - main - test thread_rand_read_scaling30 passed
ERROR - main - test thread_rand_write_scaling3 failed reason thread_rand_write_scaling3 write bandwidth less than 80%
ERROR - main - test thread_rand_write_scaling30 failed reason thread_rand_write_scaling30 write latency bigger than 80%
ERROR - main - test thread_rand_R70_W30_scaling3 failed reason thread_rand_R70_W30_scaling3 read bandwidth less than 80%
ERROR - main - test thread_rand_R70_W30_scaling30 failed reason thread_rand_R70_W30_scaling30 read bandwidth less than 80%
```
The tests are initiated one by one; if one fails, the others do not start. If the test passes, you will get the following output:
```sh
INFO - main - test <test case> passed
```
If the disk results are smaller than described in ptest.py, you will get the following error:
```sh
ERROR - main - test <test case> failed reason <reason of fail>
```

### Using debug log level option:
To use the debug log level option, run the following command:
```sh
./ptest.py -n -l6 -d /dev/sde 
```
In this case, you can check the actual results of each test:
```sh
DEBUG - runcustom - read: bw 574 KiB/s lat 4728122 ns iops 144
DEBUG - runcustom - write: bw 256 KiB/s lat 4974526 ns iops 64
```
You can find here bandwidth, latency, and IOPS gathered during different tests.
Also, you can check the parameters passed to FIO like the following:
```sh
  {"filename": "/dev/sde", "size": "4GB", "runtime": 1, "time_based": "1", "direct": "1", "ioengine": "libaio", "bs": "4k", numjobs": "3", "rw": "randrw", "rwmixread": "70", "rwmixwrite": "30", "group_reporting": 1}
```
### Store logs to file:
To store logs in a file, run the following command:
```sh
./ptest.py -n -l6 -t4 -f /root/result.log -d /dev/sde
```
Alternatively, you can enable CSV output for further processing:
```sh
./ptest.py -n  -t5 -f /root/result.csv -d /dev/sde
```
Example of result:
```sh
cat /root/result.csv 
Test Name,read bw KiB/s,read iops,read lat ns,write bw KiB/s,write iops,write lat ns
rand_read,896,224,4456938
seq_read,81310,20328,47440
rand_write,,,,792,198,5040350
seq_write,,,,663,166,6018868
rand_R70_W30,582,146,4649899,259,65,4954123
seq_R70_W30,1476,369,101060,647,162,5935668
thread_rand_read_scaling3,164,164,12
thread_rand_read_scaling30,210,210,833
thread_rand_write_scaling3,,,,10,10,170
thread_rand_write_scaling30,,,,154,154,1013
thread_rand_R70_W30_scaling3,75,75,45,72,70,129
thread_rand_R70_W30_scaling30,90,90,895,127,127,1840
```
If you convert it to a table, you will see the result as follows:

|           Test Name           | read bw KiB/s | read iops | read lat ns | write bw KiB/s | write iops | write lat ns |  
|-------------------------------|---------------|-----------|-------------|----------------|------------|--------------|  
| rand_read                     |           896 |       224 |     4456938 |                |            |              |  
| seq_read                      |         81310 |     20328 |       47440 |                |            |              |  
| rand_write                    |               |           |             |            792 |        198 |      5040350 |  
| seq_write                     |               |           |             |            663 |        166 |      6018868 |  
| rand_R70_W30                  |           582 |       146 |     4649899 |            259 |         65 |      4954123 |  
| seq_R70_W30                   |          1476 |       369 |      101060 |            647 |        162 |      5935668 |  
| thread_rand_read_scaling3     |           164 |       164 |          12 |                |            |              |  
| thread_rand_read_scaling30    |           210 |       210 |         833 |                |            |              |  
| thread_rand_write_scaling3    |               |           |             |             10 |         10 |          170 |  
| thread_rand_write_scaling30   |               |           |             |            154 |        154 |         1013 |  
| thread_rand_R70_W30_scaling3  |            75 |        75 |          45 |             72 |         70 |          129 |  
| thread_rand_R70_W30_scaling30 |            90 |        90 |         895 |            127 |        127 |         1840 |  

### Comparison mode
You can compare results from previous tests and set divergent to track performance degradation. To do that:
1) Generate test results for comparison:
```ssh
./ptest.py -n  -t5 -f /root/result.csv -d /dev/sde 
```
2) Make changes or prepare another device (for example, mount device):
```ssh
mkfs.xfs /dev/sde
mount /dev/sde /mnt/testdevice/
```
3) Run a comparison test to compare the result with the others from the file (-c option). By default it will fail if the difference is more than 10%.
```ssh
./ptest.py -n  -t5 -c /root/result.csv -f /root/result2.csv -d /mnt/testdevice/testfile
```
4) Run comparison test with a 20% fail-safe difference:
```ssh
./ptest.py -n  -t5 -c /root/result.csv -f /root/result2.csv -d /mnt/testdevice/testfile -w 20
```

### Usage of performance_test.py
This script is a part of the test suite but used like a lib. You may use it directly, but it doesn't have a stable user interface or proper error handling. We do not recommend you to use it, but you can do it at your own risk.
1) List fio configs under ./fio folder with ending.fio
```ssh
./performance_test.py list
```
2) Show test config (read the file and print it to stdout):
```ssh
./performance_test.py show 4kread
Test:
​
[global]
    name=4kread
    filename=4kread
....
```
3) Run test at the local machine:
```ssh
 ./performance_test.py runlocal 4kread dev=/dev/sde
Start performance testing
read: bw 2561 KiB/s lat 398984069 ns iops 640
write: bw 0 KiB/s lat 0 ns iops 0
End performance testing
```
3) Run a test at a virtual server (you need KVM set up at your compute resource). The command will add a new bridge to the test bridge:
```ssh
./performance_test.py run 4kread dev=/dev/sde
Start performance testing
Add bridge testbridge
VM 8472b5e485 Booted
read: bw 241576 KiB/s lat 4237781 ns iops 60394
write: bw 0 KiB/s lat 0 ns iops 0
End performance testing
```
4) Add FIO test with JSON config so you can run it later:
```ssh
./performance_test.py add newtest params='{"filename": "/dev/sde", "rw": "randread", "runtime": 5, "time_based": "1"}'
```
Here you can check if the text with the previous command was added:
```ssh
./performance_test.py list
Tests :
​
newtest
4k1thread1queue
randread
4k7030thread1
4kwrite
4kread
8k7030test
./performance_test.py show newtest
Test:
​
[global]
[newtest]
    filename=/dev/sde
    rw=randread
    runtime=5
    time_based=1
​
./performance_test.py runlocal newtest dev=/dev/sde
Start performance testing
read: bw 478 KiB/s lat 8343330 ns iops 120
write: bw 0 KiB/s lat 0 ns iops 0
End performance testing
```
5) To delete FIO test, use the following command:
```ssh
./performance_test.py del newtest
Test newtest deleted
​
./performance_test.py list
Tests :
​
4k1thread1queue
randread
4k7030thread1
4kwrite
4kread
8k7030test
```

### Test cases:
- rand_read,   random read test 4GB 
- seq_read,    sequential read test 4GB
- rand_write,  random write test 4GB
- seq_write,   sequential write test 4GB
- rand_R70_W30,random read 70% write 30% test 4GB
- seq_R70_W30, random read 70% write 30% test 4GB

Below are the same tests but with 1 thread and 3(30) threads, so results show how much I/O scaled with multithreading.
- thread_rand_read_scaling3,    
- thread_rand_read_scaling30,
- thread_rand_write_scaling3,
- thread_rand_write_scaling30,
- thread_rand_R70_W30_scaling3,
- thread_rand_R70_W30_scaling30,

You can see all FIO options using log level-l6 during a test run.

### Add new test case
1) Open ptest.py with the preferred editor or IDE.
2) Add a new test name to list test_suitee = [ in the function main().
3) Add function with the same name you added in the previous step to list with this fingerprint:
```ssh
def <test name>(params, logger=testutils.DEFULT_LOGGER, compare=None):
```
4) Update parameters dict with the parameters you want to pass to FIO:
```ssh
params["rw"] = "randread"
```
Default parameters are:
```ssh
'{"filename":"%s", "size":"4GB", "runtime":"5", "time_based":"1", "direct":"1", "ioengine":"libaio", "bs":"4k", "numjobs":"1"}'
```
Do not change the "filename" parameter because it passed from the test setup.
5) Run FIO test using libs:
```ssh
result = performance_test.runcustom(['', '', 'seq1', "params=%s" % json.dumps(params)], logger)
```
The result will be a dictionary generated with the FIO runs recorded in the dictionary key value pairs field.
"result"    - Full json output of fio
"read_bw"   - Read bandwidth
"read_iops" - Read IOPS
"read_lat"  - Read latency
"write_bw"  - Write bandwidth
"write_iops"- Write IOPS
"write_lat" - Write latency
6) If you want to specify CSV output for test check, in case CSV is configured, use the corresponding logger function:
```ssh
if hasattr(logger, 'csv'):
    logger.csv(["rand_read", int(result["read_bw"])])
```
7) Handle the compare option with implementing comparison like in the following example:
```ssh
if compare is not None:
        for k in result:
            if k == "result": # skip json result from test output
                continue
​
            if int(result[k]) - compare[k]["val"] > compare[k]["div"]:
                raise(Exception(f"rand_read result {result[k]} divergates from comparsion {compare[k]['val']}"))
        
        return result
```
8) If you want to implement your own checks in the test, raise an exception in case the test failed:
```ssh
raise(Exception("rand_read bandwidth less than 500 MB/s"))
```
If the test function did not raise any exception, the test is considered as passed.
In case you need additional results from FIO output, use JSON under result["result"].

### Configuration for virtual machine
Default config file for VS stored in the file fio/default.xml
Edit the configuration fields in function generate_vm_config() in vmtestlib.
```ssh
<uuid/>
<name/>
<memory/>
<vcpu/>
<os>
  <kernel/>
  <initrd/>
  <cmdline/>
</os>
<devices>
  <interface>
    <mac/>
    <target/>
    <source/>
  </interface>
  <disk>
    <source/>
    <target/>
  </disk>
</devices>
```
Almost all these fields are configurable in the constructor of class Testvm.
During VS lifetime, updated config is stored in file fio/<dynamicly generated vm name>.xml

### Known issues
Troubles with running tests at virtual servers with command ./performance_test.py run 4kread dev=/dev/sde

Error message from libvirt:
```ssh
virQEMUCapsNewForBinaryInternal:4555 : Cannot check QEMU binary /usr/bin/kvm-spice: No such file or directory
```
If you have an emulator different than /usr/bin/kvm-spice, you can fix this by editing default VS config fio/default.xml 
Substitute emulator option with correct for your virtualization or compute resource:
``ssh
<emulator>/usr/bin/kvm-spice</emulator>
<emulator>/usr/libexec/qemu-kvm</emulator>
....
```

Error message from libvirt:
```ssh
internal error: process exited while connecting to monitor: qemu: could not load kernel '/root/storage-performance-testsuit/fio/vmlinuz-kvm': Permission denied
```
Kernel image or rootfs has permissions conflicting with your libvirt settings.
To fix this, you can change the owner group and permissions for files fio/vmlinuz-kvm fio/testinitrd.img or move the entire test suite folder to the correct place.
```ssh
chown qemu fio/vmlinuz-kvm
chown qemu fio/testinitrd.img
chgrp qemu fio/vmlinuz-kvm
chgrp qemu fio/testinitrd.img
chmod 755 fio/vmlinuz-kvm
chmod 755 fio/testinitrd.img
cp -R storage-performance-testsuit /onappstore/
....
```

### Contributors
18 Jan 2021 Andrii Melnyk andriy.melnyk@onapp.com   
22 Jan 2021 Kateryna Bodnarchuk kateryna.bodnarchuk@onapp.com
