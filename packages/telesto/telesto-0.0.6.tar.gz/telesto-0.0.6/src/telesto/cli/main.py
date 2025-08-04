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

import logging
import argparse
import tomllib
import os
import signal
import sys

from telesto.api.telesto import Telesto

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configuration", help="Specify the path to a configuration file", default=None)

    # these common options allow settings in the configuration file to be overridden
    parser.add_argument("--host", help="Specify the host name for serving files", default=None)
    parser.add_argument("--port", type=int, help="Specify the port number for serving files", default=None)
    parser.add_argument("-b", "--base-url", help="Specify the base url for the web server", default=None)

    parser.add_argument("-l", "--launch-ui", action="store_true", help="launch a web browser", default=None)
    parser.add_argument("--verbose", action="store_true", help="enable verbose logging", default=None)

    parser.add_argument("--generate-configuration-path", type=str, metavar="PATH",
                        help="Generate a configuration file", default=None)


    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # read the configuration file
    if args.configuration:
        configuration_path = args.configuration
    else:
        configuration_path = os.path.join(os.path.split(__file__)[0], "telesto_defaults.toml")

    with open(configuration_path) as f:
        config = tomllib.loads(f.read())

    # override from the command line
    for key in ["host","port","base_url"]:
        value = getattr(args,key)
        if value:
            config[key] = value

    app = Telesto(config)

    if args.generate_configuration_path:
        app.generate_configuration(args.generate_configuration_path)
    else:
        app.run(args.launch_ui)


if __name__ == '__main__':
    main()