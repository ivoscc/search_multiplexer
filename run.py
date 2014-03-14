# -*- coding: utf-8 -*-

import argparse
from ConfigParser import MissingSectionHeaderError

import tornado.ioloop
import kaptan

from app import SearchHandler


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        help=("Specify the file containing the configuration (defaults to "
              "'config.ini' in the same dir)"),
        default="config.ini")
    parser.add_argument(
        "--section",
        help=("If the .ini file contains multiple sections one may be "
              "specified."),
        default="")
    parser.add_argument(
        "--port",
        help="The port the application will listen to.",
        nargs="?",
        const=int,
        default=8888)
    parser.add_argument(
        "--host",
        help="The base host of the search api.",
        default="http://example.com")
    parser.add_argument(
        "--search_path",
        help="The url that will be used for the search api.",
        default="/search_api_path/")
    return parser.parse_args()


if __name__ == "__main__":
    """
    By default the configuration will be loaded from a file named 'config.ini'
    from the same directory unless specified by the --config option.
    Also, any configurable value might be explicitly supplied by passing the
    desired option, i.e: --port 9999
    """

    args = parse_arguments()
    try:
        handler = kaptan.Kaptan(handler='ini')
        config_file = handler.import_config(args.config)
    except MissingSectionHeaderError:
        config_file = {}
        print ("Failed to read configuration file "
               "{0}. Using defaults...").format(args.config)
    if args.section:
        args.section += "."

    config = {}
    for parameter in ("port", "host", "search_path"):
        config[parameter] = config_file.get(args.section + parameter,
                                            getattr(args, parameter))
    config["full_api_url"] = config["host"] + config["search_path"]
    print "Listening on port {0} and passing request to {1}".format(
        config["port"],
        config["full_api_url"]
    )

    application = tornado.web.Application([
        (r"/", SearchHandler, {"api_url": config["full_api_url"]}),
    ])

    application.listen(config["port"])
    tornado.ioloop.IOLoop.instance().start()
