# Telesto
# Copyright (C) 2025  Visual Topology Ltd
#
# MIT License
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

import os
import json
import shutil
import logging
import zipfile


from telesto.utils.telesto_utils import TelestoUtils

class TopologyDirectory:

    package_metadata = []

    def __init__(self, webapp_services, workspace_path, packages, applications, templates, topology_update_callback, get_topology_statuses_callback):
        self.logger = logging.getLogger("TopologyDirectory")
        self.webapp_services = webapp_services
        self.applications = applications
        self.workspace_folder = workspace_path
        self.package_urls = []
        self.webapp_services.add_message_listener(lambda msg, sid: self.recv(msg, sid))
        self.webapp_services.add_session_open_listener(lambda app_name, sid, query_parameters, headers: self.handle_session_open(app_name, sid,query_parameters,headers))
        self.templates = templates
        for package_id in packages:
            self.package_urls.append(f"schema/{package_id}")
        self.topology_update_callback = topology_update_callback
        self.get_topology_statuses_callback = get_topology_statuses_callback

    def recv(self, msg, from_session_id):
        o = json.loads(msg)
        if o["action"] == "remove_topology":
            topology_id = o["topology_id"]
            self.remove_topology(topology_id)
            if self.topology_update_callback:
                self.topology_update_callback("remove",topology_id)
        elif o["action"] == "create_topology":
            topology_id = o["topology_id"]
            from_topology_id = o.get("from_topology_id",None)
            self.create_topology(topology_id, from_topology_id)
            if self.topology_update_callback:
                self.topology_update_callback("create",topology_id)
        elif o["action"] == "reload_topology":
            topology_id = o["topology_id"]
            self.reload_topology(topology_id)
            if self.topology_update_callback:
                self.topology_update_callback("reload",topology_id)

    def create_topology(self, topology_id, from_topology_id=None):
        to_folder = os.path.join(self.workspace_folder, topology_id)
        if from_topology_id:
            from_folder = os.path.join(self.workspace_folder, from_topology_id)
            if os.path.isdir(from_folder):
                shutil.copytree(from_folder, to_folder)
                return
            if from_topology_id in self.templates:
                TopologyDirectory.load_template(self.templates[from_topology_id]["import_path"], to_folder)
                return
            self.logger.warning(f"Unable to create {topology_id} from {from_topology_id}, creating an empty topology instead...")
        # create an empty topology
        path = os.path.join(to_folder, "topology.json")
        if not os.path.exists(path):
            folder = os.path.dirname(path)
            os.makedirs(folder, exist_ok=True)
            with open(path, "w") as f:
                f.write(json.dumps({"nodes": {}, "links": {}, "metadata": {}}, indent=4))

    def remove_topology(self, topology_id):
        if os.path.exists(os.path.join(self.workspace_folder, topology_id)):
            shutil.rmtree(os.path.join(self.workspace_folder, topology_id))

    def reload_topology(self, topology_id):
        self.remove_topology(topology_id)
        if topology_id in self.templates:
            topology_folder = os.path.join(self.workspace_folder, topology_id)
            TopologyDirectory.load_template(self.templates[topology_id]["import_path"],topology_folder)
        else:
            # no template to reload
            self.logger.warning(f"Unable to reload {topology_id}, no template exists.  Creating an empty topology instead...")
            self.create_topology(topology_id)

    def handle_session_open(self, app_name, sid, query_parameters, headers):
        print(json.dumps(headers))
        topologies = TelestoUtils.list_topologies(self.workspace_folder)
        # identify which topologies have a template
        for topology_id in topologies:
            if topology_id in self.templates:
                topologies[topology_id]["metadata"]["has_template"] = True

        statuses = self.get_topology_statuses_callback()

        for topology_id in topologies:
            if topology_id in statuses:
                running = len(statuses[topology_id]) > 0
            else:
                running = False
            topologies[topology_id]["status"] = { "running": running }

        payload = {"topologies":topologies,"applications":self.applications}
        self.webapp_services.send(json.dumps(payload), for_session_id=sid)

    @staticmethod
    def load_template(import_path, topology_folder):
        os.makedirs(topology_folder)
        zip_parent_package = ".".join(import_path.split(".")[:-2])
        zip_filename = ".".join(import_path.split(".")[-2:])
        zip_path = TelestoUtils.get_path_of_resource(zip_parent_package, zip_filename)
        zf = zipfile.ZipFile(zip_path, mode="r")
        zf.extractall(topology_folder)

