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

import subprocess

class ProcessMetrics:

    @staticmethod
    def get_process_metrics(pid, ps_metrics=["pcpu","pmem","rss"],include_nproc=False, include_children=False):
        # retrieve stats on the engine process and direct child processes using ps

        args = ["ps", "--no-headers", "--pid", str(pid),  "-o", ",".join(ps_metrics)]
        if include_children:
            args += ["--ppid", str(pid)]
        r = subprocess.run(args,stdout=subprocess.PIPE)
        outputs = r.stdout.decode("utf-8").split("\n")

        metric_values = {metric:0 for metric in ps_metrics}
        for output in outputs:
            values = list(filter(lambda s:s,output.split(" ")))
            if len(values) == len(ps_metrics):
                for (ps_metric, value) in zip(ps_metrics,values):
                    metric_values[ps_metric] += float(value)
        if include_nproc:
            metric_values["nproc"] = len(outputs)
        return metric_values

    @staticmethod
    def get_metrics_metadata():
        return {"pcpu": {"min": 0, "max": 100, "colour": "red", "minmax_decimal_places": 1},
             "pmem": {"min": 0, "max": 100, "minmax_display": True, "colour": "blue"},
             "rss": {"min": 0, "max": 100, "minmax_display": True, "colour": "purple"}}
