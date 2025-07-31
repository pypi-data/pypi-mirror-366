# Ethernet CRC32 (polynomial 0xEDB88320)
import zlib

def compute_crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF
