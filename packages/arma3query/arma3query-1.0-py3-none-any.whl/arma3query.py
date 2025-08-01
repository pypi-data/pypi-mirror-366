import a2s
from enum import Enum
from a2s import byteio
import io
from a2s.exceptions import BufferExhaustedError
import asyncio

ESCAPE_SEQUENCES = [(b"\x01\x02", b"\x00"), (b"\x01\x03", b"\xFF"), (b"\x01\x01", b"\x01")]

class DlcFlags(Enum):
    kart = 0x1
    Marksmen = 0x2
    Heli = 0x4
    Curator = 0x8
    Expansion = 0x10
    Jets = 0x20
    Orange = 0x40
    Argo = 0x80
    TacOps = 0x100
    Tanks = 0x200
    Contact = 0x400
    Enoch = 0x800

class ArmaMod:
    def __init__(self, hash_val, workshop_id, name):
        self.hash = hash_val
        self.workshop_id = workshop_id
        self.name = name

    def __repr__(self):
        return f"ArmaMod(hash={self.hash}, workshop_id={self.workshop_id}, name={self.name!r})"

class ArmaRules:
    def __init__(self):
        self.protocol_version = None
        self.general_flags = None
        self.dlc_flags = None
        self.dlcs = []
        self.difficulty_raw = None
        self.difficulty_flags = {}
        self.ai_level = None
        self.difficulty_level = None
        self.mods_count = 0
        self.mods = []
        self.signatures_count = 0
        self.signatures = []

def _parse_rules_data(rules) -> ArmaRules:
    total = list(rules.keys())[0][1]
    chunks = {}

    for (k, v) in rules.items():
        for s, r in ESCAPE_SEQUENCES:
            v = v.replace(s, r)
        chunks[list(k)[0]] = v

    combined = bytearray()
    for i in sorted(chunks):
        combined.extend(chunks[i])

    stream = io.BytesIO(combined)
    message = byteio.ByteReader(stream, endian="<")

    arma_rules = ArmaRules()

    arma_rules.protocol_version = message.read_uint8()
    assert arma_rules.protocol_version == 3

    arma_rules.general_flags = message.read_uint8()

    arma_rules.dlc_flags = message.read_uint16()
    for d in DlcFlags:
        if d.value & arma_rules.dlc_flags:
            arma_rules.dlcs.append(d)

    arma_rules.difficulty_raw = message.read_uint16()
    flags = arma_rules.difficulty_raw

    arma_rules.difficulty_flags = {
        "third_person_camera": bool(flags & 0x01),
        "advanced_flight_model": bool(flags & 0x02),
        "weapon_crosshair": bool(flags & 0x04),
    }

    # Extract AI & Difficulty level (3 bits each)
    arma_rules.ai_level = (flags >> 3) & 0b111
    arma_rules.difficulty_level = (flags >> 6) & 0b111

    for _ in DlcFlags:
        message.read_uint32()  # Skip DLC hashes

    arma_rules.mods_count = message.read_uint8()

    for _ in range(arma_rules.mods_count):
        try:
            mod_hash = message.read_uint32()
        except BufferExhaustedError:
            break

        steam_id_field = message.read_uint8()
        steam_id_len = steam_id_field & 0b1111
        workshop_id_bytes = message.read(steam_id_len)
        workshop_id = int.from_bytes(workshop_id_bytes, byteorder="little")

        name_len = message.read_uint8()
        name_bytes = message.read(name_len)
        name = name_bytes.decode("utf-8", errors="replace")

        # REPLACE workshop_id if it's 0
        if workshop_id == 0:
            workshop_id = f"{name.replace(' ', '')}"

        arma_rules.mods.append(ArmaMod(mod_hash, workshop_id, name))

    arma_rules.signatures_count = message.read_uint8()
    for _ in range(arma_rules.signatures_count):
        sig_len = message.read_uint8()
        sig_hash = int.from_bytes(message.read(sig_len), byteorder="little")
        arma_rules.signatures.append(sig_hash)
    arma_rules.mods.sort(key=lambda m: m.name.lower())
    return arma_rules

def arma3rules(addr) -> ArmaRules:
    """Synchronous Arma 3 rules query and decode"""
    rules = a2s.rules(addr, encoding=None)
    return _parse_rules_data(rules)

async def arma3rules_async(addr) -> ArmaRules:
    """Async Arma 3 rules query and decode"""
    rules = await asyncio.to_thread(a2s.rules, addr, encoding=None)
    return _parse_rules_data(rules)
