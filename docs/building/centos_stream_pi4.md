# Running CentOS-Stream on Raspberry pi 4

Because the Automotive SIG does not currently publish the images that result from the
OSBuild manifests, there are currently no CentOS Stream images available to run
on a Raspberry Pi 4.
However, CentOS Community member Pablo Greco created a CentOS
Linux 8 image that can run on a Raspberry Pi 4.

Follow these steps to get a CentOS Stream 8 OS running on a
Raspberry Pi 4.

1. Download [Pablo's CentOS Linux 8 image for Raspberry Pi 4](<https://people.centos.org/pgreco/CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4/>).
1. Unpack it.
 ```
 unxz CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4-sda.raw.xz
 ```
1. Flash it onto your SD card.

 **/!\\** Change the block device, shown as _`/dev/mmcblk0`_ in the example, according to your system.

 ```
 sudo dd if=CentOS-Userland-8-stream-aarch64-RaspberryPI-Minimal-4-sda.raw of=/dev/mmcblk0 status=progress bs=4M; sync
 ```
1. Using your preferred tool, such as gparted, gnome-disks, or another, extend the size of `/` because the
default size will not allow you to update the system.
1. Insert the SD card into your Raspberry Pi 4.
1. Boot the Raspberry Pi 4.
1. Login as root using the password: `centos`.
1. Connect the Raspberry Pi 4 to the internet.

   > **NOTE:** Wifi is not yet functional.

   1. If you are not near to a router and you cannot connect
      directly to it, use an intermediary internet-connected machine as a relay to connect the Raspberry Pi to an ethernet port.
1. On the
internet connected machine acting as a server, select **Edit connections**.
1. Select the wired network that is connected to the Raspberry Pi.
1. Select **IPv4 Settings**.
1. Set **Method:** to *Shared to other computers*.
1. Disconnect and reconnect the cable so
Raspberry Pi gets an IP address, shown as *10.x.x.x* in `ifconfig`.
1. Fully update the system and reboot.
 ```
 dnf update
 ...
 reboot
 ```
1. Switch to CentOS Stream.
```
dnf swap centos-linux-repos centos-stream-repos
dnf distro-sync
```
1. Reboot again.
 ```
 reboot
 ```
