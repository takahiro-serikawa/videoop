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
TEMPL_COLOR = (0,255,0)
MATCHED_COLOR = (0,0,255)

parser = argparse.ArgumentParser(description=f"movie shake stabilize")
parser.add_argument("video", help=f"source video")
parser.add_argument("-o", "--output", help=f"output video; default video{SUFFIX}.mov")
parser.add_argument("-w", "--width", help=f"output size; default {DEF_WIDTH}", type=int, default=DEF_WIDTH)
parser.add_argument("-t", "--tracking", help=f"tracking range. default {DEF_TRACKING} [%%]", type=float, default=DEF_TRACKING)
parser.add_argument("--select-roi", help="select ROI on image with mouse", action='store_true')
parser.add_argument("--DEBUG", help="debug option", action='store_true')
parser.add_argument("--auto-mask", help="debug option", action='store_true')
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

if args.DEBUG:
    cv2.namedWindow("templ", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("mask", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("frame", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("res", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    w = 0

perf0 = time.perf_counter()
dx, dy = (0, 0)
mask = None
for i in range(frames):
    ret, frame = video.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # make template at first frame
        if i == 0:
            r = int(args.tracking * max(width, height) / 100)
            q = r//10
            print(f"tracking: {r} ({q}) pixels")
            if args.select_roi:
                cv2.namedWindow("frame", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                tx, ty, tw, th = cv2.selectROI("frame", frame)
            else:
                tx, ty = (r, r)
                tw, th = (width-2*r, height-2*r)

            templ = gray[ty:ty+th, tx:tx+tw]
            mask = np.ones((th, tw), dtype=np.float32)

            if args.DEBUG:
                cv2.imshow("templ", templ)
                cv2.imshow("mask", mask)

                res1 = np.zeros((2*r+1, 2*r+1, 3), np.uint8)

        # calculate daviation
        if tx+dx < q:
            dx = q-tx
        if ty+dy < q:
            dy = q-ty
        sx, sy = (tx+dx, ty+dy) # serach origin
        roi = gray[sy-q:sy+th+q, sx-q:sx+tw+q]
        if args.auto_mask:
            res = cv2.matchTemplate(roi, templ, METHOD, mask=mask)
        else:
            res = cv2.matchTemplate(roi, templ, METHOD)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        dx += max_loc[0] - q
        dy += max_loc[1] - q
        print(f"{i:5}/{frames}:{100*max_val:6.2f}% ({dx:+5},{dy:+5}) {max_loc[0]-q:+3},{max_loc[1]-q:+3}", end='\r')

        # do adjust
        matrix = np.float32([[scale, 0, -dx*scale],
                             [0, scale, -dy*scale]])
        frame = cv2.warpAffine(frame, matrix, size)

        # add frame to output video
        output.write(frame)

        if args.auto_mask:
            mask = gray[ty+dy:ty+dy+th, tx+dx:tx+dx+tw]
            mask = cv2.absdiff(templ, mask)
            ret, mask = cv2.threshold(mask, 25 , 255, cv2.THRESH_BINARY)
            mask = cv2.bitwise_not(mask)

            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)

        if args.DEBUG:
            if args.auto_mask: cv2.imshow("mask", mask)
            
            #res2 = cv2.convertScaleAbs(res, alpha=255.0/(1.0-0.8), beta=-255.0*0.8/(1.0-0.8))
            res2 = cv2.convertScaleAbs(res, alpha=255.0, beta=0.0)
            res2 = cv2.applyColorMap(res2, cv2.COLORMAP_JET)
            #cv2.imshow("res", res2)

            #res1[:] = 255
            res1[sy:sy+2*q+1, sx:sx+2*q+1] = res2
            cv2.imshow("res", res1)
 
            tt = np.float32([[tx, ty, 1], [tx+tw, ty+th, 1]])
            mm = (tt @ matrix.T).astype(int)
            cv2.rectangle(frame, tuple(mm[0]), tuple(mm[1]), MATCHED_COLOR, thickness=3)

            matrix0 = np.float32([[scale, 0, 0],
                                  [0, scale, 0]])
            mm = (tt @ matrix0.T).astype(int)
            cv2.rectangle(frame, tuple(mm[0]), tuple(mm[1]), TEMPL_COLOR, thickness=3)
            cv2.imshow("frame", frame)


            key = cv2.waitKey(w)
            if key in [ord('q'), 27, 3]:    # quit on 'q', ESC, ^C
                break
            if key == ord('s'):             # toggle single step mode
                w = 1-w
            elif key == ord('d'):           # debug mode off
                args.DEBUG = False

# finalize
video.release()
output.release()

print(f"\ndone; {time.perf_counter()-perf0:.3f} sec")
