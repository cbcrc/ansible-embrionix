#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from module_utils import ssh_session
import re
import time


class arista:

    def __init__(self, ip, ports, username, password, sleep=False):
        print('Init arista ')
        self.ip = ip
        self.port = ports
        self.arista_ssh = ssh_session.session(ip, 22, username, password)
        self.sleep = sleep
        
        output = self.arista_ssh.send_command('show platform smbus counters')
        self.firmwares = []

        for port in ports:
            self.hw_addr_a0 = re.search("Ethernet" + port + "\s*\d\d/\d\d/\dx\d\d", output.decode("utf-8"),
                                        re.MULTILINE).group().replace("Ethernet" + port, "").strip()
            bus_id, dev_id, dev_addr = self.hw_addr_a0.split("/")
            self.hw_addr_a2 = "/".join([bus_id, dev_id, hex(int(dev_addr,16)+1)])
            self.arista_ssh.send_command('bash')
            fw_version_hex = self.get_page('0xff')[130-128:166-128]
            self.firmwares.append([fw_version_hex, ''.join(fw_version_hex), port])
    def get_a0(self):
        print('Get A0')
        output = self.arista_ssh.send_command(
            "en\n\rbash smbus reads /scd/" + self.hw_addr_a0 + " 0 127")
        ret = output.decode("utf-8").strip()

        return ret.replace(' ', ',').split(',')

    def write_register(self, register, value, wait_write_done = True):
        if not isinstance(register, int):
            if '0x' in register.lower():
                register = int(register, 16)

        value = value.replace(' ','').replace('0x','')
        output = self.arista_ssh.send_command("en\n\rbash smbus writes /scd/{hw_addr} {register} {value}".format(hw_addr=self.hw_addr_a2, value=value, register=register))
        #print('write {value} on a2 at {register}'.format(value=value, register=register))

        if self.sleep:
            print('Sleeping 1 second')
            time.sleep(1)
        else:
            if wait_write_done:
                self.wait_write_done()

    def wait_write_done(self):
        #print('Wait write done')
        write_not_done = True
        max_iter = 10
        while(write_not_done):
            max_iter = max_iter -1
            page_status = self.read_page(register='128', length='1')[0]
            page_status_bin = bin(int(page_status, 16))[2:].zfill(8)
            page_ready = page_status_bin[5]
            write_done = page_status_bin[6]

            print('Write Done: %s' % write_done)
            if write_done == '1':
                write_not_done = False
            if max_iter <= 0:
                return -1

    def set_page(self, page):
        #print('Set page to %s' % page)
        self.write_register(register='127', value=page, wait_write_done=False)
        if self.sleep:
            print('Sleeping 5 seconds')
            time.sleep(5)
            return True
        page_not_changed = True
        max_iter = 10
        while page_not_changed:
            max_iter = max_iter - 1
            current_page = self.read_page(register='255', length='1')[0]
            print('Current Page: %s' % current_page)
            if current_page == page.lower().replace('0x',''):
                page_not_changed = False
            if max_iter <= 0:
                return -1

        page_not_ready = True
        max_iter = 10
        while page_not_ready:
            max_iter = max_iter -1
            page_status = self.read_page(register='128', length='1')[0]
            page_status_bin = bin(int(page_status, 16))[2:].zfill(8)
            page_ready = page_status_bin[5]
            write_done = page_status_bin[6]

            print('Page Ready: %s' % page_ready)
            if page_ready == '1':
                page_not_ready = False
            if max_iter <= 0:
                return -1
        return True

    def read_page(self, monitoring=False, register='128', length='127'):
        #print('Read register %s for %s bytes' % (register, length))
        if monitoring:
            register = '0'
            length = '127'

        output = self.arista_ssh.send_command(
            "en\n\rbash smbus reads /scd/" + self.hw_addr_a2 + " " + register + " " + length)
        ret = output.decode("utf-8").strip()

        return ret.replace(' ', ',').split(',')

    def get_page(self, page='0x84'):
        self.set_page(page)

        return self.read_page()
