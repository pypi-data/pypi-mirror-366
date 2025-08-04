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

telesto.topology_application = null;

telesto.TopologyApplication = class {

    constructor(services, parameters) {
        this.services = services;
        this.parameters = parameters;

        this.services.add_message_listener((msg) => {
            this.recv(msg);
        });


        this.engine = new telesto.TopologyEngine(this,this.parameters["restartable"] || false);
        this.engine.set_load_callback((skadi_api) => this.load_callback(skadi_api));

        let plugins = {
            "engine": this.engine,
            "topology_store": new telesto.TopologyStore(this, null),
            "resource_loader": null
        }

        let options = {
            "package_urls":this.parameters["package_urls"],
            "platform_extensions": this.parameters["platform_extensions"],
            "workspace_id": this.parameters["workspace_id"]
        }

        let topology_id = this.parameters["topology_id"];

        skadi.start_application(topology_id, options, plugins).then(async skadi_app => {
            await skadi_app.start();
            configure_application_page(skadi_app);
        });
    }

    send(msg) {
        if (msg instanceof ArrayBuffer) {
            this.services.send(msg);
        } else {
            this.services.send(JSON.stringify(msg));
        }
    }

    recv(msg) {
        this.engine.handle(msg);
    }

    load_callback(skadi_api) {

    }
}



