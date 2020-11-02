#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
def convert_temp(hex_temp_msb, hex_temp_lsb):
    int_temp_msb = int(hex_temp_msb, 16)
    int_temp_lsb = int(hex_temp_lsb, 16)
    int_temp_lsb = int_temp_lsb / 255
    if int_temp_msb > 128:
        int_temp_msb = int_temp_msb-256
    temp = '%s.%s' % (int_temp_msb, int_temp_lsb)

    return temp

def convert_hexstring_to_intstring(hex):
    hex_str = ''.join(hex)
    return int(hex_str, 16)

def convert_ext_identifier(ext_identifier):
    dict_ext_identifier={
        '00': '',
        '01': 'MOD_DEF 1',
        '02': 'MOD_DEF 2',
        '03': 'MOD_DEF 3',
        '04': 'I2C',
        '05': 'MOD_DEF 5',
        '06': 'MOD_DEF 6',
        '07': 'MOD_DEF 7',
        '08-FF': 'Unallocated',
    }

    return dict_ext_identifier.get(ext_identifier, 'Unallocated')

def convert_connector(connector):
    dict_connector={
        '00': 'Unknown or unspecified',
        '01': 'SC',
        '02': 'Fibre Channel Style 1 copper connector',
        '03': 'Fibre Channel Style 2 copper connector',
        '04': 'BNC/TNC',
        '05': 'Fibre Channel coaxial headers',
        '06': 'Fiber Jack',
        '07': 'LC',
        '08': 'MT-RJ',
        '09': 'MU',
        '0A': 'SG',
        '0B': 'Optical pigtail',
        '0C': 'MPO Parallel Optic',
        '20': 'HSSDC II',
        '21': 'Copper pigtail',
        '22': 'RJ45',
    }

    return dict_connector.get(connector, 'N/A')

def convert_encoding(encoding):
    dict_encoding={
        '00': 'Unspecified',
        '01': '8B/10B',
        '02': '4B/5B',
        '03': 'NRZ',
        '04': 'Manchester',
        '05': 'SONET Scrambled',
        '06': '64B/66B',
    }

    return dict_encoding.get(encoding, 'Unallocated')

def convert_sdi_bit_rate(sdi_bit_rate):
    dict_bit_rate={
        '00': 'HD',
        '01': 'SD',
        '10': '3G'
    }

    return dict_bit_rate.get(sdi_bit_rate)

def convert_sdi_sampling_format(sdi_sampling_format):
    dict_sdi_sampling_format={
        '0000': '422_ycbcr',
        '0001': '444_ycbcr',
        '0010': '444_rgb',
        '0011': '420',
        '0100': '4224_ycbcra',
        '0101': '4444_ycbcra',
        '0110': '4444_rgba',
        '0111': 'smpte2048',
        '1000': '4224_ycbcrd',
        '1001': '4444_ycbcrd',
        '1010': '4444_rgbd'
    }

    return dict_sdi_sampling_format.get(sdi_sampling_format)

def convert_sdi_frame_rate(sdi_frame_rate):
    dic_sdi_frame_rate={
        '0000': 'undefined',
        '0001': 'reserved',
        '0010': '24 / 1.001',
        '0011': '24',
        '0100': '48 / 1.001',
        '0101': '25',
        '0110': '30 / 1.001',
        '0111': '30',
        '1000': '48',
        '1001': '50',
        '1010': '60 / 1.001',
        '1011': '60'
    }

    return dic_sdi_frame_rate.get(sdi_frame_rate)

def convert_sdi_video_format(sdi_video_format):
    dict_sdi_video_format={
    '0000': 'SMPTE ST 274 1920x1080',
    '0001': 'SMPTE ST 296 1280x720',
    '0010': 'SMPTE 2048 - 2 2048x1080',
    '0011': 'SMPTE 295 1920x1080',
    '1000': 'NTSC 720x486',
    '1001': 'PAL 720x576',
    '1111': 'unknown'
    }

    return dict_sdi_video_format.get(sdi_video_format)

def format_ip(hex_ip):
    hex_ip = [str(int(x, 16)) for x in hex_ip]
    ip_formated = '.'.join(hex_ip)

    return ip_formated

def get_video_fmt(scan, rate, family):
    if all([scan==1,rate==5,family==1]):
        return '720p25'
    if all([scan==1,rate==6,family==1]):
        return '720p29'
    if all([scan==1,rate==7,family==1]):
        return '720p30'
    if all([scan==1,rate==9,family==1]):
        return '720p50'
    if all([scan==1,rate==10,family==1]):
        return '720p59'
    if all([scan==1,rate==11,family==1]):
        return '720p60'

    if all([scan==0,rate==5,family==0]):
        return '1080i50'
    if all([scan==0,rate==6,family==0]):
        return '1080i59'
    if all([scan==0,rate==7,family==0]):
        return '1080i60'

    if all([scan==1,rate==2,family==0]):
        return '1080p23'
    if all([scan==1,rate==3,family==0]):
        return '1080p24'
    if all([scan==1,rate==5,family==0]):
        return '1080p25'
    if all([scan==1,rate==6,family==0]):
        return '1080p29'
    if all([scan==1,rate==7,family==0]):
        return '1080p30'
    if all([scan==1,rate==9,family==0]):
        return '1080p50'
    if all([scan==1,rate==10,family==0]):
        return '1080p59'
    if all([scan==1,rate==11,family==0]):
        return '1080p60'

    if all([scan==0,rate==6,family==8]):
        return '525i59'
    if all([scan==0,rate==5,family==9]):
        return '625i50'

    return ''


def get_video_format_generic(family, rate, scan):
    f = ''
    family_dict = {'0': 'SMPTE ST274 (1920x1080)',
                   '1': 'SMPTE ST296 (1280x720)',
                   '2': 'SMPTE 2048-2 (2048x1080)',
                   '3': 'SMPTE 295 (1920x1080)',
                   '8': 'NTSC (720x486)', '9': 'PAL (720x576)'}
    if family not in family_dict:
        f = 'Unknown'
    else:
        f = family_dict[str(family)]

    rate_dict = {'2': '23.98Hz', '3': '24Hz', '4': '47.95Hz',
                 '5': '25Hz', '6': '29.97Hz', '7': '30Hz', '8': '48Hz',
                 '9': '50Hz', '10': '59.94Hz', '11': '60Hz'}
    if rate not in rate_dict:
        r = 'Unknow'
    else:
        r = rate_dict[str(rate)]
    if scan == 0:
        s = 'Interlace'
    elif scan == 1:
        s = 'Progressive'
    else:
        s = 'Unknow'
    return f'{f} {r} {s}'