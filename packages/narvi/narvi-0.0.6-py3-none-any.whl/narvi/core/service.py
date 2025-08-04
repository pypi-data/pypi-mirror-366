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

import copy
import os.path
import uuid
from threading import RLock
import mimetypes
import os
import logging
import datetime
import fnmatch
import json

from narvi.core.session import Session
from narvi.web_servers.webserver_factory import WebServerFactory
from narvi.utils.resource_loader import ResourceLoader
from narvi.core.webapp import WebApp
from narvi.core.registered_app import RegisteredApp
from narvi.core.registered_service import RegisteredService
from narvi.core.monitor import Monitor

class Service:
    # one "singleton" instance of the Service class in this process
    service = None

    def __init__(self, host: str = "localhost", port: int = 8999,
                 base_path: str = "",
                 web_server_type="tornado", admin_path=None,
                 monitoring_interval:int = None,
                 monitoring_retention: int = None):
        """
        Create a Narvi application server instance

        Args:
            host: the hostname or IP address that the service will listen at
            port: the port that the service will listen at
            base_path: mount all narvi apps and resources at this base path
            web_server_type: which web server to use - either "tornado" or "builtin"
            admin_path: path to listen for admin_requests
            monitoring_interval: the interval in seconds to poll webapps for metrics, or None to turn off monitoring
            monitoring_retention: discard metrics collected more than this many seconds ago, or None to never discard
        """
        self.host = host
        self.port = port

        self.base_path = base_path
        self.resource_roots = { "narvi": "narvi/static" }
        self.admin_path = admin_path
        self.registered_apps = {} # (workspace, app_name) => RegisteredApp
        self.registered_services = {}  # (workspace, app_service_name) => ApplicationService
        self.redirects = {} # url => (workspace, app_name)

        self.logger = logging.getLogger(self.__class__.__name__)

        # service state and book-keeping
        self.lock = RLock()
        self.app_instances = {}  # (workspace, app_service_name,service_id,[session_id]) => app instance
        self.sessions = {}  # (workspace, app_name,service_id) => session_id => session
        self.service_choosers = {} # (workspace,app_name) => service_chooser_app_name

        self.server = WebServerFactory.create_webserver(web_server_type, host, port)

        self.server.attach_handler("GET", self.base_path + "/$workspace/$app/index.html",
                            lambda *args, **kwargs: self.app_html_handler(*args, **kwargs))

        self.server.attach_handler("GET", self.base_path + "/$workspace/$app/$service_id/index.html",
                            lambda *args, **kwargs: self.app_html_handler(*args, **kwargs))

        self.server.attach_ws_handler(self.base_path + "/$workspace/$app/$service_id/connect",
                            lambda *args, **kwargs: self.ws_handler(*args, **kwargs))

        self.server.attach_handler("GET", self.base_path + "/$workspace/$app/$service_id/status",
                                      lambda *args, **kwargs: self.status_handler(*args, **kwargs))

        self.server.attach_handler("GET", self.base_path + "/$workspace/$app/$service_id/$$resource",
                            lambda *args, **kwargs: self.app_resource_handler(*args, **kwargs))

        if self.admin_path:
            self.server.attach_handler("GET", self.admin_path, lambda *args, **kwargs: self.get_status())

        self.default_app_name = None

        Service.service = self

        if monitoring_interval is not None:
            self.monitor = Monitor(admin_data_callback=lambda: self.get_admin_data(),
                               interval_sec=monitoring_interval, retention_sec=monitoring_retention)
        else:
            self.monitor = None

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    def app_html_handler(self, path, headers, path_parameters, query_parameters, request_body):
        workspace = path_parameters["workspace"]
        app_name = path_parameters["app"]

        registered_app:RegisteredApp = self.registered_apps.get((workspace,app_name),None)
        if registered_app is None:
            return (404, b'NOT FOUND', "text/plain", {})

        registered_service: RegisteredService = registered_app.application_service

        service_id = path_parameters.get("service_id",None)
        if service_id is None:
            service_id = registered_service.fixed_service_id
            if service_id:
                return (307, "Temporary Redirect", "text/plain",{"Location": f"{service_id}/index.html"})
            else:
                chooser_app_name = registered_app.get_service_chooser_app_name()
                if chooser_app_name:
                    return (307, "Temporary Redirect", "text/plain", {"Location": f"../{chooser_app_name}/index.html"})
                else:
                    return (404, b'NOT FOUND', "text/plain", {})

        if not registered_service.validate_service_id(service_id, self.logger):
            chooser_app_name = registered_app.get_service_chooser_app_name()
            if chooser_app_name:
                return (307, "Temporary Redirect", "text/plain", {"Location": f"../../{chooser_app_name}/index.html"})
            else:
                return (404, b'NOT FOUND', "text/plain", {}) # or should be Forbidden?

        content = registered_app.get_app_html()

        if content is None:
            return (404, b'NOT FOUND', "text/html", {})

        return (200, content, "text/html", {})

    def app_request_handler(self, workspace, app_name, service_id, session_id, method, handler_id, path, headers, path_parameters, query_parameters, request_body):

        registered_app = self.registered_apps.get((workspace,app_name), None)
        if registered_app is None:
            return (404, b'NOT FOUND', "text/plain", {})

        app_service_name = registered_app.get_application_service_name()
        registered_service = registered_app.application_service

        # only shared services can handle requests
        if not registered_service.is_shared_service:
            return (404, b'NOT FOUND', "text/plain", {})

        if not registered_service.validate_service_id(service_id, self.logger):
            return (404, b'NOT FOUND', "text/plain", {})  # or should be Forbidden?

        if session_id:
            key = (workspace, app_service_name, service_id, session_id)
        else:
            key = (workspace, app_service_name, service_id)

        with self:
            app = self.app_instances.get(key,None)

        if app is not None:
            return app.dispatch_handle_request(method, handler_id, path_parameters, query_parameters, headers, request_body)

        return (404, b"Not Found", "text/plain", {})

    def app_resource_handler(self, request_path, headers, path_parameters, query_parameters, request_body):
        workspace = path_parameters["workspace"]
        app_name = path_parameters["app"]
        service_id = path_parameters["service_id"]
        registered_app:RegisteredApp = self.registered_apps.get((workspace,app_name), None)
        if registered_app is None:
            return (404, b'NOT FOUND', "text/plain", {})

        if not registered_app.application_service.validate_service_id(service_id, self.logger):
            return (404, b'NOT FOUND', "text/plain", {})  # or should be Forbidden?

        resource_url = path_parameters["resource"]
        return registered_app.load_resource(resource_url)

    def ws_handler(self, session_id, sender, path, path_parameters, query_parameters, headers):
        try:
            workspace = path_parameters["workspace"]
            app_name = path_parameters["app"]
            registered_app:RegisteredApp = self.registered_apps.get((workspace,app_name), None)
            registered_service:RegisteredService = registered_app.application_service

            if registered_app is None:
                return (404, b'NOT FOUND', "text/plain", {})

            service_id = path_parameters["service_id"]
            if not registered_service.validate_service_id(service_id, self.logger):
                return (404, b'NOT FOUND', "text/plain", {})  # or should be Forbidden?

            app_service_name = registered_service.app_service_name
            app_parameters = registered_app.get_app_parameters()

            if registered_service.is_shared_service:
                key = (workspace, app_service_name, service_id)
            else:
                key = (workspace, app_service_name, service_id, session_id)

            def close_listener():
                with self:
                    app = self.app_instances[key]
                    if self.monitor is not None:
                        self.monitor.untrack(app)
                    del self.app_instances[key]

            with self:
                if key not in self.app_instances:
                    self.logger.info(f"starting service: {service_id}")
                    app = registered_service.constructor_fn(service_id)
                    app.add_app_close_listener(close_listener)
                    app.start()
                    self.app_instances[key] = app
                    if self.monitor is not None:
                        self.monitor.track(app)
                else:
                    app = self.app_instances[key]

            logging.getLogger("narvi").info(f"Opening session {app_name}/{service_id}/{session_id}")
            s = Session(app_name, app_parameters, session_id, sender, app, query_parameters, headers,
                        lambda: self.close_session(workspace, app_name, service_id, session_id))
            with self:
                if key not in self.sessions:
                    self.sessions[key] = {}
                self.sessions[key][session_id] = s
            return s
        except Exception as ex:
            self.logger.exception("ws_handler")
            return None

    def status_handler(self, request_path, headers, path_parameters, query_parameters, request_body):
        try:
            workspace = path_parameters["workspace"]
            app = path_parameters["app"]
            service_id = path_parameters["service_id"]

            key = (workspace, app, service_id)

            with self:
                if key not in self.app_instances:
                    return (404, b'NOT FOUND', "text/plain", {})
                else:
                    app = self.app_instances[key]
                    elapsed_time = datetime.datetime.now() - app.get_start_time()
                    uptime_secs = int(elapsed_time.total_seconds())
                    session_count = 0
                    if key in self.sessions:
                        session_count = len(self.sessions[key])
                    status = {
                        "uptime": uptime_secs,
                        "session_count": session_count
                    }
                    return (200, json.dumps(status).encode(), "application/json", {})

        except Exception as ex:
            self.logger.exception("status_handler")
            return None


    def close_session(self, workspace, app_name, service_id, session_id):
        logging.getLogger("narvi").info(f"Closing session {workspace}/{app_name}/{session_id}")
        registered_app: RegisteredApp = self.registered_apps.get((workspace, app_name), None)
        registered_service: RegisteredService = registered_app.application_service
        if registered_service.is_shared_service:
            key = (workspace, registered_service.app_service_name, service_id)
        else:
            key = (workspace, registered_service.app_service_name, service_id, session_id)

        with self:
            if key in self.sessions:
                if session_id in self.sessions[key]:
                    del self.sessions[key][session_id]
                    if len(self.sessions[key]) == 0:
                        del self.sessions[key]

    def register_service(self, workspace, app_service_name, app_cls_name, app_parameters, fixed_service_id=None,
                     shared_service=True, service_id_validator=lambda service_id: True, idle_timeout=3600):

        def constructor_fn(service_id):
            app_id = str(uuid.uuid4())
            webapp = WebApp(workspace=workspace, app_name=app_service_name, app_id=app_id, app_cls_name=app_cls_name, app_parameters=app_parameters,
                register_request_handler_callback=lambda app_name, handler_pattern, method, service_id, session_id:
                    self.register_request_handler(workspace, handler_pattern, method,
                                                    app_name, service_id, session_id),
                unregister_request_handler_callback=lambda handler_id: self.server.detach_handler(handler_id),
                            service_id=service_id)
            if shared_service:
                if fixed_service_id is None:
                    webapp.set_idle_timeout(idle_timeout)
            else:
                webapp.set_close_on_session_end()
            return webapp

        registered_service = RegisteredService(constructor_fn=constructor_fn, workspace=workspace,
                                  app_service_name=app_service_name, app_cls_name=app_cls_name,
                                  app_parameters=copy.deepcopy(app_parameters),
                                  fixed_service_id=fixed_service_id,
                                  is_shared_service=shared_service,
                                  service_id_validator=service_id_validator)

        self.registered_services[(workspace, app_service_name)] = registered_service

        return registered_service

    def register_app(self, app_name, application_service, app_parameters={},
                     resource_roots={}, service_chooser_app_name=None):
        registered_app = RegisteredApp(app_name=app_name, application_service=application_service,
                                       app_parameters=app_parameters,
                                       resource_roots=copy.deepcopy(resource_roots),
                                       service_chooser_app_name=service_chooser_app_name)
        self.registered_apps[(application_service.workspace,app_name)] = registered_app

        return self

    def register_redirect(self, from_url, to_workspace, to_app):
        self.server.add_redirect(from_url, self.base_path+"/"+to_workspace+"/"+to_app+"/index.html")
        self.redirects[from_url] = (to_workspace, to_app)

    def register_request_handler(self, workspace, handler_pattern, method, app_name, service_id, session_id):
        with self:
            if session_id:
                service_pattern = self.base_path + f"/{workspace}/{app_name}/{service_id}/session/{session_id}/"+handler_pattern
            else:
                service_pattern = self.base_path + f"/{workspace}/{app_name}/{service_id}/"+handler_pattern

            handler_id = self.server.attach_handler(method,
                                       service_pattern,
                                       lambda *args, **kwargs: self.app_request_handler(workspace, app_name, service_id, session_id, method, handler_id, *args, **kwargs))
        return handler_id

    def get_url(self, workspace, app_name):
        return f"http://{self.host}:{self.port}{self.base_path}/{workspace}/{app_name}/index.html"

    def get_summary(self):
        summary = []
        if self.admin_path:
            summary.append(("", "admin", "http://%s:%d%s" % (self.host, self.port, self.admin_path)))

        for (workspace,app_name) in self.registered_apps:
            registered_app = self.registered_apps[(workspace,app_name)]
            registered_service = registered_app.application_service
            if registered_service.fixed_service_id or registered_app.get_service_chooser_app_name():
                url = self.get_url(workspace,app_name)
                summary.append((workspace, app_name, url))

        for url in self.redirects:
            workspace, app_name = self.redirects[url]
            url = f"http://{self.host}:{self.port}{url}"
            summary.append((workspace, app_name, url))

        return summary

    def get_app(self, name):
        return self.app_instances.get(name, None)

    def run(self, callback):
        if self.monitor:
            self.monitor.start()
        for (workspace, app_service_name) in self.registered_services:
            registered_service = self.registered_services.get((workspace,app_service_name))
            service_id = registered_service.fixed_service_id

            if service_id and registered_service.is_shared_service:
                key = (workspace, app_service_name, service_id)

                with self:
                    if key not in self.app_instances:
                        app = registered_service.constructor_fn(service_id)
                        app.start()
                        self.app_instances[key] = app
                        if self.monitor is not None:
                            self.monitor.track(app)

        self.server.run(callback)

    def restart_service(self, workspace, app_service_name, service_id):
        self.stop_service(workspace, app_service_name, service_id)
        # TODO now restart services with a fixed service id?

    def stop_service(self, workspace, app_service_name, service_id):
        key = (workspace, app_service_name, service_id)
        with self:
            if key in self.app_instances:
                self.logger.info(f"stopping service: {workspace}/{app_service_name}/{service_id}")
                app = self.app_instances[key]
                app.close()
                # the close listener will remove the app from self.app_instances

    def get_admin_data(self, for_workspace=None):
        with self:
            metrics, metrics_metadata = self.monitor.get_metrics() if self.monitor is not None else ({}, {})

            workspaces = {}
            for (workspace, app_service_name) in self.registered_services:
                if for_workspace is not None and workspace != for_workspace:
                    continue
                if workspace not in workspaces:
                    workspaces[workspace] = {}
                workspaces[workspace][app_service_name] = { "instances": {}, "apps": [] }

            for key in self.app_instances:

                workspace = key[0]
                if for_workspace is not None and workspace != for_workspace:
                    continue
                app_service_name = key[1]
                service_id = key[2]

                app = self.app_instances[key]

                elapsed_time = datetime.datetime.now() - app.get_start_time()
                instance_info = {
                    "uptime":  int(elapsed_time.total_seconds())
                }

                sessions = {}

                if key in self.sessions:
                    for session_id in self.sessions[key]:
                        session = self.sessions[key][session_id]
                        elapsed_time = datetime.datetime.now() - session.get_start_time()
                        sessions[session_id] = {
                            "app_name": session.app_name,
                            "uptime": int(elapsed_time.total_seconds())
                        }

                instance_info["sessions"] = sessions
                if (workspace, app_service_name, service_id) in metrics:
                    instance_info["metrics"] = metrics[(workspace, app_service_name, service_id)]
                if (workspace, app_service_name, service_id) in metrics_metadata:
                    instance_info["metrics_metadata"] = metrics_metadata[(workspace, app_service_name, service_id)]

                if service_id not in workspaces[workspace][app_service_name]["instances"]:
                    workspaces[workspace][app_service_name]["instances"][service_id] = []
                workspaces[workspace][app_service_name]["instances"][service_id].append(instance_info)

            if for_workspace is not None:
                return workspaces.get(for_workspace,{})

            for (workspace, app_name) in self.registered_apps:
                registered_app = self.registered_apps[(workspace, app_name)]
                service_name = registered_app.application_service.app_service_name
                if workspace not in workspaces:
                    workspaces[workspace] = {}
                if service_name not in workspaces[workspace]:
                    workspaces[workspace][service_name] = { "instances":[], "apps":[] }
                workspaces[workspace][service_name]["apps"].append({"app_name":app_name})

            return workspaces

    def get_status(self):
        return (200, json.dumps(self.get_admin_data()).encode("utf-8"), "application/json", {})

    def close(self):
        # if the monitor is enabled, close it
        if self.monitor is not None:
            self.monitor.close()
            self.monitor.join()
        self.server.close()

