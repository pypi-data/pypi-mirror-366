import yaml
import os
from enum import Enum
from collections import defaultdict

try:
    exec_entry_path_ = os.path.dirname(__file__)
    config_yaml_file = os.path.join(
        exec_entry_path_, "etc", "zonemaster_config.yaml"
    )
    with open(config_yaml_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
except Exception as e_:
    data = defaultdict(lambda: 9000)
    raise


class Dir(Enum):
    Rx = 0
    Tx = 1


class HardWare(Enum):
    VECTOR = 0x1
    PCAN = 0x2
    BUSMUST = 0x4
    USBDEVICE = 0x8
    FIRE2 = 0x10


# 节点名字 >>>>>>>>>>>>>>>>>>>>>>>>>>>
NAME_LIN_PARSER_NODE = "LIN_PARSER_NODE"
NAME_LIN_STACK_NODE = "LIN_STACK_NODE"
NAME_CAN_PARSER_NODE = "CAN_PARSER_NODE"
NAME_CAN_STACK_NODE = "CAN_STACK_NODE"
NAME_SOMEIP_NODE = "SOMEIP_NODE"
NAME_LOG_REPLAY_NODE = "LOG_REPLAY_NODE"
NAME_CAN_UDS_NODE = "CAN_UDS_NODE"
NAME_CONFIG_NODE = "CONFIG_NODE"
NAME_TCPIP_STACK_NODE = "TCPIP_STACK_NODE"
NAME_DOIP_UDS_NODE = "DOIP_UDS_NODE"
NAME_PROCESS_NODE = "PROCESS_NODE"
NAME_FIRE2_STACK_NODE = "FIRE2_STACK_NODE"
NAME_XCP_ON_CAN_NODE = "XCP_ON_CAN_NODE"
# 节点名字 <<<<<<<<<<<<<<<<<<<<<<<<<<


# RPC 常量 >>>>>>>>>>>>>>>>>>>>>>>>>
CAN_STACK_NODE_IP = "127.0.0.1"
CAN_STACK_NODE_PORT = data["CAN_STACK_NODE_PORT"]

SOMEIP_STACK_NODE_IP = "127.0.0.1"
SOMEIP_STACK_NODE_PORT = data["SOMEIP_STACK_NODE_PORT"]

LIN_STACK_NODE_IP = "127.0.0.1"
LIN_STACK_NODE_PORT = data["LIN_STACK_NODE_PORT"]

LIN_PARSER_NODE_IP = "127.0.0.1"
LIN_PARSER_NODE_PORT = data["LIN_PARSER_NODE_PORT"]

CAN_PARSER_NODE_IP = "127.0.0.1"
CAN_PARSER_NODE_PORT = data["CAN_PARSER_NODE_PORT"]

LOG_REPLAY_NODE_IP = "127.0.0.1"
LOG_REPLAY_NODE_PORT = data["LOG_REPLAY_NODE_PORT"]

PROCESS_NODE_IP = "127.0.0.1"
PROCESS_NODE_PORT = data["PROCESS_NODE_PORT"]

CAN_UDS_NODE_IP = "127.0.0.1"
CAN_UDS_NODE_PORT = data["CAN_UDS_NODE_PORT"]

TCPIP_STACK_NODE_IP = "127.0.0.1"
TCPIP_STACK_NODE_PORT = data["TCPIP_STACK_NODE_PORT"]

CONFIG_NODE_IP = "127.0.0.1"
CONFIG_NODE_PORT = data["CONFIG_NODE_PORT"]

DOIP_UDS_NODE_IP = "127.0.0.1"
DOIP_UDS_NODE_PORT = data["DOIP_UDS_NODE_PORT"]

FIRE2_STACK_NODE_IP = "127.0.0.1"
FIRE2_STACK_NODE_PORT = data["FIRE2_STACK_NODE_PORT"]

XCP_ON_CAN_NODE_IP = "127.0.0.1"
XCP_ON_CAN_NODE_PORT = data["XCP_ON_CAN_NODE_PORT"]
# RPC 常量 >>>>>>>>>>>>>>>>>>>>>>


PRE_NODES = {
    NAME_LOG_REPLAY_NODE: (LOG_REPLAY_NODE_IP, LOG_REPLAY_NODE_PORT),
    NAME_CONFIG_NODE: (CONFIG_NODE_IP, CONFIG_NODE_PORT),
}

# 用户使能NODE信息
USER_NODES = {
    NAME_CAN_STACK_NODE: (CAN_STACK_NODE_IP, CAN_STACK_NODE_PORT),
    NAME_CAN_PARSER_NODE: (CAN_PARSER_NODE_IP, CAN_PARSER_NODE_PORT),
    NAME_CAN_UDS_NODE: (CAN_UDS_NODE_IP, CAN_UDS_NODE_PORT),
    NAME_DOIP_UDS_NODE: (DOIP_UDS_NODE_IP, DOIP_UDS_NODE_PORT),
    NAME_LIN_STACK_NODE: (LIN_STACK_NODE_IP, LIN_STACK_NODE_PORT),
    NAME_LIN_PARSER_NODE: (LIN_PARSER_NODE_IP, LIN_PARSER_NODE_PORT),
    NAME_SOMEIP_NODE: (SOMEIP_STACK_NODE_IP, SOMEIP_STACK_NODE_PORT),
    NAME_TCPIP_STACK_NODE: (TCPIP_STACK_NODE_IP, TCPIP_STACK_NODE_PORT),
    NAME_XCP_ON_CAN_NODE: (XCP_ON_CAN_NODE_IP, XCP_ON_CAN_NODE_PORT),
}

# DDS DOMAIN_ID >>>>>>>>>>>>>>>>>>>>>>>>
LIN_PARSER_NODE_DDS_ID = data["DDS_DomainId"]
LIN_STACK_NODE_DDS_ID = data["DDS_DomainId"]
CAN_PARSER_NODE_DDS_ID = data["DDS_DomainId"]
CAN_STACK_NODE_DDS_ID = data["DDS_DomainId"]
SOMEIP_NODE_DDS_ID = data["DDS_DomainId"]
LOG_REPLAY_NODE_DDS_ID = data["DDS_DomainId"]
CAN_UDS_NODE_DDS_ID = data["DDS_DomainId"]
CONFIG_NODE_DDS_ID = data["DDS_DomainId"]
TCPIP_STACK_NODE_DDS_ID = data["DDS_DomainId"]
DOIP_UDS_NODE_DDS_ID = data["DDS_DomainId"]
PROCESS_NODE_DDS_ID = data["DDS_DomainId"]
FRONTEND_NODE_DDS_ID = data["DDS_DomainId"]
XCP_ON_CAN_NODE_DDS_ID = data["DDS_DomainId"]
# DDS DOMAIN_ID <<<<<<<<<<<<<<<<<<<<<<<<<<


# DDS TOPIC_INFO >>>>>>>>>>>>>>>>>>>>>>>>
class canMessageTopic(object):
    NAME = "canMessageTopic"
    IDL = "canMessageData"


class canUdsTopic(object):
    NAME = "canUdsTopic"
    IDL = "canMessageData_uds"


class doipUdsTopic(object):
    NAME = "DoipUdsTopic"
    IDL = "DoipMessageData"


class linMessageTopic(object):
    NAME = "linMessageTopic"
    IDL = "linMessageData"


class linParserTopic(object):
    NAME = "linParserTopic"
    IDL = "linParserData"


class someipPackage(object):
    NAME = "someipPackageTopic"
    IDL = "SomeIpParserData"


class someIpCalling(object):
    NAME = "someIpCallingTopic"
    IDL = "SomeIpParserData"


class someIpState(object):
    NAME = "someIpStateTopic"
    IDL = "SomeIpStateData"


class someIpSD(object):
    NAME = "someIpSDTopic"
    IDL = "SomeIpSDData"


class canParserTopic(object):
    NAME = "canParserTopic"
    IDL = "canParserData"


class canPduTopic(object):
    NAME = "canPduTopic"
    IDL = "canParserData"


class canContainerPduTopic(object):
    NAME = "canContainerPduTopic"
    IDL = "canParserData"


class SomeipByPass(object):
    NAME = "SomeipByPassTopic"
    IDL = "SomeIpParserData"


class EthFrame(object):
    NAME = "EthFrameTopic"
    IDL = "ethFrameData"


class SomeIpSdByPass(object):
    NAME = "SomeIpSdByPassTopic"
    IDL = "SomeipSdParserData"


if __name__ == "__main__":
    print(data["CONFIG_NODE_PORT"])
