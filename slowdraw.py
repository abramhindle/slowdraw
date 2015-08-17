#!/usr/bin/env python
''' Slowdraw watches an image file and makes animations out of the changes

'''
import sys
import cv2
import cv
import logging
import time
import argparse
import watchdog
import os.path
import pickle
import math
from watchdog.observers import Observer

parser = argparse.ArgumentParser(description='slowdraw')
parser.add_argument('path', help='Path of file to watch')
args = parser.parse_args()



logging.basicConfig(stream = sys.stderr, level=logging.INFO)

load_queue = []

class ModListener(watchdog.events.FileSystemEventHandler):
    def __init__(self, handler):
        super(ModListener, self).__init__()
        self.queue = []
        self.handler = handler;

    def on_modified(self, event):
        logging.info("Modified: "+event.src_path)
        if (event.src_path == args.path):
            logging.info( "Recorded Modified: " + event.src_path )
            self.queue.append( event.src_path )
            self.handler( event.src_path )
        

frame1 = cv2.imread(args.path)
w,h,_ = frame1.shape
frames = [frame1]
curr_frame = 0
done = False

def handle_frame(fname):
    newframe = cv2.imread(fname)
    frames.append(newframe)

mod_listener = ModListener(handle_frame)
observer = Observer()
directory = os.path.dirname(args.path)
observer.schedule(mod_listener, directory, recursive=True)
observer.start()

maxtime = 1000/2
mintime = 1000/30

#           2     4    8     16    32    64     128   256    512
maxtimes = [2000,2000,2000, 1000, 1000, 1000,  1000, 1000,  1000, 1000]
mintimes = [1000,1000,1000, 1000,  500,  200,   100,   50,    50,   50]

def get_times(nframes):
    index = int(math.ceil(math.log(nframes) / math.log(2)))
    if index >= len(maxtimes):
        return maxtimes[-1], mintimes[-1]
    else:
        return maxtimes[index], mintimes[index]
    

def scalexp(v,mint,maxt,scale=5):
    mine = math.exp(1.0)/math.exp(scale)
    maxe = 1.0
    vs = math.exp(1 + (scale-1)*v)/math.exp(scale)
    vs = (vs - mine)/(maxe - mine)
    return vs * (maxt - mint) + mint

def linscale(v,mint,maxt):
    return v*(maxt-mint) + mint

fourcc = cv2.cv.FOURCC(*'XVID')
writer = cv2.VideoWriter("slowdraw.avi",fourcc,30,(h,w),1)
frametime = 1000.0/30.0
try:
    while not done:
        framen = curr_frame % len(frames)
        frame = frames[curr_frame % len(frames)]
        cv2.imshow('slowdraw', frame  )
        tmaxtime, tmintime = get_times(len(frames))        
        wait = scalexp( (framen + 1.0) / len(frames) , tmintime,tmaxtime)
        print(wait,tmaxtime,tmintime)
        curr_frame += 1
        for i in range(0,max(1,int(wait/frametime))):
            print("Writing frame %s %s %s" % (i,wait,wait/frametime))
            writer.write(frame)
        # TODO: fix the wait time
        k = cv2.waitKey(int(wait)) & 0xff
        if k == 27:
            done = True
            continue

except KeyboardInterrupt:
    observer.stop()

# pickle.dump(frames,file('slowdraw.pkl','wb'))

writer.release()

observer.stop()
observer.join()




