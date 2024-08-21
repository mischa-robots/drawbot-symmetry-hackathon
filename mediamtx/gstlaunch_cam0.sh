#!/bin/bash

export GST_DEBUG=3

# This works with one camera but both cams will crash the jetson nano

gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
    'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1' ! \
    nvv4l2h264enc bitrate=5000000 preset-level=1 ! \
    h264parse ! \
    rtspclientsink latency=0 protocols=tcp location=rtsp://localhost:8554/video0

# This also works with one camera but both cams will crash the jetson nano

# gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
#     'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1' ! \
#     nvvidconv ! 'video/x-raw, format=I420' ! \
#     omxh264enc bitrate=5000000 control-rate=constant iframeinterval=10 qp-range="20,40:20,40:20,40" preset-level=1 ! \
#     h264parse ! \
#     rtspclientsink latency=0 protocols=tcp location=rtsp://localhost:8554/video0

# Interestingly also does not work with both cameras anymore ¯\_(ツ)_/¯

# gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
#     'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1' ! \
#     nvvidconv ! 'video/x-raw, format=I420' ! \
#     omxh264enc bitrate=5000000 control-rate=variable ! \
#     h264parse ! mpegtsmux ! \
#     udpsink host=localhost port=5000
