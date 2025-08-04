/*
 Telesto
 Copyright (C) 2025  Visual Topology Ltd

 MIT License

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
*/

var telesto = telesto || {};

telesto.TopologyDirectory = class {

    constructor(services, parameters) {
        this.services = services;
        this.parameters = parameters;
        this.designer_app_name = parameters.designer_app_name;

        this.services.add_message_listener(async (msg) => {
            await this.recv(msg);
        });

        this.skadi_directory_api = null;
    }

    send(msg) {
        this.services.send(JSON.stringify(msg));
    }

    async recv(msg_txt) {
        let payload = JSON.parse(msg_txt);
        let topologies = payload["topologies"];
        let applications = payload["applications"];

        let options = {
            "l10n_url": "static/skadi/l10n",
            "package_urls": this.parameters["package_urls"],
            "title": "Topology Directory",
            "templates": {}
        }
        if ("skadi_options" in this.parameters) {
            for (let option in this.parameters["skadi_options"]) {
                if (!(option in options)) {
                    options[option] = this.parameters["skadi_options"][option];
                }
            }
        }
        let topology_store = new telesto.TopologyStore(this,topologies);
        let plugins = {
            "topology_store": topology_store
        }
        this.skadi_directory_api = new skadi.DirectoryApi("skadi_container", options, plugins, applications);

        this.skadi_directory_api.set_open_topology_in_designer_handler((topology_id) => {
            let target_url = "../../" + this.designer_app_name + "/" + topology_id + "/index.html";
            window.open(target_url);
        });

        await this.skadi_directory_api.load();
    }
}



