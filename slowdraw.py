#!/usr/bin/env python
''' Slowdraw watches an image file and makes animations out of the changes

'''
import opencv
import logging
import time
from watchdog.observers import Observer

parser = argparse.ArgumentParser(description='slowdraw')
parser.add_argument('path', help='Path of file to watch')
args = parser.parse_args()



logging.basicConfig(stream = sys.stderr, level=logging.INFO)

load_queue = []

class ModListener(watchdog.events.FileSystemEventHandler):
    def __init__(self):
        super(self)
        self.queue = []

    def on_modified(self, event):
        logging.info("Modified: "+event.src_path)
        self.queue.append(event.src_path)
        
mod_listener = ModListener()
observer = Observer()
observer.schedule(mod_listener, args.path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
observer.join()



