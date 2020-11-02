#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
import os
import sys
import re
import time

import paramiko

import errno
from socket import error as socket_error
import re

def connectToServer(ip, port, username, password):
    client = 0
    try:
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port, username, password)

    except:
        print("Error:", sys.exc_info()[0])
    return client
    #TODO: Error handling

class session:

    def __init__(self, ip, port, username, password):
        self.ssh_client = connectToServer(ip, port, username, password)

    def send_command(self, cmd):
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)

        # TODO FOR ARISTA NEED TO FIND A BETTER SOLUTION.
        if cmd == 'bash':
            return True
        repr(stdout)
        return stdout.read()

    def close(self):
        self.ssh_client.close()