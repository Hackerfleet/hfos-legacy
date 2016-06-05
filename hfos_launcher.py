#!/usr/bin/env python

"""
Hackerfleet Operating System - Backend

Application
===========

See README.rst for Build/Installation and setup details.

URLs & Contact
==============

Hackerfleet Homepage: http://hackerfleet.org
Mail: info@hackerfleet.org
IRC: #hackerfleet@irc.freenode.org

Project repository: http://github.com/hackerfleet/hfos
Frontend repository: http://github.com/hackerfleet/hfos-frontend

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos import launcher
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Define port for server",
                        type=int, default=80)
    parser.add_argument("--host", help="Define hostname for server",
                        type=str, default='0.0.0.0')
    parser.add_argument("--profile", help="Enable profiler", action="store_true")
    parser.add_argument("--opengui", help="Launch webbrowser for GUI "
                                          "inspection after startup",
                        action="store_true")
    parser.add_argument("--drawgraph", help="Draw a snapshot of the "
                                            "component graph "
                                            "after construction",
                        action="store_true")
    parser.add_argument("--log", help="Define log level (0-100)",
                        type=int, default=20)

    parser.add_argument("--insecure", help="Keep privileges - INSECURE",
                    action="store_true")

    args = parser.parse_args()
    launcher.launch(args)
