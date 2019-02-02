import sys
import time
import logging
import os
import datetime
import importlib
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemMovedEvent
from watchdog import events

import csv

DIRTOWATCH = os.environ['TMP']
EVENTS = []

# Debug script used to log all events to a given directory

class ChangeEvent():
    time = None

    event = None
    event_type = None
    is_directory = None
    src_path = None
    dst_path = None

    def __init__(self, time, event):
        self.setTime(time)
        self.setEvent(event)

    def setTime(self, time = datetime.datetime.now()):
        self.time = time

    def setEvent(self, event):
        self.event = event
        self.event_type = event.event_type
        self.is_directory = event.is_directory
        self.src_path = event.src_path

        if(type(event) == FileSystemMovedEvent):
            self.dst_path = event.dest_path

    def toString(self):
        return "{0}\t{1}\t{2}\t{3}".format(self.time.strftime("%Y-%m-%d %H:%M:%S"), self.event_type, self.src_path, self.dst_path)

    def toCSV(self):
        return (self.time.strftime("%Y-%m-%d %H:%M:%S"), self.event_type, self.src_path, self.dst_path)

# class ConsoleLogger():
#     @staticmethod
#     def log(message):
#         time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#         print("[" + time + "] " + message)

class FileWatcher(PatternMatchingEventHandler):
    patterns = ["*"]

    def __init__(self):
        super().__init__()
        
    def process(self, event):
        event = ChangeEvent(datetime.datetime.now(), event)
        EVENTS.append(event)
        print(event.toString())

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


if __name__ == "__main__":
    print("[Watching] " + DIRTOWATCH)

    event_handler = FileWatcher()
    observer = Observer()
    observer.schedule(event_handler, DIRTOWATCH, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("ending... writing to disk")
        with open('C:\\filemodifications.csv', mode='w') as outfile:
            writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for event in EVENTS:
                print(event.toCSV())
                writer.writerow(event.toCSV())

    observer.join()