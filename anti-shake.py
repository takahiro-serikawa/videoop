#!/usr/bin/env python3
import os
import time
import argparse
import cv2
import numpy as np

SUFFIX = '-a'
DEF_WIDTH = 1280
METHOD = cv2.TM_CCOEFF_NORMED

parser = argparse.ArgumentParser(description=f"movie shake stabilize")
parser.add_argument("video", help=f"source video")
parser.add_argument("-o", "--output", help=f"output video; default video{SUFFIX}.mov")
parser.add_argument("-w", "--width", help=f"output size; default {DEF_WIDTH}", type=int, default=DEF_WIDTH)
parser.add_argument("-t", "--tracking", help=f"tracking range. default 20 [%%]", type=float, default=20)
args = parser.parse_args()

# open source video
video = cv2.VideoCapture(args.video)
frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video.get(cv2.CAP_PROP_FPS))

scale = args.width / width
size = (args.width, round(height * scale))

# create output video
if args.output is None:
    root, ext = os.path.splitext(args.video)
    args.output = root+SUFFIX+ext
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
output = cv2.VideoWriter(args.output, fourcc, fps, size)

print(f"{args.video} ({width}, {height}) x{scale:.2f} -> {args.output} {size}")

r = int(args.tracking * max(width, height) / 100)
print(f"tracking: {r} pixels")
tx, ty = (r, r)
tw, th = (width-2*r, height-2*r)

perf0 = time.perf_counter()
for i in range(frames):
    ret, frame = video.read()
    if ret:
        # make template at first frame
        if i == 0:
            templ = frame[ty:ty+th, tx:tx+tw]

        # calculate daviation
        res = cv2.matchTemplate(frame, templ, METHOD)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        dx = max_loc[0] - tx
        dy = max_loc[1] - ty
        print(f"{i:5}/{frames}:{100*max_val:6.2f}% ({dx:+5},{dy:+5})", end='\r')

        # do adjust
        matrix = np.float32([[scale, 0, -dx*scale],
                             [0, scale, -dy*scale]])
        frame = cv2.warpAffine(frame, matrix, size)

        # add frame to output video
        output.write(frame)

# finalize
video.release()
output.release()

print(f"\ndone; {time.perf_counter()-perf0:.3f} sec")
