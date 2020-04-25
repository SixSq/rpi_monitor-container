#!/usr/bin/env python
from __future__ import print_function

# Require the vcgencmd command which itself require access to /dev/vchiq
# vcgencmd can be installed on Raspbian with `apt-get install -y libraspberrypi-bin`

import os
import time
import socket
import subprocess


def vcgencmd(*args):
    return subprocess.check_output(('vcgencmd',) + args)

def clock():
    args = ('arm', 'core', 'h264', 'isp', 'v3d', 'uart', 'pwm', 'emmc', 'pixel', 'vec', 'hdmi', 'dpi')
    data = {arg: vcgencmd('measure_clock',arg).split('=')[-1] for arg in args}
    return {k: int(v.strip()) for k, v in data.items()}

def voltage():
    args = ('core', 'sdram_c', 'sdram_i', 'sdram_p')
    data = {arg: vcgencmd('measure_volts',arg).split('=')[-1].strip('\n') for arg in args}
    return {k: float(v.strip('V')) for k, v in data.items()}

def temperature():
    out = vcgencmd('measure_temp')
    return {'core': float(out.split('=')[-1].strip().rstrip("'C"))}

def throttling():
    return {}

def send_to_graphite(graphite_address, graphite_port, metric_prefix, metrics):
    metrics_data = ''
    t = int(time.time())

    for name, value in metrics.items():
        metrics_data += '{}.{} {} {}\n'.format(metric_prefix, name, value, t)

    if metrics_data:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((graphite_address, graphite_port))
        s.sendall(metrics_data)
        s.close()

def main():
    interval =    float(os.environ.get('INTERVAL', 60.0))
    metric_prefix     = os.environ.get('METRIC_PREFIX', 'rpi_monitor.{}'.format(socket.gethostname()))
    graphite_address  = os.environ.get('GRAPHITE_ADDRESS', 'localhost')
    graphite_port = int(os.environ.get('GRAPHITE_PORT', 2003))

    while True:
        t = time.time()
        metrics = {}

        metrics.update({'clock.'+k      : v for k, v in clock().items()})
        metrics.update({'voltage.'+k    : v for k, v in voltage().items()})
        metrics.update({'temperature.'+k: v for k, v in temperature().items()})
        metrics.update({'throttling.'+k : v for k, v in throttling().items()})

        send_to_graphite(graphite_address, graphite_port, metric_prefix, metrics)

        time.sleep(interval - (time.time() - t))


if __name__ == '__main__':
    main()
