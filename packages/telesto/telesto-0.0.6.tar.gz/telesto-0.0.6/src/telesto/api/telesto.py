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
import logging
import sys
import importlib.metadata

from narvi.api.server import NarviServer
from hyrrokkin.execution_manager.process_runner import ProcessRunner
from telesto.app_services.topology_directory import TopologyDirectory
from telesto.utils.telesto_utils import TelestoUtils
from narvi.utils.resource_loader import ResourceLoader


def dict2toml(name, f, d):
    count = 0
    for key, value in d.items():
        if not isinstance(value, dict):
            if count == 0:
                f.write(f'\n[{name}]\n\n')
            f.write(f'{key} = {json.dumps(value)}\n')
            count += 1

    for key, value in d.items():
        if isinstance(value, dict):
            dict2toml(name + "." + key, f, value)

DESIGNER_APP_NAME = "topology_designer"
DIRECTORY_APP_NAME = "topology_directory"

class TelestoWorkspace:

    def __init__(self, telesto, workspace_id, configuration):
        self.telesto = telesto
        self.logger = logging.getLogger(f"telesto[{workspace_id}]")
        self.logger.info(f"Creating workspace {workspace_id}")
        self.workspace_id = workspace_id
        self.workspace_name = configuration.get("workspace_name","")
        self.workspace_description = configuration.get("workspace_description", "")
        self.workspace_path = configuration.get("workspace_path", ".")

        self.applications = configuration.get("application", {})

        self.skadi_options = {}
        self.package_lists = {}

        self.server = None

        self.skadi_options = configuration.get("skadi_options", {})
        self.skadi_options["workspace_id"] = workspace_id

        self.package_list = configuration.get("packages", [])

        if len(self.package_list) == 0:
            eps = importlib.metadata.entry_points()
            for (name, ep_list) in eps.items():
                if name == "telesto_package":
                    for ep in ep_list:
                        if ep.value not in self.discovered_packages:
                            self.package_list.append(ep.value)

        if len(self.package_list):
            for package_id in self.package_list:
                self.logger.info(f"\tLoading package {package_id}")
        else:
            self.logger.warning(f"\tNo packages loaded for workspace {workspace_id}")

        self.in_process = configuration.get("in_process", False)

        self.hyrrokkin_options = configuration.get("hyrrokkin_options", {})

        self.templates = configuration.get("templates", {})

        self.package_folders = {}
        self.packages = {}

        for package_resource in self.package_list:
            package_folder = TelestoUtils.get_path_of_resource(package_resource)

            schema_path = os.path.join(package_folder, "schema.json")
            # check package can be loaded
            try:
                with open(schema_path) as f:
                    o = json.loads(f.read())
                    package_id = o["id"]
            except:
                self.logger.error(f"Unable to load package {package_resource} from {schema_path}")
                sys.exit(0)
            self.package_folders[package_id] = package_folder
            self.packages[package_id] = {"package": package_resource}

    def get_skadi_options(self):
        options = {}
        options.update(self.telesto.get_skadi_options())
        options.update(self.skadi_options)
        return options

    def get_hyrrokkin_options(self):
        options = {}
        options.update(self.telesto.get_hyrrokkin_options())
        options.update(self.hyrrokkin_options)
        return options

    def get_resource_roots(self, from_roots={}):

        telesto_static_folder = TelestoUtils.get_path_of_resource("telesto.static")
        narvi_static_folder = TelestoUtils.get_path_of_resource("narvi.static")

        apps_common_folder = TelestoUtils.get_path_of_resource("telesto.apps.common")
        resource_roots = {}
        resource_roots[("static", "**")] = telesto_static_folder
        resource_roots["**/skadi-page.js"] = os.path.join(telesto_static_folder, "skadi", "skadi-page.js")
        resource_roots[("narvi", "narvi.js")] = narvi_static_folder
        resource_roots[("common", "topology_engine.js")] = apps_common_folder
        resource_roots[("common", "topology_store.js")] = apps_common_folder

        for package_id, package_folder in self.package_folders.items():
            resource_roots[(f"schema/{package_id}", "**")] = package_folder
        resource_roots.update(**from_roots)
        return resource_roots

    def get_platform_extensions(self):
        from hyrrokkin import __version__ as HYRROKKIN_VERSION
        from telesto import __version__ as TELESTO_VERSION
        from narvi import __version__ as NARVI_VERSION
        platform_extensions = []
        platform_extensions.append({"name": "Hyrrokkin", "version": HYRROKKIN_VERSION,
                                    "license_name": "MIT", "url": "https://codeberg.org/visual-topology/hyrrokkin"})
        platform_extensions.append({"name": "Narvi", "version": NARVI_VERSION,
                                    "license_name": "MIT", "url": "https://codeberg.org/visual-topology/narvi"})
        platform_extensions.append({"name": "Telesto", "version": TELESTO_VERSION,
                                    "license_name": "MIT", "url": "https://codeberg.org/visual-topology/telesto"})
        return platform_extensions

    def generate_configuration(self, f, to_path=""):

        f.write(f'# configuration for telesto workspace {self.workspace_id}\n\n')

        if to_path:
            f.write(f'[{to_path}]\n\n')
        else:
            f.write(f'workspace-id = "{self.workspace_id}"\n')

        f.write(f'workspace-name = "{self.workspace_name}"\n')
        f.write(f'workspace-description = "{self.workspace_description}"\n')
        f.write(f'workspace-path = "{self.workspace_path}"\n\n')

        packages = ", ".join(map(lambda id: '"' + id + '"', self.package_list))
        f.write('# specify import paths for each topology package to load\n')
        f.write(f'packages = [{packages}]\n\n')

        if self.skadi_options:
            dict2toml(f"{to_path}.skadi_options" if to_path else "skadi_options", f, self.skadi_options)
        if self.hyrrokkin_options:
            dict2toml(f"{to_path}.hyrrokkin_options" if to_path else "hyrrokkin_options", f, self.hyrrokkin_options)
        if self.templates:
            dict2toml(f"{to_path}.templates" if to_path else "templates", f, self.templates)

    def load_templates(self):
        for topology_id in self.templates:
            topology_folder = os.path.join(self.workspace_path, topology_id)
            if not os.path.exists(topology_folder):
                import_path = self.templates[topology_id]["import_path"]
                self.logger.info(f"loading {topology_id} from {import_path}")
                TopologyDirectory.load_template(import_path, topology_folder)

    def bind(self, server):
        self.server = server
        package_urls = []
        for package_id in self.packages:
            package_urls.append(f"schema/{package_id}")

        applications = {}

        for app_name, app_config in self.applications.items():
            self.logger.info(f"registering application {app_name}")
            name = app_config.get("name")
            description = app_config.get("description", "")
            topology_id = app_config.get("topology_id", "")
            shared = app_config.get("shared", False)

            application_package = app_config.get("application_package")

            topology_path = os.path.join(self.workspace_path, topology_id, "topology.json")
            if not os.path.exists(topology_path):
                self.logger.error(
                    f"Application {app_name} configuration error, no topology found in {topology_path}")
                sys.exit(-1)

            topology_runner = self.server.register_service(workspace=self.workspace_id,
                                                           app_service_name="topology_runner",
                                                           app_cls_name="telesto.app_services.topology_runner.TopologyRunner",
                                                           app_parameters={
                                                               "packages": self.packages,
                                                               "workspace_path": self.workspace_path,
                                                               "hyrrokkin_options": self.get_hyrrokkin_options()
                                                           }, shared_service=shared, fixed_service_id=topology_id)

            application_resource_roots = self.get_resource_roots({
                "topology_application.js": TelestoUtils.get_path_of_resource("telesto.apps", "topology_application.js"),
                "**": TelestoUtils.get_path_of_resource(application_package)
            })

            self.server.register_app(app_name=app_name,
                                     application_service=topology_runner,
                                     app_parameters={
                                         "base_url": self.telesto.base_url,
                                         "package_urls": package_urls,
                                         "platform_extensions": self.get_platform_extensions(),
                                         "workspace_id": self.workspace_id,
                                         "topology_id": topology_id
                                     },
                                     resource_roots=application_resource_roots)

            applications[app_name] = {
                "name": name,
                "description": description,
                "url": f"{self.telesto.base_url}/{self.workspace_id}/{app_name}/index.html"
            }

        topology_runner = server.register_service(workspace=self.workspace_id, app_service_name="topology_runner",
                                                       app_cls_name="telesto.app_services.topology_runner.TopologyRunner",
                                                       app_parameters={
                                                           "packages": self.packages,
                                                           "workspace_path": self.workspace_path,
                                                           "hyrrokkin_options": self.get_hyrrokkin_options()
                                                       }, shared_service=True,
                                                       service_id_validator=
                                                       lambda topology_id: os.path.exists(
                                                           os.path.join(self.workspace_path, topology_id)),
                                                       idle_timeout=self.telesto.idle_timeout)

        designer_resource_roots = self.get_resource_roots({
            "index.html": TelestoUtils.get_path_of_resource("telesto.apps", "topology_designer.html"),
            "topology_designer.js": TelestoUtils.get_path_of_resource("telesto.apps", "topology_designer.js")
        })

        self.server.register_app(app_name=DESIGNER_APP_NAME,
                                 application_service=topology_runner,
                                 app_parameters={
                                     "package_urls": package_urls,
                                     "topology": {},
                                     "read_only": False,
                                     "platform_extensions": self.get_platform_extensions(),
                                     "restartable": not self.in_process,
                                     "skadi_options": self.get_skadi_options()
                                 },
                                 resource_roots=designer_resource_roots,
                                 service_chooser_app_name="topology_directory")

        directory_service = server.register_service(workspace=self.workspace_id,
                                                         app_cls_name="telesto.app_services.topology_directory.TopologyDirectory",
                                                         app_service_name="directory_service",
                                                         app_parameters={
                                                             "workspace_path": self.workspace_path,
                                                             "packages": self.packages,
                                                             "applications": applications,
                                                             "templates": self.templates,
                                                             "get_topology_statuses_callback": lambda: self.get_topology_statuses(),
                                                             "topology_update_callback": lambda action,
                                                                                                topology_id: self.topology_update(
                                                                 action, topology_id)
                                                         },
                                                         fixed_service_id="directory")

        directory_resource_roots = self.get_resource_roots({
            "index.html": TelestoUtils.get_path_of_resource("telesto.apps", "topology_directory.html"),
            "topology_directory.js": TelestoUtils.get_path_of_resource("telesto.apps", "topology_directory.js")
        })

        self.server.register_app(app_name=DIRECTORY_APP_NAME,
                                 application_service=directory_service,
                                 app_parameters={
                                     "designer_app_name": DESIGNER_APP_NAME,
                                     "base_url": self.telesto.base_url,
                                     "package_urls": package_urls,
                                     "skadi_options": self.get_skadi_options()
                                 },
                                 resource_roots=directory_resource_roots)


    def get_topology_statuses(self):
        service_statuses = self.server.get_service_statuses(self.workspace_id)
        runner_statuses = service_statuses.get("topology_runner", {}).get("instances", {})
        return runner_statuses

    def topology_update(self, action, topology_id):
        if action == "create":
            pass
        elif action == "reload":
            self.server.restart_service(self.workspace_id, "topology_runner", topology_id)
        elif action == "remove":
            self.server.stop_service(self.workspace_id, "topology_runner", topology_id)


class Telesto:

    def __init__(self, configuration):
        self.logger = logging.getLogger("telesto")
        self.host = configuration.get("host","localhost")
        self.port = configuration.get("port",8889)

        self.narvi_options = configuration.get("narvi_options", {})
        self.hyrrokkin_options = configuration.get("hyrrokkin_options",{})
        self.skadi_options = configuration.get("skadi_options", {})

        self.workspaces = {}
        self.main_workspace = None
        self.first_workspace_id = ""

        if "workspace_id" in configuration:
            self.first_workspace_id = configuration["workspace_id"]
            self.workspaces[self.first_workspace_id] = TelestoWorkspace(self, configuration["workspace_id"], configuration)

        for workspace_id, workspace_configuration in configuration.get("workspaces",{}).items():
            if self.first_workspace_id == "":
                self.first_workspace_id = workspace_id
            self.workspaces[workspace_id] = TelestoWorkspace(self, workspace_id, workspace_configuration)

        # if no workspaces are defined, error
        if len(self.workspaces) == 0:
            self.logger.error("No workspaces are defined")
            sys.exit(-1)

        self.base_url = configuration.get("base_url","/telesto")
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self.web_server_type = self.narvi_options.get("webserver", "tornado")  # or "builtin"
        self.idle_timeout = self.narvi_options.get("idle_timeout", None)

        self.server = None

        self.launch_ui_command = configuration.get("launch_ui_command","")

        if self.web_server_type == "tornado":
            try:
                # check tornado is installed
                import tornado
            except:
                # if not, fallback to the builtin webserver
                self.logger.warning("tornado web-server not installed, falling back to builtin web-server")
                self.web_server_type = "builtin"

    def get_skadi_options(self):
        return self.skadi_options

    def get_hyrrokkin_options(self):
        return self.hyrrokkin_options

    def generate_configuration(self, path):

        with open(path,"w") as f:
            f.write('# configuration for a set of telesto applications\n\n')
            f.write(f'base-url = "{self.base_url}"\n')
            f.write(f'host = "{self.host}"\n')
            f.write(f'port = {self.port}\n\n')

            f.write('# local application mode - automatically open the page in chromium, stop the server when the page is closed\n')
            f.write('# launch-ui="chromium --app=URL\n\n')

            if self.narvi_options:
                dict2toml("narvi_options", f, self.narvi_options)

            if self.hyrrokkin_options:
                dict2toml("hyrrokkin_options", f, self.hyrrokkin_options)

            if self.skadi_options:
                dict2toml("skadi_options", f, self.skadi_options)

            if self.main_workspace:
                self.main_workspace.generate_configuration(f,"")

            for workspace_id in self.workspaces:
                self.workspaces[workspace_id].generate_configuration(f,f"workspaces.{workspace_id}")


    def run(self, launch_ui=False):

        self.logger.info("starting telesto")

        self.logger.info("base_url="+self.base_url)

        self.server = NarviServer(host=self.host, port=self.port, web_server_type=self.web_server_type,
                             base_path=self.base_url, admin_path="/status.json", monitoring_interval_s=5, monitoring_retention_s=1800)


        if self.main_workspace:
            self.main_workspace.bind(self.server)

        for workspace in self.workspaces.values():
            workspace.bind(self.server)

        # setup shortcuts to the first directory app
        self.server.register_redirect(self.base_url + "/index.html", self.first_workspace_id,
                                      DIRECTORY_APP_NAME)
        self.server.register_redirect(self.base_url + "/", self.first_workspace_id, DIRECTORY_APP_NAME)

        # add a monitor service and app
        app_service = self.server.register_service(workspace="system_workspace",
                                                   app_cls_name="narvi.apps.monitor.monitor_app.MonitorApp",
                                                   app_service_name="monitor_service",
                                                   fixed_service_id="monitor", shared_service=True)

        self.server.register_app(application_service=app_service, app_name="monitor_app",
                                 app_parameters={},
                                 resource_roots={
                                     "index.html": ResourceLoader.get_path_of_resource("narvi.apps.monitor",
                                                                                       "index.html"),
                                     "monitor_app.js": ResourceLoader.get_path_of_resource("narvi.apps.monitor",
                                                                                           "monitor_app.js"),
                                     ("narvi", "*"): ResourceLoader.get_path_of_resource("narvi.static")
                                 })

        # called when the web server is listening, open a web browser on the directory of the first workspace
        def open_callback():
            if launch_ui:
                local_url = f"http://{self.host}:{self.port}{self.base_url}/{self.first_workspace_id}/topology_directory/index.html"
                cmd = self.launch_ui_command.replace("URL",local_url)
                pr = ProcessRunner(cmd.split(" "), exit_callback=lambda: self.server.close())
                pr.start()

        app_details = sorted(self.server.list_app_urls(), key=lambda t:t[0])
        for (workspace, app_name, url) in app_details:
            if workspace and workspace != "system_workspace":
                self.logger.info(f"{workspace}:{app_name} => {url}")

        for (workspace, app_name, url) in app_details:
            if workspace == "system_workspace":
                self.logger.info(f"{workspace}:{app_name} => {url}")

        for (workspace, app_name, url) in app_details:
            if workspace == "":
                self.logger.info(f"{app_name} => {url}")

        self.server.run(open_callback)


