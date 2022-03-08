#!/usr/bin/env python3
import os
import time
import argparse
import cv2

SUFFIX = '-cut'

parser = argparse.ArgumentParser(description="Edit the video. Change resolution.")
parser.add_argument("video", help="input video")
parser.add_argument("-o", f"--output", help="output video; default video{SUFFIX}.mov")
parser.add_argument("-w", f"--width", help="resize output width; [pixels]", type=int)
args = parser.parse_args()

# open source video
video = cv2.VideoCapture(args.video)
if not video.isOpened():
    print(f"video open error '{args.video}'")
    exit()

frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video.get(cv2.CAP_PROP_FPS))

# change resolution
if args.width is None: args.width = width
scale = args.width/width
size = (args.width, round(height*scale))

print(f"resolution: ({width},{height}) x{scale:.2f} -> {size}")

# make output video
if args.output is None:
	root, ext = os.path.splitext(args.video)
	args.output = root+SUFFIX+ext
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
output = cv2.VideoWriter(args.output, fourcc, fps, size)

perf0 = time.perf_counter()
while True:
    ret, frame = video.read()
    if not ret:
        break

    frame = cv2.resize(frame, size)

    output.write(frame)

video.release()
output.release()

print(f"done; {time.perf_counter()-perf0:.3f} sec")
