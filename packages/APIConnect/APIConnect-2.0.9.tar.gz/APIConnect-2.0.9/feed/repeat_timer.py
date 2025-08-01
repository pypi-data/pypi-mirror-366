import threading
import time

class RepeatedTimer(object):
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, interval, function):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.interval = interval
                cls._instance.function = function
                cls._instance.thread = threading.Timer(cls._instance.interval, cls._instance.run)
                cls._instance.active = False
                cls._instance.paused = False
                cls._instance.resume_event = threading.Event()
            return cls._instance

    def run(self):
        while self.active:
            self.resume_event.wait(self.interval)
            if self.active and not self.paused:
                self.function()
        self.thread = threading.Timer(self.interval, self.run)
        self.thread.start()

    def start(self):
        with self._instance_lock:
            if not self.active:
                self.active = True
                self.thread.start()

    def stop(self):
        with self._instance_lock:
            self.active = False
            self.thread.cancel()

    def pause(self):
        with self._instance_lock:
            if self.active and not self.paused:
                self.paused = True

    def resume(self):
        with self._instance_lock:
            if self.active and self.paused:
                self.paused = False
                self.resume_event.set()
                self.resume_event.clear()

    def isTimerActive(self):
        return self.active

    def isTimerPaused(self):
        return self.paused
