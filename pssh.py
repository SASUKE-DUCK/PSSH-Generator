import base64
import os
import json
import subprocess
import argparse
import sys
import pyfiglet
from rich import print
from typing import DefaultDict
from pathlib import Path

title = pyfiglet.figlet_format('PSSH Generator', font='slant')
print(f'[magenta]{title}[/magenta]')
print("by -∞WKS∞-#3982")

print("\nGenerating PSSH:.....")
def read_pssh(path: str):
    raw = Path(path).read_bytes()
    pssh_offset = raw.rfind(b'pssh')
    _start = pssh_offset - 4
    _end = pssh_offset - 4 + raw[pssh_offset-1]
    pssh = raw[_start:_end]
    print('\nPSSH: ', base64.b64encode(pssh))
    return base64.b64encode(pssh)
pssh_b64= read_pssh('video.mp4')
print("\nAll Done .....")    