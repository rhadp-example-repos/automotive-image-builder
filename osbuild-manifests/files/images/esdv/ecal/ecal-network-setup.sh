#!/bin/bash

ifconfig lo multicast
route add -net 239.0.0.0 netmask 255.255.255.0 dev lo metric 1000

ifconfig enp0s2 multicast
route add -net 239.0.0.0 netmask 255.255.255.0 dev enp0s2 metric 1
