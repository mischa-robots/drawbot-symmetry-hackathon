#!/bin/bash

#export GST_DEBUG=3

gst-launch-1.0 nvarguscamerasrc sensor-id=1 ! \
    'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1' ! \
    nvvidconv ! 'video/x-raw, format=I420' ! \
    omxh264enc bitrate=5000000 control-rate=variable ! \
    h264parse ! mpegtsmux ! \
    udpsink host=localhost port=5001
