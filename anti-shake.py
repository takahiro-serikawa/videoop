#!/usr/bin/env python3
import os
import time
import argparse
import cv2
import numpy as np

SUFFIX = '-a'
DEF_WIDTH = 1280
DEF_TRACKING = 20
METHOD = cv2.TM_CCOEFF_NORMED

parser = argparse.ArgumentParser(description=f"movie shake stabilize")
parser.add_argument("video", help=f"source video")
parser.add_argument("-o", "--output", help=f"output video; default video{SUFFIX}.mov")
parser.add_argument("-w", "--width", help=f"output size; default {DEF_WIDTH}", type=int, default=DEF_WIDTH)
parser.add_argument("-t", "--tracking", help=f"tracking range. default {DEF_TRACKING} [%%]", type=float, default=DEF_TRACKING)
parser.add_argument("--select-roi", help="select ROI on image with mouse", action='store_true')
args = parser.parse_args()

# open source video
video = cv2.VideoCapture(args.video)
frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

scale = args.width / width
size = (args.width, round(height * scale))

# create output video
if args.output is None:
    root, ext = os.path.splitext(args.video)
    args.output = root+SUFFIX+ext
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
output = cv2.VideoWriter(args.output, fourcc, fps, size)

print(f"{args.video} ({width}, {height}) x{scale:.2f} -> {args.output} {size}")

perf0 = time.perf_counter()
for i in range(frames):
    ret, frame = video.read()
    if ret:
        # make template at first frame
        if i == 0:
            r = int(args.tracking * max(width, height) / 100)
            print(f"tracking: {r} pixels")
            if args.select_roi:
                cv2.namedWindow("frame", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                tx, ty, tw, th = cv2.selectROI("matched", frame)
            else:
                tx, ty = (r, r)
                tw, th = (width-2*r, height-2*r)

            templ = frame[ty:ty+th, tx:tx+tw]

        # calculate daviation
        roi = frame[ty-r:ty+th+r, tx-r:tx+tw+r]
        res = cv2.matchTemplate(roi, templ, METHOD)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        dx = max_loc[0] - r
        dy = max_loc[1] - r
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
