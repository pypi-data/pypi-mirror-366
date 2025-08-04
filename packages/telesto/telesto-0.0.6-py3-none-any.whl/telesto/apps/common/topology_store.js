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

telesto.TopologyStore = class extends skadi.StoreBase {

    constructor(webapp, topologies) {
        super();
        this.webapp = webapp;
        this.topologies = topologies;
        this.options = null;
    }

    /**
     * Initialise the store
     *
     * @param {object} options
     *
     * @returns {Promise<void>}
     */
    async init(options)  {
        this.options = options;
    }

    /**
     * Create a new topology in the store, either empty or a copy of an existing topology
     *
     * @param {string} topology_id
     * @param {?string} from_topology_id
     * @returns {Promise<void>}
     */
    async create_topology(topology_id, from_topology_id) {
        this.webapp.send({"action":"create_topology","topology_id":topology_id, "from_topology_id":from_topology_id});
    }

    /**
     * Remove a topology from the store, if it exists
     *
     * @param topology_id
     * @returns {Promise<void>}
     */
    async remove_topology(topology_id) {
        this.webapp.send({"action":"remove_topology", "topology_id":topology_id});
    }

    /**
     * Reload a topology from its template
     *
     * @param topology_id
     * @returns {Promise<void>}
     */
    async reload_topology(topology_id) {
        this.webapp.send({"action":"reload_topology", "topology_id":topology_id});
    }

    /**
     * @typedef  TopologyMetadata
     * @type {object}
     * @property {string} name - the topology name.
     * @property {string} description - the topology name.
     * @property {?string} version - the topology version.
     * @property {?number} authors - list of authors.
     *
     */

    /**
     * Get an array of all the topology ids in the store
     *
     * @returns {Promise<string[]>}
     */
    async list_topologies() {
        return Object.keys(this.topologies);
    }

    /**
     * Check if a topology exists in the store
     *
     * @param {string} topology_id the id of the topology
     * @returns {Promise<boolean>}
     */
    async topology_exists(topology_id) {
        return topology_id in this.topologies;
    }

    /**
     * Return a list of topologies, where the key is the topology metadata
     *
     * @returns {Promise<Object.<string, TopologyMetadata>>}
     */
    async get_topology_details() {
        return this.topologies;
    }

    /**
     * Get the metadata for a topology
     *
     * @returns {Promise<TopologyMetadata>}
     */
    async get_topology_metadata(topology_id) {
        return this.topologies[topology_id];
    }

    /**
     * Load the topology from the store into the bound skadi instance
     *
     * @param {string} topology_id the id of the topology to load
     *
     * @returns {Promise<void>}
     */
    async load_topology(topology_id) {
        return {};
    }

    /**
     *
     */
    bind() {
    }

    async save() {
    }

    async get_save_link() {
        return this.webapp.get_download_url();
    }

    async load_from(file, node_renamings) {
        // FIXME what about node renamings?
        file.arrayBuffer().then(array_buffer => {
            this.webapp.upload(array_buffer);
        });
    }

    get_file_suffix() {
        return ".zip";
    }
}
