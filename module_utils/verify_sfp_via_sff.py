#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from lxml import etree
import sys
import requests
import time
import json
import getopt
from module_utils.arista import arista
#import pi
#import embox
#from module_utils.em_convert import em_convert
#import omnitek
import codecs
#import mellanox
#import aardvark


# def print_usage(arg=None):
#     print("\nSFP A0 and A2 \n")
#     print("Usage:")
#     print("sff.py -r restip -a aristaip -p sfpport")
#     print("\n")













# def write_multibyte_register(session, register, value, length):
#     value_hex = hex(value)[2:].zfill(2*length)
#     value_hex_list = [value_hex[i:i + 2] for i in range(0, len(value_hex), 2)]
#     i=0
#     for byte in value_hex_list:
#         session.write_register(hex(register+i), byte)
#         i += 1



# def get_ip(session):
#     the_page = session.read_page()
#     if the_page[255-128] != '84':
#         session.set_page('0x84')
#         the_page = session.read_page()
#     ip = the_page[139-128:139-128+4]
#     ip = [str(int(x, 16)) for x in ip]
#     ip_formated = '.'.join(ip)
#     print('IP is: %s ' % ip_formated)

#     return ip_formated


# def reset_device(session):
#     # RESET DEVICE
#     session.set_page('0x84')
#     session.write_register('0x81', '0x02')
#     session.write_register('0x81', '0x06')
#     session.write_register('0x81', '0x01')
#     time.sleep(20)  # Wait for reboot


# def change_current_load(session, load_id):
#     # CHANGE DEFAULT LOAD
#     session.set_page('0xFA')
#     session.write_register('0x81', '0x02')
#     session.write_register(hex(131), "{0:#0{1}x}".format(load_id, 4))  # VALUE 0 to 3
#     session.write_register('0x81', '0x03')
#     time.sleep(1)


# def change_default_load(session, load_id):
#     # CHANGE CURRENT LOAD
#     session.set_page('0xFA')
#     session.write_register('0x81', '0x02')
#     session.write_register(hex(133), "{0:#0{1}x}".format(load_id, 4))  # VALUE 0 to 3
#     session.write_register('0x81', '0x03')
#     time.sleep(10)


# def verify_and_set_page(session, page):
#     current_page = session.read('a2', 0x7f, 1)
#     if current_page != page[-2:]:
#         session.setPage(page)

#     i = 0
#     while i < 10:
#         page_status = session.read('a2', 0x80, 1)
#         page_status_bin = bin(int(page_status, 16))[2:].zfill(8)
#         print(page_status_bin)  #100000110
#         print('write done: %s' % page_status_bin[6])
#         print('page ready: %s' % page_status_bin[5])
#         if page_status_bin[5] == '1':
#             break
#         print('waiting page status')
#         time.sleep(0.1)
#         i += 1


# def unlock_flash(session):
#     session.write_register('0x81', '0x02')  # Unlock


# def commit_flash(session):
#     session.write_register('0x81', '0x03')  # Commit


# def print_a0(sff_a0):
#     if sff_a0 is None:
#         return False
#     print('A0')
#     #0 Identifier
#     identifier = sff_a0[0]
#     print('Identifier: %s' % identifier)
#     #1 Ext. Identifier
#     ext_identifier = sff_a0[1]
#     print('Ext. Identifier: %s (%s)' % (ext_identifier, em_convert.convert_ext_identifier(ext_identifier)))
#     #2 Connector
#     connector = sff_a0[2]
#     print('Connector: %s (%s)' % (connector, em_convert.convert_connector(connector)))
#     #4-10 Transceiver
#     transceiver = sff_a0[4:11]
#     print('Transceiver: %s' % transceiver)
#     #11 Encoding
#     encoding = sff_a0[3]
#     print('Encoding: %s (%s)' % (encoding, em_convert.convert_encoding(encoding)))
#     #20-35 Vendor Name
#     vendor_name_hex = sff_a0[20:36]
#     vendor_name = ''.join(vendor_name_hex)
#     print('Vendor Name: %s' % codecs.decode(vendor_name, 'hex'))
#     #37-39 Vendor OUI
#     vendor_oui = '%s%s%s' % (sff_a0[37], sff_a0[38], sff_a0[39])
#     print('Vendor OUI: %s' % vendor_oui)
#     #40-55 Vendor PN
#     vendor_pn_hex = sff_a0[40:56]
#     vendor_pn = ''.join(vendor_pn_hex)
#     print('Vendor PN: %s' % codecs.decode(vendor_pn, 'hex'))
#     #56-59 Vendor Rev
#     vendor_rev_hex = sff_a0[56:59]
#     vendor_rev = ''.join(vendor_rev_hex)
#     print('Vendor Rev: %s (%s)' % (codecs.decode(vendor_rev, 'hex'), vendor_rev_hex))

#     #60-61 Laser Wavelength
#     laser_wave_length_hex = sff_a0[60] + sff_a0[61]
#     laser_wave_length = int(laser_wave_length_hex, 16)
#     print('Laser Wavelength: %s' % laser_wave_length)

#     #68-83 Vendor SN
#     vendor_sn_hex = sff_a0[68:83]
#     vendor_sn = ''.join(vendor_sn_hex)
#     print('Vendor SN: %s' % codecs.decode(vendor_sn, 'hex'))

#     #84-91 Date Code
#     # 84-85 Year
#     # 86-87 Month
#     # 88-89 Day
#     # 90-91 Specific
#     date_code_year = codecs.decode(sff_a0[84] + sff_a0[85],'hex')
#     date_code_month = codecs.decode(sff_a0[86] + sff_a0[87], 'hex')
#     date_code_day = codecs.decode(sff_a0[88] + sff_a0[89], 'hex')
#     date_code_lot = codecs.decode(sff_a0[90] + sff_a0[91], 'hex')
#     print('Date Code: %s/%s/%s %s (YY/MM/DD LOT)' % (date_code_year, date_code_month, date_code_day, date_code_lot))

#     #93 Enhanced Options
#     options = sff_a0[93]
#     options_bin = bin(int(options, 16))[2:].zfill(8)
#     print('Option: %s (%s)' % (options, options_bin))
#     print('Alarm/Warning implemented: %s' % options_bin[0])
#     print('soft TX_DISABLE implemented: %s' % options_bin[1])
#     print('soft TX_FAULT implemented: %s' % options_bin[2])
#     print('soft RX_LOS implemented: %s' % options_bin[3])
#     print('soft RATE_SELECT implemented: %s' % options_bin[4])
#     print('soft Select SFF-8079: %s' % options_bin[5])
#     print('soft RATE_SELECT SFF-8431: %s' % options_bin[6])
#     print('Unallocated: %s' % options_bin[7])


# def print_a2(sff_a2):
#     if sff_a2 is None:
#         return False
#     print('-----------------------------------------------------------------------------------------------------------')
#     print('A2')
#     #00-01 Temp High Alarm
#     temp_high_alarm_1 = sff_a2[0]
#     temp_high_alarm_2 = sff_a2[1]
#     print('Temp High Alarm: %s,%s (%sC)' %(temp_high_alarm_1, temp_high_alarm_2, em_convert.convert_temp(temp_high_alarm_1, temp_high_alarm_2)))
#     #02-03 Temp Low Alarm
#     temp_low_alarm_1 = sff_a2[2]
#     temp_low_alarm_2 = sff_a2[3]
#     print('Temp Low Alarm: %s,%s (%sC)' %(temp_low_alarm_1, temp_low_alarm_2, em_convert.convert_temp(temp_low_alarm_1, temp_low_alarm_2)))
#     #04-05 Temp High Warning
#     temp_high_warning_1 = sff_a2[4]
#     temp_high_warning_2 = sff_a2[5]
#     print('Temp High Warning: %s,%s (%sC)' %(temp_high_warning_1, temp_high_warning_2, em_convert.convert_temp(temp_high_warning_1, temp_high_warning_2)))
#     #06-07 Temp Low Warning
#     temp_low_warning_1 = sff_a2[6]
#     temp_low_warning_2 = sff_a2[7]
#     print('Temp Low Warning: %s,%s (%sC)' %(temp_low_warning_1, temp_low_warning_2, em_convert.convert_temp(temp_low_warning_1, temp_low_warning_2)))
#     #08-09 Voltage High Alarm
#     voltage_high_alarm = sff_a2[8]+sff_a2[9]
#     print('Voltage High Alarm: %s (%sV)' %(voltage_high_alarm, int(voltage_high_alarm, 16)/10000.0))
#     #10-11 Voltage Low Alarm
#     voltage_low_alarm_1 = sff_a2[10]+sff_a2[11]
#     print('Voltage Low Alarm: %s (%sV)' %(voltage_low_alarm_1, int(voltage_low_alarm_1, 16)/10000.0))
#     #12-13 Voltage High Warning
#     voltage_high_warning = sff_a2[12]+sff_a2[13]
#     print('Voltage High Warning: %s (%sV)' % (voltage_high_warning, int(voltage_high_warning, 16)/10000.0))
#     #14-15 Voltage Low Warning
#     voltage_low_warning = sff_a2[14]+sff_a2[15]
#     print('Voltage Low Warning: %s (%sV)' % (voltage_low_warning, int(voltage_low_warning, 16)/10000.0))
#     #16-17 Bias High Alarm
#     bias_high_alarm = sff_a2[16]+sff_a2[17]
#     print('Bias High Alarm: %s (%s)' % (bias_high_alarm, int(bias_high_alarm, 16)))
#     #18-19 Bias Low Alarm
#     bias_low_alarm = sff_a2[18]+sff_a2[19]
#     print('Bias Low Alarm: %s (%s)' % (bias_low_alarm, int(bias_low_alarm, 16)))
#     #20-21 Bias High Warning
#     bias_high_warning = sff_a2[20]+sff_a2[21]
#     print('Bias High Warning: %s (%s)' % (bias_high_warning, int(bias_high_warning, 16)))
#     #22-23 Bias Low Warning
#     bias_low_warning = sff_a2[22]+sff_a2[23]
#     print('Bias Low Warning: %s (%s)' % (bias_low_warning, int(bias_low_warning, 16)))
#     #24-25 TX Power High Alarm
#     #26-27 TX Power Low Alarm
#     #28-29 TX Power High Warning
#     #30-31 TX Power Low Warning
#     #32-33 RX Power High Alarm
#     #34-35 RX Power Low Alarm
#     #36-37 RX Power High Warning
#     #38-39 RX Power Low Warning
#     #40-45 Unallocated
#     #56-59 Rx_PWR(4)
#     #60-63 Rx_PWR(3)
#     #64-67 Rx_PWR(2)
#     #68-71 Rx_PWR(1)
#     #72-75 Rx_PWR(0)
#     print('Rx Power 0: %s' %sff_a2[72:75])
#     #76-77 Tx_l(Slope)
#     #78-79 Tx_l(Offset)
#     #80-81 Tx_PWR(Slope)
#     #82-83 Tx_PWR(Offset)
#     #84-85 T (Slope)
#     temp_slope_1 = sff_a2[84]
#     temp_slope_2 = sff_a2[85]
#     print('Temperature Slope: %s,%s' %(temp_slope_1, temp_slope_2))
#     #86-87 T (Offset)
#     temp_offset_1 = sff_a2[86]
#     temp_offset_2 = sff_a2[87]
#     print('Temperature Offset: %s,%s' %(temp_offset_1, temp_offset_2))
#     #88-89 V (Slope)
#     voltage_slope_1 = sff_a2[88]
#     voltage_slope_2 = sff_a2[89]
#     print('Voltage Slope: %s,%s' %(voltage_slope_1, voltage_slope_2))
#     #90-91 V (Offset)
#     voltage_offset_1 = sff_a2[90]
#     voltage_offset_2 = sff_a2[91]
#     print('Voltage Offset: %s,%s' %(voltage_offset_1, voltage_offset_2))
#     #92-94 Unallocated
#     #95 Checksum
#     calculated_checksum=0
#     for i in range(0,95):
#         calculated_checksum += int(sff_a2[i], 16)
#     print('Calculated Checksum: %s' % hex(calculated_checksum)[-2:])
#     checksum = sff_a2[95]
#     print('Checksum: %s' %checksum)
#     #96 Temperature MSB
#     temp_msb = sff_a2[96]
#     #97 Temperature LSB
#     temp_lsb = sff_a2[97]
#     print('Temperature: %s,%s (%s.%sC)' %(temp_msb, temp_lsb, int(temp_msb, 16), int(temp_lsb, 16)))
#     #98 Vcc MSB
#     voltage = sff_a2[98] + sff_a2[99]
#     #99 Vcc LSB
#     print('Voltage: %s (%sV)' %(voltage, int(voltage, 16)/10000.0))
#     #100 TX Bias MSB 101 TX Bias LSB
#     tx_bias_msb = sff_a2[100]
#     tx_bias_lsb = sff_a2[101]
#     print('TX Bias: %s,%s (%s.%s)' % (tx_bias_msb, tx_bias_lsb, int(tx_bias_msb, 16), int(tx_bias_lsb, 16)))
#     #102 Tx Power MSB 103 Tx Power LSB
#     tx_power_msb = sff_a2[102]
#     tx_power_lsb = sff_a2[103]
#     print('TX Power: %s,%s (%s.%s)' % (tx_power_msb, tx_power_lsb, int(tx_power_msb, 16), int(tx_power_lsb, 16)))
#     #104 RX Power MSB 105 RX Power LSB
#     rx_power_msb = sff_a2[104]
#     rx_power_lsb = sff_a2[105]
#     print('RX Power: %s,%s (%s.%s)' % (rx_power_msb, rx_power_lsb, int(rx_power_msb, 16), int(rx_power_lsb, 16)))
#     #106-109 Unallocated

#     # 106-107 Laser Temperature
#     temp_msb = sff_a2[106]
#     temp_lsb = sff_a2[107]
#     print('Laser Temperature: %s,%s (%s.%sC)' %(temp_msb, temp_lsb, int(temp_msb, 16), int(temp_lsb, 16)))

#     # 108-109 TEC Current
#     tec_msb = sff_a2[108]
#     tec_lsb = sff_a2[109]
#     print('TEC: %s,%s (%s.%s mA)' %(tec_msb, tec_lsb, int(tec_msb, 16), int(tec_lsb, 16)))

#     #110 Control
#     control = sff_a2[110]
#     control_bin = bin(int(control, 16))[2:].zfill(8)
#     print('Control: %s (%s)' % (control, control_bin))
#     print('TX Disable State: %s' %control_bin[0])
#     print('Soft TX Disable Select: %s' %control_bin[1])
#     print('RS(1) State: %s' % control_bin[2])
#     print('RS(0): %s' % control_bin[3])
#     print('Soft RS(0): %s' % control_bin[4])
#     print('TX Fault State: %s' % control_bin[5])
#     print('RX_LOST State: %s' % control_bin[6])
#     print('Data_Ready_Bar State: %s' % control_bin[7])
#     #111 Reserved
#     #112 Alarm
#     alarm_flag = sff_a2[112]
#     alarm_flag_bin = bin(int(alarm_flag, 16))[2:].zfill(8)
#     print('Alarm: %s (%s)' % (alarm_flag, alarm_flag_bin))
#     print('Temp High Alarm: %s' %alarm_flag_bin[0])
#     print('Temp Low Alarm: %s' %alarm_flag_bin[1])
#     print('Vcc High Alarm: %s' % alarm_flag_bin[2])
#     print('Vcc Low Alarm: %s' % alarm_flag_bin[3])
#     print('TX Bias High Alarm:%s' % alarm_flag_bin[4])
#     print('TX Bias Low Alarm:%s' % alarm_flag_bin[5])
#     print('TX Power High Alarm:%s' % alarm_flag_bin[6])
#     print('TX Power Low Alarm:%s' % alarm_flag_bin[7])
#     #113 Alarm 2
#     alarm2_flag = sff_a2[113]
#     alarm2_flag_bin = bin(int(alarm2_flag, 16))[2:].zfill(8)
#     print('RX Power High Alarm:%s' % alarm2_flag_bin[0])
#     print('RX Power Low Alarm:%s' % alarm2_flag_bin[1])
#     #114-115 Unallocated
#     #116 Warning
#     warning_flag = sff_a2[116]
#     warning_flag_bin = bin(int(warning_flag, 16))[2:].zfill(8)
#     print('Warning: %s (%s)' % (warning_flag, warning_flag_bin))
#     print('Temp High Warning: %s' % warning_flag_bin[0])
#     print('Temp Low Warning: %s' % warning_flag_bin[1])
#     print('Vcc High Warning: %s' % warning_flag_bin[2])
#     print('Vcc Low Warning: %s' % warning_flag_bin[3])
#     print('TX Bias High Warning:%s' % warning_flag_bin[4])
#     print('TX Bias Low Warning:%s' % warning_flag_bin[5])
#     print('TX Power High Warning:%s' % warning_flag_bin[6])
#     print('TX Power Low Warning:%s' % warning_flag_bin[7])
#     #117 Warning 2
#     warning2_flag = sff_a2[117]
#     warning2_flag_bin = bin(int(warning2_flag, 16))[2:].zfill(8)
#     print('RX Power High Warning:%s' % warning2_flag_bin[0])
#     print('RX Power Low Warning:%s' % warning2_flag_bin[1])


# def print_a2_84(sff_a2_84):
#     dict_84={}
#     if sff_a2_84 is None:
#         return False
#     print('-----------------------------------------------------------------------------------------------------------')
#     print('A2 Page 84')
#     # 128 Controller page
#     # 129 Flash operation
#     # 130 a2 page rev
#     # 131, 132 asic general
#     # 133-138 mac
#     mac = sff_a2_84[5:11]
#     mac_formated = ':'.join(mac)
#     dict_84['mac']=mac_formated
#     print('MAC: %s' % mac_formated)

#     # 139-142 current ip
#     ip = sff_a2_84[11:15]
#     ip = [str(int(x, 16)) for x in ip]
#     ip_formated = '.'.join(ip)
#     dict_84['ip']=ip_formated
#     print('Current IP: %s' % ip_formated)

#     # 143-146 current mask
#     mask = sff_a2_84[15:19]
#     mask = [str(int(x, 16)) for x in mask]
#     mask_formated = '.'.join(mask)
#     dict_84['mask']=mask_formated
#     print('Current Mask: %s' % mask_formated)

#     # 147-150 current gateway
#     gateway = sff_a2_84[19:23]
#     gateway = [str(int(x, 16)) for x in gateway]
#     gateway_formated = '.'.join(gateway)
#     dict_84['gateway']=gateway_formated
#     print('Current Gateway: %s' % gateway_formated)

#     # 151-154 static ip
#     static_ip = sff_a2_84[23:27]
#     static_ip = [str(int(x, 16)) for x in static_ip]
#     static_ip_formated = '.'.join(static_ip)
#     dict_84['static_ip']=static_ip_formated
#     print('Static IP: %s' % static_ip_formated)

#     # 155-158 static mask
#     static_mask = sff_a2_84[27:31]
#     static_mask = [str(int(x, 16)) for x in static_mask]
#     static_mask_formated = '.'.join(static_mask)
#     dict_84['static_mask']=static_mask_formated
#     print('Static Mask: %s' % static_mask_formated)

#     # 159-162 static gateway
#     static_gateway = sff_a2_84[31:35]
#     static_gateway = [str(int(x, 16)) for x in static_gateway]
#     static_gateway_formated = '.'.join(static_gateway)
#     dict_84['static_gateway']=static_gateway_formated
#     print('Static Gateway: %s' % static_gateway_formated)

#     # 163-178 hostname
#     hostname = sff_a2_84[35:49]
#     hostname = ''.join(hostname)
#     dict_84['hostname']=hostname
#     print('Hostname: %s' % codecs.decode(hostname, 'hex'))

#     # 179 ttl
#     ttl = sff_a2_84[51]
#     dict_84['ttl']=ttl
#     print('TTL: %s' % ttl)

#     # 180 DHCP
#     dhcp = sff_a2_84[52]
#     dhcp_bin = bin(int(dhcp, 16))[2:].zfill(8)
#     dhcp_status = dhcp_bin[1:3]
#     dict_84['dhcp']=dhcp_bin
#     print('DHCP: %s' % dhcp_bin)
#     dict_84['dhcp_status']=dhcp_status
#     print('DHCP Status: %s' % dhcp_status)
#     dhcp_state = dhcp_bin[7]
#     dict_84['dhcp_state']=dhcp_state
#     print('DHCP State: %s' % dhcp_state)

#     # 181 VLAN
#     vlan = sff_a2_84[181-128:183-128]
#     vlan = em_convert.convert_hexstring_to_intstring(vlan)
#     dict_84['vlan']=vlan
#     print('VLAN ID: %s' % vlan)
#     # 183 vlan config
#     vlan_config = sff_a2_84[183-128]
#     dict_84['vlan_config'] = vlan_config
#     print('VLAN Config: %s' % vlan_config)
#     # 184-185 controller_ipv4_pkt_dropped
#     controller_ipv4_pkt_dropped = sff_a2_84[184-128:186-128]
#     controller_ipv4_pkt_dropped = em_convert.convert_hexstring_to_intstring(controller_ipv4_pkt_dropped)
#     dict_84['pkt_dropped'] = controller_ipv4_pkt_dropped
#     print('controller ipv4 pkt dropped: %s' % controller_ipv4_pkt_dropped)
#     # 186-189 controller_ipv4_rx_pkt_cnt
#     controller_ipv4_rx_pkt_cnt = sff_a2_84[186-128:192-128]
#     controller_ipv4_rx_pkt_cnt = em_convert.convert_hexstring_to_intstring(controller_ipv4_rx_pkt_cnt)
#     dict_84['pkt_rx'] = controller_ipv4_rx_pkt_cnt
#     print('controller ipv4 rx pkt: %s' % controller_ipv4_rx_pkt_cnt)
#     # 190-193 controller_ipv4_tx_pkt_cnt
#     controller_ipv4_tx_pkt_cnt = sff_a2_84[192-128:196-128]
#     print(sff_a2_84[194 - 128:194 - 128])
#     controller_ipv4_tx_pkt_cnt = em_convert.convert_hexstring_to_intstring(controller_ipv4_tx_pkt_cnt)
#     dict_84['pkt_tx'] = controller_ipv4_tx_pkt_cnt
#     print('controller ipv4 tx pkt: %s' % controller_ipv4_tx_pkt_cnt)
#     # 194-195 controller_api_pkt_cnt
#     controller_api_pkt_cnt = sff_a2_84[194-128:196-128]
#     print(sff_a2_84[194-128:196-128])
#     controller_api_pkt_cnt = em_convert.convert_hexstring_to_intstring(controller_api_pkt_cnt)
#     dict_84['pkt_cnt'] = controller_api_pkt_cnt
#     print('controller api pkt: %s' % controller_api_pkt_cnt)
#     # 197 controller_watchdog_status
#     watchdog = sff_a2_84[197-128]
#     dict_84['watchdog'] = watchdog
#     print('controller watchdog status: %s' % watchdog)
#     # 198-199 controller_uptime
#     controller_uptime = sff_a2_84[198-128:200-128]
#     controller_uptime = em_convert.convert_hexstring_to_intstring(controller_uptime)

#     print('controller uptime: %s' % controller_uptime)
#     # 200 controller_cnt_clear

#     # 202 embox-7
#     embox7 = sff_a2_84[202-128]
#     print('embox-7: %s' %embox7)

#     # 205 ip alias
#     static_ip = sff_a2_84[204-128:208-128]
#     static_ip = [str(int(x, 16)) for x in static_ip]
#     static_ip_formated = '.'.join(static_ip)
#     dict_84['alias_ip']=static_ip_formated
#     print('Alias IP: %s' % static_ip_formated)

#     # 209 ip alias subnet
#     static_ip = sff_a2_84[208-128:212-128]
#     static_ip = [str(int(x, 16)) for x in static_ip]
#     static_ip_formated = '.'.join(static_ip)
#     dict_84['alias_subnet']=static_ip_formated
#     print('Alias Subnet: %s' % static_ip_formated)

#     return dict_84




# def print_a2_ff(sff_a2_ff):
#     if sff_a2_ff is None:
#         return False
#     print('-----------------------------------------------------------------------------------------------------------')
#     print('A2 page ff')
#     fw_version_hex = sff_a2_ff[130-128:166-128]
#     fw_version = ''.join(fw_version_hex)
#     print('FF: %s' % codecs.decode(fw_version, 'hex'))
#     if fw_version_hex[0] != '34':
#         print ("Error: Version of firware is not 4.x.x")
#         print(fw_version_hex[0])
#     else:
#         print("Firmware version is at latest major release.")

def get_firmware(ip, ports, username, password):
    session = arista(ip, ports, username, password)
    return session.firmwares
    
# def main(argv):
#     restip = None
#     aristaip = None
#     sfpport = None
#     emboxip = None
#     omnitekip = None
#     mellanoxip = None
#     totalphase = False
#     piip = None
#     try:
#         opts, args = getopt.getopt(sys.argv[1:],"hr:a:p:e:o:m:t",["restip=","aristaip=","sfpport=","emboxip=","omnitekip=","mellanox=", "totalphase", "pi="])
#     except getopt.GetoptError:
#         print_usage()
#         sys.exit(2)
#     for opt, arg in opts:
#         if opt == '-h':
#             print_usage()
#             sys.exit()
#         elif opt in ("-r", "--restip"):
#             restip = arg
#         elif opt in ("-a", "--aristaip"):
#             aristaip = arg
#         elif opt in ("-p", "--sfpport"):
#             sfpport = arg
#         elif opt in ("-e", "--emboxip"):
#             emboxip = arg
#         elif opt in ("-o", "--omnitek"):
#             omnitekip = arg
#         elif opt in ("-m", "--mellanox"):
#             mellanoxip = arg
#         elif opt in ("-t", "--totalphase"):
#             totalphase = True
#         elif opt in ("--pi"):
#             piip = arg

    # if len(argv) == 1:
    #     sff = {"a0":"03,04,83,20,00,00,00,00,00,00,00,06,68,00,00,00,00,00,00,00,45,4d,42,52,49,4f,4e,49,58,20,20,20,20,20,20,20,00,00,00,00,45,42,32,32,54,44,52,54,2d,53,4d,2d,30,35,32,30,33,20,20,20,00,00,00,22,00,02,00,00,31,31,38,30,33,31,35,30,30,31,33,34,20,20,20,20,31,38,30,33,31,35,20,20,68,90,05,4c,45,42,32,32,54,44,52,54,2d,53,4d,2d,30,35,32,30,20,20,20,20,20,20,20,20,33,20,20,20,00,00,00,00","shadow":"31,2e,31,2e,36,5f,47,43,43,20,37,2e,33,2e,30,5f,4a,75,6e,20,32,36,20,32,30,31,38,5f,31,35,3a,30,36,3a,34,33,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00","a2":"4b,00,ec,00,46,00,f1,00,8c,a0,75,30,87,8c,7a,a8,ff,ff,00,00,ff,ff,00,00,ff,ff,00,00,ff,ff,00,00,ff,ff,00,00,ff,ff,00,00,7f,ff,80,01,7f,ff,80,01,7f,ff,80,01,7f,ff,80,01,00,00,00,00,00,00,00,00,00,00,00,00,3f,80,00,00,00,00,00,00,01,00,00,00,01,00,00,00,01,00,00,00,01,00,00,00,00,00,00,27,37,70,81,14,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00","b2":"123"}
    #     sff['a0'] = sff['a0'].split(',')
    #     sff['a2'] = sff['a2'].split(',')
    # # REST
    # elif restip is not None:
    #     sff = send_command(restip, 'self/sff')
    #     sff['a0'] = sff['a0'].split(',')
    #     sff['a2'] = sff['a2'].split(',')

    # session = None
    # if aristaip is not None:
    #     session = arista.arista(aristaip, sfpport, sleep=False)
    # elif omnitekip is not None:
    #     session = omnitek.omnitek(omnitekip, sleep=False)
    # elif piip is not None:
    #     session = pi.pi(piip)
    # elif totalphase:
    #     session = aardvark.aardvark()
    # elif emboxip is not None:
    #     session = embox.emboxi2c(ip=emboxip, slot='0')

    # if session is not None:
    #     sff={}
        # A0
        # sff['a0'] = session.get_a0()

        # # MONITORING
        # sff['a2'] = session.read_page(monitoring=True)

        # # CONTROLLER
        # sff['a2_84'] = session.get_page('0x84')

        # BASE
        # sff['a2_ff'] = session.get_page('0xff')

    # PRINT SFF RESULT

    # print_a0(sff.get('a0', None))
    # print_a2(sff.get('a2', None))
    # print_a2_84(sff.get('a2_84', None))
    # print_a2_ff(sff.get('a2_ff', None))  # BASE


# if __name__ == "__main__":
#     sys.exit(main(sys.argv))
