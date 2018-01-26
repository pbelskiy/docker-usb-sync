#!/usr/bin/env python3

import syslog
import subprocess
import os


def log(message):
    print(message)
    syslog.syslog(message)


def exec_in_container(cmd, name="container_name"):
    return subprocess.check_output(
        "docker exec {} bash -c '{}'".format(name, cmd),
        universal_newlines=True,
        shell=True
    )


root_dev = "/dev/bus/usb"

for bus_num in os.listdir(root_dev):
    bus_path = os.path.join(root_dev, bus_num)

    container_devices = exec_in_container("ls " + bus_path).split("\n")
    host_devices = os.listdir(bus_path)

    # remove dead links
    for device in container_devices:
        if device and device not in host_devices:
            exec_in_container("rm " + os.path.join(bus_path, device))

    # add new links
    for device in host_devices:
        if device not in container_devices:
            stat = os.stat(os.path.join(bus_path, device))

            cmd = "mknod {device} c {major} {minor}".format(
                device=os.path.join(bus_path, device),
                major=os.major(stat.st_rdev),
                minor=os.minor(stat.st_rdev)
            )

            exec_in_container(cmd)
