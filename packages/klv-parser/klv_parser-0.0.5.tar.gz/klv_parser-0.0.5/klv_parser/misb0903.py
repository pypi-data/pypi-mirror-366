#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

# The MIT License (MIT)
#
# Copyright (c) 2017 Matthew Pare (paretech@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from klv_parser.element import UnknownElement
from klv_parser.elementparser import BytesElementParser
from klv_parser.elementparser import DateTimeElementParser
from klv_parser.elementparser import MappedElementParser
from klv_parser.elementparser import StringElementParser
from klv_parser.elementparser import IntegerElementParser
from klv_parser.elementparser import LocationElementParser
from klv_parser.misb0601 import UASLocalMetadataSet
from klv_parser.setparser import SetParser
from klv_parser.seriesparser import SeriesParser


@UASLocalMetadataSet.add_parser
class VMTILocalSet(SetParser):
    """MISB ST0903 VMTI Metadata nested local set parser.
    Must be a subclass of Element or duck type Element.
    """
    key = b'\x4A'
    name = 'VMTI_Local_Set'
    TAG = 74
    UDSKey = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 06 00 00 00"
    LDSName = "VMTI Local Set"
    ESDName = ""
    UDSName = "Video Moving Target Indicator Local Set"

    key_length = 1
    parsers = {}

    _unknown_element = UnknownElement


@VMTILocalSet.add_parser
class Checksum(BytesElementParser):
    """Checksum used to detect errors within a UAV Local Set packet.

    Checksum formed as lower 16-bits of summation performed on entire
    LS packet, including 16-byte US key and 1-byte checksum length.

    Initialized from bytes value as BytesValue.
    """
    key = b'\x01'
    TAG = 1
    UDSKey = "-"
    LDSName = "Checksum"
    ESDName = ""
    UDSName = ""


@VMTILocalSet.add_parser
class PrecisionTimeStamp(DateTimeElementParser):
    """Precision Timestamp represented in microseconds.

    Precision Timestamp represented in the number of microseconds elapsed
    since midnight (00:00:00), January 1, 1970 not including leap seconds.

    See MISB ST 0601.11 for additional details.
    """
    key = b'\x02'
    TAG = 2
    UDSKey = "06 0E 2B 34 01 01 01 03 07 02 01 01 01 05 00 00"
    LDSName = "Precision Time Stamp"
    ESDName = ""
    UDSName = "User Defined Time Stamp"


@VMTILocalSet.add_parser
class SystemName(StringElementParser):
    """Mission ID is the descriptive mission identifier.

    Mission ID value field free text with maximum of 127 characters
    describing the event.
    """
    key = b'\x03'
    TAG = 3
    UDSKey = "06 0E 2B 34 01 01 01 01 01 05 05 00 00 00 00 00"
    LDSName = "Mission ID"
    ESDName = "Mission Number"
    UDSName = "Episode Number"
    min_length, max_length = 0, 127


@VMTILocalSet.add_parser
class LSVersionNumber(MappedElementParser):
    key = b'\x04'
    TAG = 4
    UDSKey = "-"
    LDSName = "Platform Tail Number"
    ESDName = "Platform Tail Number"
    UDSName = ""
    min_length, max_length = 0, 127
    _domain = (0, 2 ** 16 - 1)
    _range = (0, 65535)
    _error = None


@VMTILocalSet.add_parser
class NumberDetectedTargets(IntegerElementParser):
    key = b'\x05'
    TAG = 5
    UDSKey = "-"
    LDSName = "Number of Detected Targets"
    ESDName = "Number of Detected Targets"
    UDSName = ""

    _signed = False
    _size = 3


@VMTILocalSet.add_parser
class NumberReportedTargets(IntegerElementParser):
    key = b'\x06'
    TAG = 6
    UDSKey = "-"
    LDSName = "Number of Reported Targets"
    ESDName = "Number of Reported Targets"
    UDSName = ""

    _signed = False
    _size = 3


@VMTILocalSet.add_parser
class FrameNumber(IntegerElementParser):
    key = b'\x07'
    TAG = 5
    UDSKey = "-"
    LDSName = "Frame Number"
    ESDName = "Frame Number"
    UDSName = ""

    _signed = False
    _size = 3


@VMTILocalSet.add_parser
class FrameWidth(IntegerElementParser):
    key = b'\x08'
    TAG = 8
    UDSKey = "-"
    LDSName = "Frame Width"
    ESDName = "Frame Width"
    UDSName = ""

    _signed = False
    _size = 3


@VMTILocalSet.add_parser
class FrameHeight(IntegerElementParser):
    key = b'\x09'
    TAG = 9
    UDSKey = "-"
    LDSName = "Frame Height"
    ESDName = "Frame Height"
    UDSName = ""

    _signed = False
    _size = 3


@VMTILocalSet.add_parser
class SourceSensor(StringElementParser):
    key = b'\x0A'
    TAG = 10
    UDSKey = "-"
    LDSName = "Source Sensor"
    ESDName = "Source Sensor"
    UDSName = ""

    _encoding = 'UTF-8'
    min_length, max_length = 0, 127


@VMTILocalSet.add_parser
class VTargetSeries(SeriesParser):
    key = b'\x65'
    name = "VTarget Series"
    TAG = 101
    # key_length = 1
    parser = None


@VTargetSeries.set_parser
class VTargetPack(SetParser):
    name = "VMTI Target Pack" # will be overwritten by the track id
    # key_length = 0 # not needed cause there is no key for target object
    parsers = {}

    def __init__(self, value):
        """All parser needs is the value, no other information"""
        self.key, value = self.decode_ber_length(value)
        self.name = self.key
        super().__init__(value)


    @staticmethod
    def decode_ber_length(value):
        if not value[0] & 0x80:
            return np.uint32(value[0] & 0x7F), value[1:]
        buf = value[1: 1 + (value[0] & 0x7F)]
        out = 0
        for octet in buf:
            out <<= 8
            out += octet
        return np.uint32(out), value[1 + (value[0] & 0x7F):]


@VTargetPack.add_parser
class CentroidPixel(IntegerElementParser):
    key = b'\x01'
    TAG = 1
    UDSKey = "-"
    LDSName = "Centroid Pixel"
    ESDName = "Centroid Pixel"
    UDSName = ""

    _signed = False
    _size = 3


@VTargetPack.add_parser
class BoundingBoxTopLeftPixel(IntegerElementParser):
    key = b'\x02'
    TAG = 2
    UDSKey = "-"
    LDSName = "Bounding Box Top Left Pixel"
    ESDName = "Bounding Box Top Left Pixel"
    UDSName = ""

    _signed = False
    _size = 3


@VTargetPack.add_parser
class BoundingBoxBottomRightPixel(IntegerElementParser):
    key = b'\x03'
    TAG = 3
    UDSKey = "-"
    LDSName = "Bounding Box Bottom Right Pixel"
    ESDName = "Bounding Box Bottom Right Pixel"
    UDSName = ""

    _signed = False
    _size = 3

@VTargetPack.add_parser
class TargetPriority(IntegerElementParser):
    key = b'\x04'
    TAG = 4
    UDSKey = "-"
    LDSName = "Target Priority"
    ESDName = "Target Priority"
    UDSName = ""

    _signed = False
    _size = 1

@VTargetPack.add_parser
class TargetConfidenceLevel(IntegerElementParser):
    key = b'\x05'
    TAG = 5
    UDSKey = "-"
    LDSName = "Target Confidence Level"
    ESDName = "Target Confidence Level"
    UDSName = ""

    _signed = False
    _size = 1

@VTargetPack.add_parser
class DetectionCount(IntegerElementParser):
    key = b'\x06'
    TAG = 6
    UDSKey = "-"
    LDSName = "Detection Count"
    ESDName = "Detection Count"
    UDSName = ""

    _signed = False
    _size = 2

@VTargetPack.add_parser
class TargetColor(IntegerElementParser):
    key = b'\x08'
    TAG = 8
    UDSKey = "-"
    LDSName = "Target Color"
    ESDName = "Target Color"
    UDSName = ""

    _signed = False
    _size = 3


@VTargetPack.add_parser
class TargetIntensity(IntegerElementParser):
    key = b'\x09'
    TAG = 9
    UDSKey = "-"
    LDSName = "Target Intensity"
    ESDName = "Target Intensity"
    UDSName = ""

    _signed = False
    _size = 3


@VTargetPack.add_parser
class TargetLocationLatitudeOffset(LocationElementParser):
    key = b'\x0A'
    TAG = 10
    UDSKey = "-"
    LDSName = "Target Location Latitude Offset"
    ESDName = "Target Location Latitude Offset"
    UDSName = ""

@VTargetPack.add_parser
class TargetLocationLongitudeOffset(LocationElementParser):
    key = b'\x0B'
    TAG = 11
    UDSKey = "-"
    LDSName = "Target Location Longitude Offset"
    ESDName = "Target Location Longitude Offset"
    UDSName = ""
    _domain = (0, 2 **(8*3) - 1)
    _range = (-19.2, 19.2)
    units = 'degrees'

@VTargetPack.add_parser
class TargetHeight(MappedElementParser):
    key = b'\x0C'
    TAG = 12
    UDSKey = "-"
    LDSName = "Target Height"
    ESDName = "Target Height"
    UDSName = ""
    _domain = (0, 2 ** 16 - 1)
    _range = (-900, 19000)
    units = 'meters'

@VTargetPack.add_parser
class TargetLocation(LocationElementParser):
    key = b'\x11'
    TAG = 17
    UDSKey = "-"
    LDSName = "Target Location"
    ESDName = "Target Location"
    UDSName = ""

@VTargetPack.add_parser
class VObjectLS(SetParser):
    key = b'\x66'
    name = "VObject LS"
    TAG = 102
    # key_length = 1
    parsers = {}

@VObjectLS.add_parser
class Ontology(StringElementParser):
    key = b'\x01'
    TAG = 1
    UDSKey = "-"
    LDSName = "Ontology"
    ESDName = "Ontology"
    UDSName = ""

    min_length, max_length = 0, 127

@VObjectLS.add_parser
class OntologyClass(StringElementParser):
    key = b'\x02'
    TAG = 2
    UDSKey = "-"
    LDSName = "Ontology Class"
    ESDName = "Ontology Class"
    UDSName = ""

    min_length, max_length = 0, 127

@VTargetPack.add_parser
class VTrackerLS(SetParser):
    key = b'\x68'
    name = "VTracker LS"
    TAG = 104
    # key_length = 1
    parsers = {}

@VTrackerLS.add_parser
class Algorithm(StringElementParser):
    key = b'\x06'
    TAG = 6
    UDSKey = "-"
    LDSName = "Algorithm"
    ESDName = "Algorithm"
    UDSName = ""

    min_length, max_length = 0, 127