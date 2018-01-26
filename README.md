# Working with ephemeral (dynamically created) USB devices in Docker

In case you need to run some Android flashing utils like `heimdall` in Docker you need to run your container with following options of your choice.

### There are two  of implementation ways of this:
1. Create cgroup rule and sync devices in container by udev trigger (as described below and what I've made)
2. Run docker container with --priviliged -v /dev/bus/usb (not safe)

This repository contains an implementation of https://github.com/moby/moby/pull/22563 PR:

> Dealing with dynamically created devices (--device-cgroup-rule)
Devices available to a container are assigned at creation time. The assigned devices will both be added to the cgroup.allow file and created into the container once it is run. This poses a problem when a new device needs to be added to a running container.
> One of the solution is to add a more permissive rule to a container allowing it access to a wider range of devices. For example, supposing our container needs access to a character device with major 42 and any number of minor number (added as new devices appear), the following rule would be added:
> docker create --device-cgroup-rule='c 42:* rmw' -name my-container my-image
Then, a user could ask udev to execute a script that would docker exec my-container mknod newDevX c 42 <minor> the required device when it is added.
> NOTE: initially present devices still need to be explicitely added to the create/run command

#### 1. Add sync script:
```sh
cp docker-usb-sync.py /usr/bin/docker_device_sync.py
```

Don't forget to change container name in script.

#### 2. Create new udev rule:
```sh vim /etc/udev/rules.d
ACTION=="add", SUBSYSTEM=="usb", RUN+="/usr/bin/docker_device_sync.py"
sudo service udev restart
```

#### 3. Run container:
```sh
docker run --rm -d --device=/dev/bus/usb --device-cgroup-rule='c 189:* rmw' <image_name>
```

#### 4. Device reboot:
```sh
adb reboot download
heimdall close-pc-screen
```

Now at every host device reconnect, a device also will be mapped into a container by our script triggered by udev.
