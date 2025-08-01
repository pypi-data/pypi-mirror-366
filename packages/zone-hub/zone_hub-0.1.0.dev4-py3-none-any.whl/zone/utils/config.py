import time
from pathlib import Path
import yaml
import traceback

from zone.IDL.thrift.CommonNode.ttypes import arpPair, netInfo
from zone.IDL.thrift.SomeIpNode.ttypes import someipStackConfig, someipChannelConfig


class CAN_Config(object):
    software_channel_map = ["CAN" + str(i) for i in range(0, 64)]

    def __init__(
        self,
        software_channel: int,
        hardware_channel: str,
        database_channel: str,
        can_type: bool = False,
        arb_bitrate: int = 500000,
        data_bitrate: int = 2000000,
        sjwArb: int = 20,
        sjwDbr: int = 5,
        tseg1Abr=59,
        tseg1Dbr=14,
        tseg2Abr=20,
        tseg2Dbr=5,
        txreceipts=1,
        nsamplepos=75,
        dsamplepos=75,
        clockfreq=80,
        dprescaler=2,
        nprescaler=2,
    ):
        self.software_channel = self.software_channel_map[software_channel]
        self.hardware_channel = hardware_channel
        self.database_channel = database_channel
        self.can_type = can_type
        self.arb_bitrate = arb_bitrate
        self.data_bitrate = data_bitrate
        self.sjwArb = sjwArb
        self.sjwDbr = sjwDbr
        self.tseg1Abr = tseg1Abr
        self.tseg1Dbr = tseg1Dbr
        self.tseg2Abr = tseg2Abr
        self.tseg2Dbr = tseg2Dbr
        self.txreceipts = txreceipts
        self.nsamplepos = nsamplepos
        self.dsamplepos = dsamplepos
        self.clockfreq = clockfreq
        self.dprescaler = dprescaler
        self.nprescaler = nprescaler


class LIN_Config(object):
    software_channel_map = ["LIN" + str(i) for i in range(0, 64)]

    def __init__(
        self,
        software_channel: int,
        hardware_channel: str,
        database: str,
        is_master: bool = False,
        bitrate: int = 19200,
        deviceId=0x0,
        combaudrate=19200,
        major_version=2,
        minor_version=1,
        txreceipts=1,
        DLC=None,
    ):
        if DLC is None:
            DLC = []
        self.software_channel = self.software_channel_map[software_channel]
        # self.software_channel = software_channel
        self.hardware_channel = hardware_channel
        self.database = database
        self.is_master = 1 if is_master else 0
        self.bitrate = bitrate
        self.deviceId = deviceId
        self.combaudrate = combaudrate
        self.major_version = major_version
        self.minor_version = minor_version
        self.txreceipts = txreceipts
        self.DLC = DLC


class ETH_Config_PC(object):
    def __init__(self, ip_address: str, net_card_name: str, database: list):
        self.ip_address = ip_address
        self.iface = net_card_name
        self.eth_device = 0
        self.database = database


class ETH_Config_Vector(object):
    # arp dict e.g. {"ip": "192.168.1.13", "mac": 00:00:00:00:00:00}
    def __init__(
        self,
        ip_address: str,
        vector_port: str,
        subnet_mask: str,
        gateway: str,
        igmp_address: str,
        mac: str,
        vlan: int,
        arps: list = None,
        database: list = None,
    ):
        self.ip_address = ip_address
        self.vector_port = vector_port
        self.mask = [int(data) for data in subnet_mask.split(".")]
        self.gateway = [int(data) for data in gateway.split(".")]
        self.igmp_address = [int(data) for data in igmp_address.split(".")]
        self.mac_address = [int(data, base=16) for data in mac.split(":")]
        self.vlan = vlan
        self.eth_device = 1
        self.arps = arps
        self.database = database


class Config(object):
    pass
