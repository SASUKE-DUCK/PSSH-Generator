import requests
import base64
import xmltodict
import uuid
import argparse
import os
import json
import subprocess
import sys
import pyfiglet
from rich import print
from typing import DefaultDict
from pathlib import Path
from urllib.parse import urlparse

title = pyfiglet.figlet_format('PSSH Generator From ISM', font='slant')
print(f'[magenta]{title}[/magenta]')
print("Edit by -∞WKS∞-#3982")

WV_SYSTEM_ID = [237, 239, 139, 169, 121, 214, 74, 206, 163, 200, 39, 220, 213, 29, 33, 237]


def get_pssh_from_ism_manifest(manifest_link):
    r = requests.get(manifest_link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                           'Chrome/72.0.3626.121 Safari/537.36'})

    if r.status_code != 200:
        raise Exception(r.text)

    ism = xmltodict.parse(r.text)

    pssh = ism['SmoothStreamingMedia']['Protection']['ProtectionHeader']['#text']

    pr_pssh_dec = base64.b64decode(pssh).decode('utf16')
    pr_pssh_dec = pr_pssh_dec[pr_pssh_dec.index('<'):]
    pr_pssh_xml = xmltodict.parse(pr_pssh_dec)
    kid = base64.b64decode(pr_pssh_xml['WRMHEADER']['DATA']['KID']).hex()

    kid = uuid.UUID(kid).bytes_le

    init_data = bytearray(b'\x12\x10')
    init_data.extend(kid)
    init_data.extend(b'H\xe3\xdc\x95\x9b\x06')

    pssh = bytearray([0, 0, 0])
    pssh.append(32 + len(init_data))
    pssh[4:] = bytearray(b'pssh')
    pssh[8:] = [0, 0, 0, 0]
    pssh[13:] = WV_SYSTEM_ID
    pssh[29:] = [0, 0, 0, 0]
    pssh[31] = len(init_data)
    pssh[32:] = init_data

    print('\nPSSH: ', base64.b64encode(pssh))
    print('\nKID: {}'.format(kid.hex()))
    print("\nAll Done .....")    

def parse_urls(urls):
    found = []
    for u in urls:
        if u[len(u) - 1] == '/':
            u = u[:len(u) - 1]

        if u.startswith('http') or u.startswith('https'):
            url = urlparse(u)

            components = url.path.split('/')

            if 'manifest' not in components[len(components) - 1].lower():
                print('Wrong manifest, trying to fix automatically')
                u += '/Manifest'

            found.append(u)
        else:
            print('Invalid URL: ' + u)
            exit()
    return found


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="psshFromIsm: Calculates the kid/key id/PSSH Box from a .ism Manifest (Smooth Streaming) link"
    )

    parser.add_argument('urls',
                        help='The URLs to parse. You may need to wrap the URLs in double quotes if you have issues.',
                        nargs='+')

    args = parser.parse_args()

    links = parse_urls(args.urls)

    for link in links:
        get_pssh_from_ism_manifest(link)
