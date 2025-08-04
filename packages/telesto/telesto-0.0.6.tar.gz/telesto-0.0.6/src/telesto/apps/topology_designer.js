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

telesto.topology_designer = null;

telesto.TopologyDesigner = class  {

    constructor(services, parameters) {
        this.services = services;
        this.skadi = null;
        // manage messages from the app service
        this.is_handling_messages = false;
        this.message_queue = [];
        this.services.add_message_listener((msg) => {
            this.message_queue.push(msg);
            if (!this.is_handling_messages) {
                this.handle_messages();
            }
        });
        this.download_url = "";

        const path = window.location.pathname;

        const path_parts = path.split("/");
        const path_len = path_parts.length;

        let workspace_id = path_parts[path_len-4];
        let topology_id = path_parts[path_len-2];

        this.topology_store = new telesto.TopologyStore(this, {});
        this.engine = new telesto.TopologyEngine(this,parameters["restartable"] || false);
        let plugins = {
            "engine": this.engine,
            "topology_store": this.topology_store
        }

        let options = {
            "package_urls":parameters["package_urls"],
            "platform_extensions": parameters["platform_extensions"],
            "workspace_id": workspace_id,
            "topology_id": topology_id,
            "designer_title": "Telesto Topology Designer",
            "directory_title": "Telesto Topology Directory",
            "splash": {
                "title": "Telesto Topology Designer",
                "image_url": "skadi/images/skadi.svg"
            },
            "directory_url": "../../topology_directory/index.html"
        }

        let skadi_options = parameters["skadi_options"] || {};

        for (let option in skadi_options) {
            if (!(option in options)) {
                options[option] = skadi_options[option];
            }
        }

        skadi.start_designer(topology_id, "skadi_container", options, plugins)
            .then(skadi_designer_api => this.init(skadi_designer_api), err => console.error(err));
        telesto.topology_designer = this;
    }

    send(msg) {
        if (msg instanceof ArrayBuffer) {
            this.services.send(msg);
        } else {
            this.services.send(JSON.stringify(msg));
        }
    }

    handle_messages() {
        if (this.message_queue.length>0) {
            this.is_handling_messages = true;
            this.recv(this.message_queue.shift()).then(() => this.handle_messages());
        } else {
            this.is_handling_messages = false;
        }
    }

    async recv(msg) {
        await this.engine.handle(msg);
    }

    set_download_url(url) {
        this.download_url = url;
    }

    get_download_url() {
        return this.download_url;
    }

    upload(file_contents) {
        let msg_header = {
            "action": "upload_topology"
        }
        let message_content = [msg_header].concat(file_contents);
        let enc_msg = NarviMessageUtils.encode_message(...message_content);
        this.send(enc_msg);
    }

    init(skadi_designer_api) {
        this.skadi = skadi_designer_api;
    }

    load(from_obj) {
        this.send(from_obj); // binary message will be automatically interpreted by the peer as a load command
    }
}


