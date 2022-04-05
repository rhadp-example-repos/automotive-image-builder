# Unattended updates using OSTree

This document expects some basic knowledge about OSTree and how the
auto-sig uses it, see the [basic docs](updating_ostree.md) for that.

The basic ostree update operation is atomic in the sense that it is
either fully applies, or not at all on the next reboot. However, an
upgrade can still fail in other ways, like failing to boot, or booting
in a mode that doesn't work. When this happens on a regular computer
it is easy to interactively use the boot menu to boot the old
deployment and then roll back.

However, in the automotive use-case, like typical embedded systems,
there is no user than can interactively fix things up like
this. Instead we need a system that can detect such failures and
automatically fall back to the old boot. This is referred to as
"Unattended updates".


## Basic mechanisms: watchdog, boot-once

The basic implementation detail of unattended updates is an external
watchdog. The idea is that before applying the new update we tell some
external device to start a timer, and then we switch to the new
update.  If the update succeeds in some ahead-of-time time frame, it
will tell the watchdog to stop, and the update is considered
working. If the boot succeeds, but we detect that something is not
working we can roll back and reboot into the old version.

However, if the boot hang, the watchdog will not see a stop
command. When the time runs out the watchdog will then reset
the CPU, triggering a forced reboot.

In order to use the above we need the system to support some kind of
"boot-once" support. This is a mechanism where you tell the system
that the next boot should be into a new target, but unless that boot
triggers a permanent change, the next reboot will boot back into the
original target.

## Implementation in qemu

The basic mechanisms described above are very dependent on the exact
hardware, so it is hard to give general documentation on how to do
this. Instead we chose to make an example based on a virtual machine
in qemu. As it doesn't need any particular hardware this means anyone
can try it.

### Watchdog in qemu

Qemu actually supports some emulated hardware watchdogs, but
unfortunately those all reset the watchdog on system reset, so it is
not possible to use them for unattended updates. Instead we use the
`runvm` script in this repo, as it has a simple external watchdog
built in.

Just pass `--watchdog` on the command line (and `--verbose` if you
want to see messages from the watchdog. This will create a device
`/dev/virtio-ports/watchdog.0`, in the VM. If you write "START" into
it the watchdog will start a 30 sec timeout, and if you write "STOP"
into it it will stop any outstanding timeout. If the timeout runs
out the script will connect to the qemu monitor and tell it to reset
the VM.

There is some code in the `rpms/autosig-watchdog` to use the watchdog.
There are watchdog-start and watchdog-stop commands, and some systemd
service files to integrate with the systems a described below.

### boot-once in grub2

The OSTree images uses grub2 to boot the system, this uses the
BootLoader Standard (BLS) files to describe the possible boot targets,
and supports a boot counter mechanism to do the fallback. After an
update, ostree creates BLS files for the new and the old target, where
the new one is first (default boot) and the old is second.

Each time grub boots it loads the `grubenv` file, and this can store
key/value state between boots. In particular, it supports the
`boot_counter` and `boot_success` keys. If `boot_counter` is set
it gets decremented (and saved back to `grubenv`). If boot_counter
reaches 0 we consider the boot failed, and we change the default
to the second entry, thus falling back to the old system.

## Health check system integration

To combine the above during an update we use
[greenboot](https://github.com/fedora-iot/greenboot) which hooks into
OSTree and systemd adding various forms of health checks.

Using greenboot, an regular update would look like this:

 * rpm-ostree upgrade prepares (stages) an update, this writes
   all the basic OS in place for the next boot, but doesn't
   merge the system /etc into the new deployment, or configure
   grub to boot it.
 * rpm-ostree triggers `ostree-finalize-staged.service`, which
   will complete the update at the end of this reboot.
 * This triggers `greenboot-grub2-set-counter.service` which
   modifies `grubenv` to set `boot_counter`, enabling boot-once
   and health checks for the new boot.
 * The system is rebooted,
 * Before reaching the `boot-complete.target`systemd target,
   `greenboot-healthcheck.service` is run, which runs various
   checks on the system and detects if it is OK (green) or
   failed (red).
 * In case the system is red, some info is logged and the system
   is rebooted. This will trigger the boot_counter mechanism,
   and falling back to the old ostree deployment. In the
   next boot the `greenboot-rpm-ostree-grub2-check-fallback.service`
   service will detect this and will make the old default
   permanent (roll back).
 * In case the system is green, the `greenboot-grub2-set-success.service`
   will remove the `boot_counter` key and set `boot_success=1` in grubenv.
   This makes further reboots use the new version.

The watchdog service files mentioned above integrate with this setup
in two ways. First of all, the `watchdog-ostree-start.service`
triggers before the `ostree-finalize-staged.service` completes the
migration (at reboot) and starts the watchdog.

Secondly, the `watchdog-ostree-stop.service` triggers of
`boot-complete.target` (i.e. after a successful green boot) and stops
the watchdog.

## Example

The `upgrade-demo` image demonstrates how this can work.

First we build the basic demo, and create a repo for the update.

```
$ make cs9-qemu-upgrade-demo-ostree.x86_64.qcow2 OSTREE_REPO=upgrade-demo-repo
```

Then we build the update, and this one includes the `slow-startup`
extra rpm which makes the boot slower than the 30 sec of the watchdog.

```
$ make cs9-qemu-upgrade-demo-ostree.x86_64.repo OSTREE_REPO=upgrade-demo-repo DEFINES='extra_rpms=["slow-startup"] distro_version="9.1"'
```

To make it easier to see what version is running we also set a newer version (9.1) for the update.

Then run the image like so:

```
$ ./runvm --verbose --watchdog --publish-dir=upgrade-demo-repo cs9-qemu-upgrade-demo-ostree.x86_64.qcow2
```

After login we can check the state of the system:

```
# rpm-ostree status
State: idle
Deployments:
● auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9 (2022-04-05T10:26:04Z)
                    Commit: da5f056764585acb7b618ac826f2555b8ef0cfac7ab783a7e48b4140814dc342
# cat /boot/grub2/grubenv
# GRUB Environment Block
boot_success=1
...
```

Then trigger an update and check out the new state:

```
# rpm-ostree upgrade
Staging deployment... done
Added:
  slow-startup-0.1-1.el9.x86_64
Run "systemctl reboot" to start a reboot
# rpm-ostree status
State: idle
Deployments:
  auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9.1 (2022-04-05T10:28:59Z)
                    Commit: b4eeec5715eb8b18fae89e95e2ac295279e23b84675bb38281c03bc52543db9e
                      Diff: 1 added

● auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9 (2022-04-05T10:26:04Z)
                    Commit: da5f056764585acb7b618ac826f2555b8ef0cfac7ab783a7e48b4140814dc342
# cat /boot/grub2/grubenv
# GRUB Environment Block
boot_success=0
boot_counter=1
...
```

Then run `reboot`, and notice the `Starting watchdog for 30 sec` output from runvm.
If you manage to log in before the watchdog you can get the state:

```
# rpm-ostree status
State: idle
Deployments:
● auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9.1 (2022-04-05T10:28:59Z)
                    Commit: b4eeec5715eb8b18fae89e95e2ac295279e23b84675bb38281c03bc52543db9e

  auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9 (2022-04-05T10:26:04Z)
                    Commit: da5f056764585acb7b618ac826f2555b8ef0cfac7ab783a7e48b4140814dc342
# cat /boot/grub2/grubenv
# GRUB Environment Block
boot_success=0
boot_counter=0
...
```

However, the slow-start service is slower than the watchdog, so after
a short time you should see `Triggering watchdog` from runvm, and the
VM reboots.

At the end of the next boot you will see `Stopped watchdog` from runvm
as the fallback succeeds, and if you look in the logs you will see lines like:

```
greenboot-rpm-ostree-grub2-check-fallback[561]: FALLBACK BOOT DETECTED! Default rpm-ostree deployment has been rolled back.
Reached target Boot Completion Check.
Starting Mark boot as successful in grubenv...
Starting greenboot Success Scripts Runner...
greenboot[670]: Boot Status is GREEN - Health Check SUCCESS
Starting Stop watchdog after update on successful boot...
Finished greenboot Success Scripts Runner.
watchdog-ostree-stop.service: Deactivated successfully.
Finished Stop watchdog after update on successful boot.
Finished Mark boot as successful in grubenv.
```

And if you check the status, we're back at the original version:

```
# rpm-ostree status
State: idle
Deployments:
● auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9 (2022-04-05T10:26:04Z)
                    Commit: da5f056764585acb7b618ac826f2555b8ef0cfac7ab783a7e48b4140814dc342

  auto-sig:cs9/x86_64/qemu-upgrade-demo
                   Version: 9.1 (2022-04-05T10:28:59Z)
                    Commit: b4eeec5715eb8b18fae89e95e2ac295279e23b84675bb38281c03bc52543db9e
# cat /boot/grub2/grubenv
# GRUB Environment Block
boot_success=1
...
```
