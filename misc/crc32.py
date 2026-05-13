import sys
import struct
import binascii
import os

FLASH_SECTOR_SIZE = 4096
MAGIC_VALUE = 0xf00d
COUNTER_FILE = os.path.join(os.path.dirname(__file__), '.build_counter')

elf_filename = sys.argv[1]
output_filename = sys.argv[2]
version_arg = sys.argv[3]

# Local extension: "<base>+auto" reads/increments misc/.build_counter and stamps
# (base + counter) so every rebuild has a strictly-greater version, which is what
# DeskHop's OTA path requires to trigger propagation between the two Picos.
if version_arg.endswith('+auto'):
    base = int(version_arg[:-len('+auto')])
    counter = 0
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            counter = int(f.read().strip() or '0')
    counter += 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(counter))
    version = (base + counter) % 65536
else:
    version = int(version_arg)

with open(elf_filename, 'r+b') as f:
    data = f.read()

    data = data[:-FLASH_SECTOR_SIZE]
    crc32_value = binascii.crc32(data) & 0xFFFFFFFF

with open(output_filename, 'wb') as f:
    f.write(struct.pack('<IHI', MAGIC_VALUE, int(version), crc32_value))
