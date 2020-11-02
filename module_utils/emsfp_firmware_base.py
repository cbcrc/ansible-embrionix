#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from bs4 import BeautifulSoup
from ntpath import basename
from requests import get, Session
from requests import exceptions as requestsExceptions
from time import sleep

import lxml, json




ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: 
author:
    - Société Radio-Canada
version_added: ""
short_description: Courte description
description:
    - Longue description
options:

notes:
    *** Part of this code whas provided by the company Embrionix.
requirements:

'''

EXAMPLES = '''
'''

RETURN = '''
status:
    description: A dictionary with the key=value pairs returned from `systemctl show`
    returned: success
    type: complex
    contains: {
        }
'''

'''[Constantes de validation des entrées]

'''

class FirmwareUploadError(Exception):
    pass

class EB22():
    def __init__(self, ip):
        self.ip = ip
        self.configUrl = "/gifnoc"
        self.informationUrl = "/emsfp/node/v1/self/information"
        self.sffUrl = "/emsfp/node/v1/self/sff"
        self.session = Session()
        self.moduleType = ""


    def getModuleType(self):
        """
        getModuleType Get the module type to verify if the firmware correpond to the module type.

        Returns:
            [type]: [description]
        """
        try:            
            get_response = get("http://" + self.ip + self.informationUrl)
            if 'Encapsulator' in get_response.json()['type'] :
                self.moduleType = 'Encapsulator'
            elif 'Decapsulator' in get_response.json()['type'] :
                self.moduleType = 'Decapsulator'
            return self.moduleType
        except:
            return "Error getting the module information"

    def getLoads(self):
        """
        getLoads Webscrap the config of the firmware slot of Embrionix module.
        
        Returns:
            dict: loads wich contain the firmware slot configuration.
        """
        # try:
        r = self.session.get("http://" + self.ip + self.configUrl, timeout=1)
        # except:
            # sleep(10)
            # self.getLoads()
            # return(self.loads)
            # pass

        soup = BeautifulSoup( r.content, "lxml" )
        table = soup.select('table')[0]
        table = table.findAll('table')[0]
        rows = table.findAll('tr')
        loads = {}
        cols = []
        for i, row in enumerate(rows[1:]):
            loads[str(i)] = {}
            if( len(row.findAll('td')) == 3 ):
                loads[str(i)]['empty'] = True
            else:
                loads[str(i)]['empty'] = False
                loads[str(i)]['Active'] = False
                loads[str(i)]['Default'] = False
                for j, col in enumerate(row.findAll('td')):
                    if( j == 0 ):
                        if col['bgcolor'] == '#00C000':
                            loads[str(i)]['Active'] = True                    
                    if( j == 2 ):
                        loads[str(i)]['Description'] = col.text
                    if( j == 3 ):
                        loads[str(i)]['Version'] = col.text
                    if( j == 7 ):
                        if col.text == "Yes":
                            loads[str(i)]['Default'] = True
        return(loads)

    def clearSlot(self,slot):
        """[summary]
        Clear the firmware slot of Embrionix module.

        Return:
        A list containg the boolean result and message of the result [boolean result,message]       
        """
        try:
            data = {'clear_'+slot:'Clear'}
            response = self.session.post("http://" + self.ip + "/config/active_element_action", data=data)
            sleep(30)
            return [True, "The selected slot " + slot + " on the module " +  self.ip + " has been cleared."]
        except requestsExceptions.RequestException as e:
            return [False, "Error clearing slot " + slot + " on the module " +  self.ip + " : " + e]

    def uploadFirmware(self, slot, filePath):
        """[summary]
        Upload a firmware file to a slot of Embrionix module.

        Return:
        A list containg the boolean result and message of the result [boolean result,message]  
        """
        try:
            fn = basename(filePath)
            data = {'name':'element_' + slot}
            f = {'file': (fn ,open(filePath,'rb'), 'application/octet-stream', {'Expires':'0'})}
            self.session.post("http://" + self.ip + "/config/upload", files=f, data=data, timeout=240)
        except requestsExceptions.RequestException as e:
            pass
            # return [False,"Error uploading the firmware to slot " + slot + " on the module " +  self.ip + "\nError message: " + str(e) + \
            # "\nCheck if this version of the file is allready in one of the other slot of the module."]
        wait = True
        retry_connexion = 300
        while retry_connexion:
            try:
                response = self.session.get(f"http://{self.ip}/" ,timeout=1)
                retry_connexion -= 1
                break
            except requestsExceptions.RequestException as e:
                pass
        if retry_connexion == 0:
            return [False, f"Module {self.ip} is unreachable after upload"]
        slot_info = self.getLoads()[slot]
        if bool(slot_info['empty']) == True:
            return [False, f"The firmware slot {slot} is still empty. Firmware upload failed"]
        return [True,"Firmware has been upload to the selected slot " + slot + " on the module " +  self.ip]

    def setDefaultSlot(self,slot):
        """[summary]
        Set selected slot as Default.
        Return: A list containg the boolean result and message of the result [boolean result,message]
        """
        if bool(self.getLoads()[slot]['Default']) == True:
            return [False , "The slot selected is allready set as default."]

        data = {'cold_boot_'+slot:'Set As Default'}
        try:
            post_response = self.session.post("http://" + self.ip + "/config/active_element_action", data=data )
            #Add a delay before next query
            sleep(5)
            if(post_response.status_code == 200):
                return [True,"The selected slot " + slot + " on the module " +  self.ip + " has been set as default. Response code : " + str(post_response.status_code)]
            return [False,"Error setting the selected slot " + slot + " on the module " +  self.ip + " as default. Response code: " + str(post_response.status_code)]
        except requestsExceptions.RequestException as e:
            return [False,"Error communicating with the module slot " + slot + " on the module " +  self.ip + \
            ". Ensure that you can manually set the slot as default via the web interface.\n"] + f"Exception message: {e}"

    def setActiveSlot(self,slot):
        """[summary]
        Set selected slot as Active.
        Return: A list containg the boolean result and message of the result [boolean result,message]
        """
        data = {'warm_boot_'+slot:'Load Now'}
        try:
            post_response = self.session.post("http://" + self.ip + "/config/active_element_action", data=data )
            #Add a delay before next query
            sleep(5)
            if(post_response.status_code == 202):
                return [True,"The selected slot " + slot + " on the module " +  self.ip + " has been set as active. Response code : " + str(post_response.status_code)]
            return [False,"Error setting the selected slot " + slot + " on the module " +  self.ip + " as active. Response code: " + + str(post_response.status_code)]
        except requestsExceptions.RequestException as e:
            return [False,"Error communicating with the module " +  self.ip + ". Ensure that you can manually set the slot as active via the web interface.\n" + \
            f"Exception message: {e}"]

    def getActiveFirmawareVersion(self):
        """ 
        Search for the active firmware among all the slots and return a string containing the frimware version.

        Return: a string with the firmware version
        """
        loads = self.getLoads()
        firmware_version = ""
        for slot in loads:
            if 'Active' in loads[slot]:
                if loads[slot]["Active"]:
                    firmware_version = loads[slot]["Version"]
        return firmware_version

    def getSerialNumber(self):
        r = self.session.get("http://" + self.ip + self.sffUrl, timeout=1)
        try:
            serial_number_ascii = json.loads(r.content)['a0'].split(",")[68:80]
            serial_number_dec = ""       
            
            for x in serial_number_ascii:
                if x.isnumeric():
                    serial_number_dec += str(int(x) - 30)
                else:
                    return f"Invalid serial number: {serial_number_dec}{x}"
            return serial_number_dec
        except:
            return f"Page not found http://{self.ip + self.sffUrl}"
        
#118013000193
def main():
    #Initiating the upload firmware object.
    # module_ip = "10.168.206.82"
    module_ip = "10.173.224.19"
    # module_firmware_slot= "2"
    # module_firmware_filepath= "../firmwares/PLD-078-SFPXX-2E-2110-E-3.0.1371_ENC_CBC.img"

    sfp = EB22(module_ip)  

    # print(sfp.getActiveFirmawareVersion())
    print(sfp.getSerialNumber())
    #print(sfp.getModuleType())
    #print(sfp.clearSlot())
    #print(sfp.loadFirmwareInSelectedSlot(module_firmware_filepath))
    #print(sfp.setActiveSlot())
    #print(sfp.setDefaultSlot())
    print(sfp.getActiveFirmawareVersion())


if __name__ == "__main__":
    main()