from zone.IDL.thrift.CanStackNode.ttypes import (
    canMessage,
    canMessages,
    canChannelConfigs,
    canChannelConfig,
    frameCrcRcConfig,
    channel,
)
from zone.IDL.thrift.CanParserNode.ttypes import (
    canDbInfo,
    pduMessage,
    pduMessages,
    pduUpdate,
    pduCrcRcConfig,
    iSignalIPduEncode,
    iSignalIPduObj,
    dbConfigs,
    convertInput,
    subscribeInfo,
    dbConfigPair,
)
from zone.IDL.thrift.ConfigNode.ttypes import dbPath, canConfigInfo
from zone.IDL.thrift.SomeIpNode.ttypes import (
    someipInfo,
    someipPackage,
    someipServiceInfo,
    someipServiceInfos,
    someipStackConfig,
    someipChannelConfig,
)
from zone.IDL.thrift.LinStackNode.ttypes import (
    linStackStatus,
    linMessageConfig,
    linCrcConfig,
    linHeaderConfig,
    linMessageDataT,
)


class CanMessage(canMessage):
    pass


class CanMessages(canMessages):
    pass


class CanChannelConfigs(canChannelConfigs):
    pass


class CanDbinfo(canDbInfo):
    pass


class PduMessage(pduMessage):
    pass


class PduMessages(pduMessages):
    pass


class PduUpdate(pduUpdate):
    pass


class PduCrcRcConfig(pduCrcRcConfig):
    pass


class ISignaliPduEncode(iSignalIPduEncode):
    pass


class ISignaliPduObj(iSignalIPduObj):
    pass


class DbPath(dbPath):
    pass


class CanConfigInfo(canConfigInfo):
    pass


class SomeipInfo(someipInfo):
    pass


class SomeipPackage(someipPackage):
    pass


class SomeipServiceInfo(someipServiceInfo):
    pass


class SomeipServiceInfos(someipServiceInfos):
    pass


class SomeipStackConfig(someipStackConfig):
    pass


class SomeipChannelConfig(someipChannelConfig):
    pass


class LinStackStatus(linStackStatus):
    pass


class LinMessageConfig(linMessageConfig):
    pass


class LinCrcConfig(linCrcConfig):
    pass


class LinHeaderConfig(linHeaderConfig):
    pass


class LinMessageDataT(linMessageDataT):
    pass


class ConvertInput(convertInput):
    pass


class Channel(channel):
    pass


class SubscribeInfo(subscribeInfo):
    pass


class CanPdu(pduMessage, pduUpdate):
    """ """

    def __init__(self):
        super().__init__()


class CanConfig(dbConfigs, canChannelConfigs):
    """ """

    def __init__(self):
        super().__init__()


class CrcRcConfig(pduCrcRcConfig, frameCrcRcConfig):
    def __init__(self):
        super().__init__()


class CanChannelConfig(canChannelConfig, dbConfigPair):
    def __init__(self):
        canChannelConfig.__init__(self)
        self.channel_can = self.channel
        dbConfigPair.__init__(self)
        self.channel_db = self.channel


req = CanPdu()
req.channel = 1
req.pduName = "test"
req.period = 100
req.context = {"sig1:1,sig2:2"}
req.times = -1
