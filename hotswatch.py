import sys
import time
import logging
import os
import datetime
import importlib
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

# Plugins
from os.path import dirname, basename, isfile
import glob
from notifier import Notifier

# Import Custom Classes
import config as cfg

class ConsoleLogger():
    @staticmethod
    def log(message):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print("[" + time + "] " + message)

class HOTSTempReplayHandler(PatternMatchingEventHandler):
    patterns = ["*.battlelobby"]

    def __init__(self):
        super().__init__()
        self.old = 0

    def process(self, event):
        # Check this is a new event, and not a duplicate one
        statbuf = os.stat(event.src_path)
        new = statbuf.st_mtime

        if (new - self.old) > 0.5:           
            ConsoleLogger.log("Game detected (" + event.event_type + ")")
            Notifier().triggerNotificationThreaded()

        self.old = new

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)
        

if __name__ == "__main__":
    print("[Watching] " + cfg.REPLAYDIR)

    event_handler = HOTSTempReplayHandler()
    observer = Observer()
    observer.schedule(event_handler, cfg.REPLAYDIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()