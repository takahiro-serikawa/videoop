#!/usr/bin/env python3
import os
import time
import math
import argparse
import cv2

SUFFIX = '-cut'

parser = argparse.ArgumentParser(description="Edit the video. Change resolutioncut, out for specified time.")
parser.add_argument("video", help="input video")
parser.add_argument("-o", f"--output", help="output video; default video{SUFFIX}.mov")
parser.add_argument("-w", f"--width", help="resize output width; [pixels]", type=int)
parser.add_argument("-l", "--length", help="output video length; [sec]", type=float, default=math.inf)
parser.add_argument("-s", "--start", help="start time. [sec]", type=float, default=0.0)
parser.add_argument("-e", "--end", help="end time; [sec]", type=float, default=math.inf)
parser.add_argument("--alpha", help="", type=float, default=1.0)
parser.add_argument("--beta", help="", type=float, default=0.0)
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

# time parameters
start_msec = args.start * 1000
end_msec = args.end * 1000
length_msec = args.length * 1000

perf0 = time.perf_counter()
video.set(cv2.CAP_PROP_POS_MSEC, start_msec)
msec = 0.0
while video.get(cv2.CAP_PROP_POS_MSEC) < end_msec and msec < length_msec:
    ret, frame = video.read()
    if not ret:
        break

    frame = cv2.convertScaleAbs(frame, alpha=args.alpha, beta=args.beta)
    frame = cv2.resize(frame, size)

    output.write(frame)
    msec += 1000/fps

video.release()
output.release()

print(f"done; {time.perf_counter()-perf0:.3f} sec")