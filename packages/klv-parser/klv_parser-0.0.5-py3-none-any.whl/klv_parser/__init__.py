from .streamparser import StreamParser
from . import misb0601
from . import misb0903
from . import misb0102
from . import misbEG0104

from .element import UnknownElement

parser = StreamParser()

def parse_md(packet):
    md = {}
    for item in packet.items:
        if isinstance(packet.items[item], UnknownElement):
            continue
        elif hasattr(packet.items[item], 'items'):
            md[packet.items[item].name] = parse_md(packet.items[item])
        else:
            md[packet.items[item].name] = packet.items[item].value.value
    return md

def read(data: bytes):
    global parser
    metadata = {}
    # if parser is None:
    #     parser = StreamParser(data)
    # else:
    parser.set_source(data)
    for packet in parser:
        if isinstance(packet, UnknownElement):
            # Unparsed packets are ignored. Check manually if you need those and add custom implementations.
            print(f"Unknown element: {packet}")
            continue
        metadata = parse_md(packet)

    return metadata