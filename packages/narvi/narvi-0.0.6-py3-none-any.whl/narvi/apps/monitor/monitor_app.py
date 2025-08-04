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

import json

class MonitorApp:

    def __init__(self, services):
        self.services = services
        self.services.add_session_open_listener(lambda app_name,sid,query_parameters,headers: self.session_open_handler(app_name,sid,query_parameters,headers))
        self.services.add_session_close_listener(lambda sid: self.session_close_handler(sid))
        # whenever admin status is collected, send it to any open clients
        self.services.set_admin_listener(lambda status: self.process_status(status))
        self.status = None

    def process_status(self, status):
        self.status = status
        self.services.send(json.dumps(self.status))

    def session_open_handler(self,app_name,sid,query_parameters,headers):
        self.services.send(json.dumps(self.status),for_session_id=sid)

    def session_close_handler(self,sid,headers):
        pass



