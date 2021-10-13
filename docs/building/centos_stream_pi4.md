# Running CentOS-Stream on Raspberry pi 4

As the Automotive-SIG does not currently publish the images resulting from the
osbuild manifests, there are currently no CentOS-Stream images available to run
on a Raspberry pi 4.

However, Pablo Greco (CentOS Community member) created a little while ago CentOS
Linux 8 images that can be run on a Raspberry Pi 4.

You can find these images at: <https://people.centos.org/pgreco/CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4/>

So here are the steps you can follow to get a CentOS-Stream 8 OS running on a
Raspberry Pi 4.


* Download Pablo's image at: <https://people.centos.org/pgreco/CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4/>

* Unpack it:

```
unxz CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4-sda.raw.xz
```

* Flash it onto your SD card:

**/!\\** Beware to change the block device (``/dev/mmcblk0`` below) according to your system.

```
sudo dd if=CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4-sda.raw of=/dev/mmcblk0 status=progress bs=4M; sync
```

* Expand the size of `/`

Using your preferred tool: gparted, gnome-disks... extend the size of `/` as the
default size will not allow you to update the system.

* Insert the SD card into your raspberry pi 4

* Boot the raspberry pi

* Login as root using the `centos` password

* Connect to internet on raspberry pi 4 (wi-fi non-functional at present)

If you are not near to a router and you cannot connect directly to it, connect
the raspberry pi to an ethernet port on an internet connected machine. On the
internet connected machine acting as a server, go to "Edit connections..." ->
select wired network that is connected to pi -> "IPv4 Settings" ->
Method: "Shared to other computers" -> disconnect and reconnect cable so
raspberry pi gets an ip address which should be seen via `ifconfig`, should be
a 10.x.x.x in this case.

* Fully update the system and reboot

```
dnf update
...
reboot
```

* Switch to CentOS-Stream

```
dnf swap centos-linux-repos centos-stream-repos
dnf distro-sync
```

* Reboot

```
reboot
```
