#!/usr/bin/env python3
import os
import time
import datetime
import glob
import argparse
import cv2
import numpy as np

#DEF_WIDTH = 1280
DEF_FRAME_RATE = 30

parser = argparse.ArgumentParser(description="make time-lapse video from image files")
parser.add_argument("files", help="input directories or image files", nargs='+')
parser.add_argument("-o", "--output", help="output video")
parser.add_argument("-w", "--width", help="change output video size; default same as input", type=int)
parser.add_argument("-r", "--frame-rate", help=f"frame rate; default {DEF_FRAME_RATE}fps", type=float, default=DEF_FRAME_RATE)
parser.add_argument("-t", "--timestamp", help="draw timestamp", default="%Y-%m-%d %I:%M %p")
parser.add_argument("--flash-adjust", help="flash adjust", action='store_true')
args = parser.parse_args()

# input filenames
files = []
for f in args.files:
    if os.path.isdir(f):
        ff = glob.glob(os.path.join(f, "**/*.*"), recursive=True)
        ff = [p for p in ff
          if os.path.splitext(p)[1].lower() in ['.jpg']]
        files += sorted(ff)
    else:
        files.append(f)

perf0 = time.perf_counter()

for i, file in enumerate(files):
    image = cv2.imread(file)

    if i == 0:
        # determine video size at first loop
        height, width, channels = image.shape[:3]
        if args.width is None:
            args.width = width
        scale = args.width/width
        size = (args.width, round(height*scale))

        # output video
        if args.output is None:
            args.output = os.path.splitext(file)[0]+".mov"
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        output = cv2.VideoWriter(args.output, fourcc, args.frame_rate, size)
        print(f" -> {args.output} {size}, {args.frame_rate}fps")

    print(f"{i:6}/{len(files)}: {file}", end='')

    image = cv2.resize(image, size)

    if args.flash_adjust:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        flatten = np.array(gray).flatten()
        mean = flatten.mean()
        if i == 0:
            mean0 = mean    # reference level
        elif mean > 0:
            image = cv2.convertScaleAbs(image, alpha=mean0/mean, beta=0.0)
            print(f", alpha={mean0/mean:.3f}", end='')

    # draw timestamp
    d = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
    cv2.putText(image,
        d.strftime(args.timestamp),
        (size[0]-400, size[1]-20),
        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
        (255,255,255),
        thickness=1,
        lineType=cv2.LINE_AA)

    # add image as video frame
    output.write(image)

    print()

# finalize
output.release()

print(f"done; {time.perf_counter()-perf0:.3f} sec")
