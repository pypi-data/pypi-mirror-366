# MIT License
#
# Narvi - a simple python web application server
#
# Copyright (C) 2022-2025 Visual Topology Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import threading
import time
import copy

from threading import RLock

class Monitor(threading.Thread):

    def __init__(self, interval_sec=60, retention_sec=3600, admin_data_callback=None):
        super().__init__()
        self.interval_sec = interval_sec
        self.retention = retention_sec // interval_sec if retention_sec >= interval_sec else 1

        self.closed = False
        self.services = {}
        self.metrics = {}
        self.metrics_metadata = {}
        self.admin_data_callback = admin_data_callback
        self.lock = RLock()

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    def track(self, webapp):
        with self:
            self.services[webapp.get_key()] = webapp

    def untrack(self, webapp):
        with self:
            key = webapp.get_key()
            if key in self.services:
                del self.services[key]

    def run(self):
        admin_listeners = set()
        while not self.closed:

            # collect metrics for all running services
            for key, webapp in self.services.items():
                metrics = webapp.get_metrics()

                if metrics is None:
                    metrics = {}
                metrics_metadata = webapp.get_metrics_metadata()
                admin_listener = webapp.get_admin_listener()
                if admin_listener is not None:
                    admin_listeners.add(admin_listener)
                if key not in self.metrics:
                    self.metrics[key] = []
                with self:
                    self.metrics[key].insert(0,[time.time(),metrics])
                    self.metrics_metadata[key] = metrics_metadata
                    # truncate metrics according to retention
                    if len(self.metrics[key]) >= self.retention:
                        self.metrics[key] = self.metrics[key][:self.retention]

            # go through metrics from services that are no longer running
            with self:
                for key in self.metrics:
                    if key not in self.services:
                        self.metrics[key].insert(0, [time.time(), None])

                        if len(self.metrics[key]) >= self.retention:
                            if self.metrics[key][-1][1] is None:
                                # no valid metrics remain - tidy up
                                del self.metrics[key]
                                del self.metrics_metadata[key]
                            else:
                                # truncate metrics according to retention
                                self.metrics[key] = self.metrics[key][:self.retention]

            # push metrics to all listeners
            if len(admin_listeners) > 0:
                if self.admin_data_callback:
                    admin_data = self.admin_data_callback()
                    for admin_listener in admin_listeners:
                        admin_listener(admin_data)

            time.sleep(self.interval_sec)

    def get_metrics(self, last_n=None):
        with self:
            metrics = {}
            for key, values in self.metrics.items():
                metrics[key] = values[:] if last_n is None else values[:last_n]
            return (metrics, copy.copy(self.metrics_metadata))

    def close(self):
        self.closed = True