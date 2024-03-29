#!/usr/bin/env python3
import os
import time
import math
import argparse
import cv2
import numpy as np

SUFFIX = '-cut'

parser = argparse.ArgumentParser(description="Edit the video. Change resolutioncut, out for specified time.")
parser.add_argument("video", help=f"input video")
parser.add_argument("-o", "--output", help=f"output video; default video{SUFFIX}.mov")
parser.add_argument("-w", "--width", help=f"resize output width; [pixels]", type=int)
parser.add_argument("-l", "--length", help=f"output video length; [sec]", type=float, default=math.inf)
parser.add_argument("-s", "--start", help=f"start time. [sec]", type=float, default=0.0)
parser.add_argument("-e", "--end", help=f"end time; [sec]", type=float, default=math.inf)
parser.add_argument("-r", "--frame-rate", help=f"change frame rate", type=float)
parser.add_argument("--rotate", help=f"", type=float, default=0.0)
parser.add_argument("--crop", help=f"crop; x,y,width,height")
parser.add_argument("--alpha", help=f"", type=float, default=1.0)
parser.add_argument("--beta", help=f"", type=float, default=0.0)
args = parser.parse_args()

# open source video
video = cv2.VideoCapture(args.video)
if not video.isOpened():
    print(f"video open error '{args.video}'")
    exit()

frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# crop rectangle
def conv(s, full):
    if s[-1] == '%':
        return int(float(s[:-1]) * full / 100)
    if '.' in s:
        return int(float(s) * full)
    return int(s)

cx, cy, cw, ch = (0, 0, width, height)
if not args.crop is None:
    cc = args.crop.split(',')
    if len(cc) > 0:
        cx = conv(cc[0], width)
    if len(cc) > 1:
        cy = conv(cc[1], height)
    if len(cc) > 2:
        cw = conv(cc[2], width)
    if len(cc) > 3:
        ch = conv(cc[3], height)

# change resolution
if args.width is None: args.width = width
scale = args.width/cw
size = (args.width, round(ch*scale))

print(f"{args.video} ({width},{height}) x{scale:.2f} -> {args.output} {size}")
print(f"crop ({cx},{cy}) ({cw},{ch})")

# make output video
if args.output is None:
	root, ext = os.path.splitext(args.video)
	args.output = root+SUFFIX+ext
if not args.frame_rate is None:
    fps = args.frame_rate
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
output = cv2.VideoWriter(args.output, fourcc, fps, size)

# time parameters
start_msec = args.start * 1000
end_msec = args.end * 1000
length_msec = args.length * 1000

# affine matrix
cosT = math.cos(math.pi*args.rotate/180)
sinT = math.sin(math.pi*args.rotate/180)
m1 = np.array([[1, 0, -cx-cw/2], 		# centering
               [0, 1, -cy-ch/2],
			   [0, 0, 1]])
m2 = np.array([[cosT,-sinT, 0],			# rotate
               [sinT, cosT, 0],
			   [0, 0, 1]])
m3 = np.array([[1, 0, cx+cw/2],			# un-centering
               [0, 1, cy+ch/2],
			   [0, 0, 1]])
m4 = np.array([[scale, 0, -cx*scale], 	# crop
               [0, scale, -cy*scale],
			   [0, 0, 1]])
m = m4 @ m3 @ m2 @ m1
#print(m)

perf0 = time.perf_counter()
video.set(cv2.CAP_PROP_POS_MSEC, start_msec)
msec = 0.0
while video.get(cv2.CAP_PROP_POS_MSEC) < end_msec and msec < length_msec:
    ret, frame = video.read()
    if not ret:
        break

    frame = cv2.warpAffine(frame, m[:-1], size)
    frame = cv2.convertScaleAbs(frame, alpha=args.alpha, beta=args.beta)

    output.write(frame)
    msec += 1000/fps

video.release()
output.release()

print(f"done; {time.perf_counter()-perf0:.3f} sec")
