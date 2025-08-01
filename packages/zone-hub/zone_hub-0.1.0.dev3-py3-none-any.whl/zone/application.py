from zone.IDL.thrift.CanParserNode.ttypes import *
from zone.IDL.thrift.CanStackNode.ttypes import *
from zone.IDL.thrift.CommonNode import Result
from zone.dsc import (
    CanPdu,
    CanConfig,
    CrcRcConfig,
    ConvertInput,
    PduCrcRcConfig,
    CanMessage,
    PduMessage,
    PduMessages,
    DbPath,
    PduUpdate,
    CanMessages,
    Channel,
    SubscribeInfo,
    CanChannelConfig,
)
from .utils.dsx import as_list
from .utils.snippets import normalize_components

from zone.clients import (
    canstackclient,
    canparserclient,
    linstackclient,
    linparserclient,
)


class App(object):
    """
    Application的入口。
    """

    def __init__(
        self,
        *,
        configs=None,
        connections=None,
        canstack=None,
        canparser=None,
        linstack=None,
        linparser=None,
        data=None
    ) -> None:
        """ """
        self._configs = as_list(configs)
        self._connections = as_list(connections)
        self._clients = []
        self._canstack = canstack or canstackclient
        self._canparser = canparser or canparserclient
        self._linstack = linstack or linstackclient
        self._linparser = linparser or linparserclient
        self._data = data
        self._clients = {
            "canstack": self._canstack,
            "canparser": self._canparser,
            "linstack": self._linstack,
            "linparser": self._linparser,
        }

    @property
    def Configs(self):
        return self._configs

    @Configs.setter
    def Configs(self, value):
        self._configs = as_list(value)

    @property
    def Connections(self):
        return self._connections

    @Connections.setter
    def Connections(self, value):
        self._connections = as_list(value)

    @property
    def CanStack(self):
        return self._canstack

    @CanStack.setter
    def CanStack(self, value):
        self._canstack = value

    @property
    def CanParser(self):
        return self._canparser

    @CanParser.setter
    def CanParser(self, value):
        self._canparser = value

    @property
    def LinStack(self):
        return self._linstack

    @LinStack.setter
    def LinStack(self, value):
        self._linstack = value

    @property
    def LinParser(self):
        return self._linparser

    @LinParser.setter
    def LinParser(self, value):
        self._linparser = value

    @property
    def Clients(self):
        return self._clients

    @property
    def DataModel(self):
        return self._data

    # api
    def connect(self, components: list = None) -> dict:
        """
        连接部件。

        :param components: 需要连接的组件。
        :type components: 列表，list

        .. note::

            列表中可能的值是"canstack", "canparser", "linstack", "linparser"。

            例如 app.connect(["canstack", "canparser"])。

            当只有一个元素时候可以单纯写字符串，例如 app.connect("canstack")。

            如果要连接所有的四个组件，canstack、canparser、linstack、linparser，可以用 app.connect(["all"]) 表示。

        :return: 连接结果的字典
        :rtype: dict of :class:`~zone.IDL.thrift.CommonNode.Result`

        .. note::

            例如 dict("canstack": result(result=0, reason="connected"))
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].connect()
                print(result)
                results[i] = result
        return results

    def connect_all(self) -> dict:
        """
        连接所有部件。即

        .. note::

            app.connect()

        :return: 连接结果的字典
        :rtype: dict of :class:`~zone.IDL.thrift.CommonNode.Result`

        .. note::

            例如 dict("canstack": result(result=0, reason="connected"))
        """
        return self.connect()

    def disconnect(self, components: list = None) -> dict:
        """
        断开组件。

        :param components: 断开连接的组件。
        :type components: 列表，list

        .. note::

            列表中可能的值是"canstack", "canparser", "linstack", "linparser"。

            例如 app.disconnect(["canstack", "canparser"])。

            当只有一个元素时候可以单纯写字符串，例如 app.disconnect("canstack")。

            如果要断开所有的四个组件，canstack、canparser、linstack、linparser，可以用 app.disconnect(["all"]) 表示。

        :return: 断开操作结果的字典
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`

        .. note::

            例如 dict("canstack": result(result=0, reason="disconnected"))
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].disconnect()
                print(result)
                results[i] = result
        return results

    def disconnect_all(self) -> dict:
        """
        断开所有组件。即

        .. note::

            app.connect()

        :return: 断开操作结果的字典
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self.disconnect()

    def getStatus(self, components: list = None) -> dict:
        """
        获得组件状态。

        :param components: 获取状态的组件。
        :type components: 列表，list

        .. note::

            列表中可能的值是"canstack", "canparser", "linstack", "linparser"。

            例如 app.getStatus(["canstack", "canparser"])。

            当只有一个元素时候可以单纯写字符串，例如 app.getStatus("canstack")。

            如果要断开所有的四个组件，canstack、canparser、linstack、linparser，可以用 app.getStatus(["all"]) 表示。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`

        .. note::

            例如 dict("canstack": result(result=0, reason="connected"))
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].getStatus()
                print(result)
                results[i] = result
        return results

    def setCrcRcConfig(self, req: CrcRcConfig) -> Result:
        # canstack and canparser
        """
        设置CRC RC配置。

        :param req: CrcRc配置的实例。
        :type req: CrcRcConfig

        .. code:: python

            from zone.dsc import CrcRcConfig
            config = CrcRcConfig()
            config.channel = xxx
            config.crcBitStarts = xxx
            config.crcName = xxx
            config.crcTable = xxx
            config.pduName = xxx
            config.rcBitStarts = xxx
            config.rcConfig = xxx
            config.rcName = xxx
            ret = app.setCrcRcConfig(config)

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        ret = self._canstack.setCrcRcConfig(req)
        ret = self._canparser.setCanParserCrcRcConfig(req)
        return ret

    def clearCrcRcConfig(self, req: CrcRcConfig) -> Result:
        # canstack and canparser
        """
        清除CRC RC配置。

        :param req: CrcRc配置的实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        ret = self._canstack.clearCrcRcConfig(req)
        ret = self._canparser.clearCrcRcConfig(req)
        return ret

    def clearAllCrcRcConfig(self) -> Result:
        # canstack and canparser
        # todo
        """
        清除所有的CRC RC配置。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        ret = self._canstack.clearAllCrcRcConfig()
        ret = self._canparser.clearAllCrcRcConfig()
        return ret

    def checkAlive(self, components: list = None) -> dict:
        """
        检查组件的活跃度。

        :param components: 检查活跃度的组件。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].checkAlive()
                print(result)
                results[i] = result
        return results

    def start(self, components: list = None) -> dict:
        """
        启动组件。

        :param components: 需要启动的组件。

        :return: 启动组件状态的字典
        :rtype: dict of :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                if hasattr(self._clients[i], "start") and callable(
                    getattr(self._clients[i], "start")
                ):
                    result = self._clients[i].start()
                    results[i] = result
        return results

    def stop(self, components: list = None) -> dict:
        """
        停止组件。

        :param components: 需要停止的组件。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                if hasattr(self._clients[i], "stop") and callable(
                    getattr(self._clients[i], "stop")
                ):
                    result = self._clients[i].checkAlive()
                    results[i] = result
        return results

    # # can stack

    def getVersion(self) -> Result:
        """
        获取版本。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getVersion()

    def setCanConfig(self, req: CanConfig) -> Result:
        """
        设置CAN配置。

        :param req: 设置CAN的配置实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        ret = self._canparser.setCanConfig(req)
        ret = self._canstack.setConfigs(req)
        return ret

    def sendCanPdu(self, req: CanPdu) -> Result:
        """
        发送CANPDU。

        :param req: 发送CANPDU的实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        ret = self._canparser.updateCanPdu(req)
        ret = self._canparser.sendCanPduCyc(req)
        return ret

    def stopCanPdu(self, req: CanPdu) -> Result:
        """
        停止发送CANPDU。

        :param req: 停止的CANPDU实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.sendCanPduCyc(req)

    def setConfigs(self, req: CanConfig) -> Result:
        """
        设置配置。

        :param req: 需要设置的Can配置实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.setConfigs(req)

    def startCanStack(self) -> Result:
        """
        启动CAN。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.startCanStack()

    def stopCanStack(self) -> Result:
        """
        停止CAN。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.stopCanStack()

    def clearCanSend(self) -> Result:
        """
        清除CAN。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.clearCanSend()

    def clearCanAllCrcRcConfig(self) -> Result:
        """
        清除所有CAN CRC Rc 配置。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.clearAllCrcRcConfig()

    def sendCanMessageCyc(self, req: CanMessage) -> Result:
        """
        循环发送CAN消息。

        :param req: 循环发送的CAN消息实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.sendCanMessageCyc(req)

    def sendCanMessage(self, req: CanMessage) -> Result:
        """
        发送CAN消息。

        :param req: 发送的CAN消息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.sendCanMessage(req)

    def sendCanMessages(self, req: CanMessages, stmin: int) -> Result:
        """
        发送CAN消息列表。

        :param req: CAN消息。
        :param stmin: 每条报文的间隔时间。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.sendCanMessages(req, stmin)

    def getStackStatus(self) -> Result:
        """
        获取状态。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getStatus()

    def stopChannelSendCyc(self, req: Channel) -> Result:
        """
        循环停止通道发送。

        :param req: 通道实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.stopChannelSendCyc(req)

    def sendCan(self, req: CanMessage) -> Result:
        """
        发送CAN消息。

        :param req: CAN消息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.sendCan(req)

    def getChannelBusloadCurrent(self, req: Channel) -> Result:
        """
        获取通道当前总线负载率。

        :param req: 通道实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getChannelBusloadCurrent(req)

    def getChannelBusloadMax(self, req: Channel) -> Result:
        """
        获取通道最大总线负载率。

        :param req: 通道实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getChannelBusloadMax(req)

    def getChannelBusloadAvg(self, req: Channel) -> Result:
        """
        获取通道平均总线负载率。

        :param req: 通道实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getChannelBusloadAvg(req)

    def getChannelErrorFrameTotal(self, req: Channel) -> Result:
        """
        获取通道错误帧总数。

        :param req: 通道实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canstack.getChannelErrorFrameTotal(req)

    def setCanChannelConfig(self, req: list[CanChannelConfig]):
        """
        设置CAN通道的配置

        :param req: CAN通道配置的列表

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        canchannel_configs = canChannelConfigs()
        dbconfigs = dbConfigs()
        canchannel_configs.configs = []
        dbconfigs.configs = []
        for item in req:
            canchannel_configs.configs.append(item)
            dbconfigs.configs.append(item)
        self._canstack.setConfigs(canchannel_configs)
        self._canparser.setConfig(dbconfigs)

    def clearAllCanParserCrcRcConfig(self) -> Result:
        """
        清除所有CANParser的CRC RC配置。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.clearAllCanParserCrcRcConfig()

    def clearCanParserCrcRcConfig(self, req: PduCrcRcConfig) -> Result:
        """
        清除CANParser的CRC RC配置。

        :param req: 需要操作的PduCrcRc配置实例。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.clearCanParserCrcRcConfig(req)

    def sendCanFrameCyc(self, req: CanMessage) -> Result:
        """
        循环发送CAN帧。

        :param req: 发送到的CAN消息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.sendCanFrameCyc(req)

    def sendCanPduCyc(self, req: PduMessage) -> Result:
        """
        循环发送CANPDU。

        :param req: 发送的PDU消息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.sendCanPduCyc(req)

    def sendCanPduCycList(self, req: PduMessages) -> Result:
        """
        发送CANPDU循环列表。

        :param req: 循环发送的PDU消息列表。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.sendCanPduCycList(req)

    def addCanDbFile(self, db_path: str) -> Result:
        """
        添加数据库文件。

        :param db_path: 添加的数据库路径。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.addDbFile(dbPath(dbPath=db_path))

    def getCanDbConfigs(self) -> Result:
        """
        获取CAN数据库配置。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.getCanDbConfigs()

    def getCanDbPath(self) -> Result:
        """
        获取CAN数据库路径。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.getCanDbPath()

    def subscribeMsg(self, req: SubscribeInfo) -> Result:
        """
        订阅消息。

        :param req: 订阅信息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.subscribeMsg(req)

    def unSubscribeMsg(self, req: SubscribeInfo) -> Result:
        """
        退订消息。

        :param req: 退订的订阅消息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.unSubscribeMsg(req)

    def getCanDbInfo(self) -> Result:
        """
        获取CAN数据库信息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.getCanDbInfo()

    def clear(self) -> Result:
        """
        清理。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.clear()

    def clearCanStackSubscribe(self) -> Result:
        """
        清除CAN订阅。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.clearCanStackSubscribe()

    def encodePdu(self, req: iSignalIPduObj) -> Result:
        """
        编码PDU。

        :param req: 编码的PDU信号。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.encodePdu(req)

    def convertCanDbToPy(self, req: ConvertInput) -> Result:
        """
        把CAN数据库转换成Python文件。

        :param req: 转换输入。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.convertCanDbToPy(req)

    def convertCanDbToJson(self, req: ConvertInput) -> Result:
        """
        把CAN数据库转换成JSON文件。

        :param req: 转换输入。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.convertCanDbToJson(req)

    def updateCanPdu(self, req: PduUpdate) -> Result:
        """
        更新CANPDU。

        :param req: 需要更新的PDU更新信息。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`
        """
        return self._canparser.updateCanPdu(req)

    # todo, the following are to be implemented...
    # # lin stack
    #
    # def reset(self):
    #     return self._linstack.reset()
    #
    # def setLinConfig(self, req):
    #     return self._linstack.setLinConfig(req)
    #
    # def setChannelConig(self, req):
    #     return self._linstack.setChannelConig(req)
    #
    # def startLinStack(self):
    #     return self._linstack.LinStack()
    #
    # def stopLinStack(self):
    #     return self._linstack.stopLinStack()
    #
    # def setMessageSimulation(self, req):
    #     return self._linstack.setMessageSimulation(req)
    #
    # def setHeaderSimulation(self, req):
    #     return self._linstack.setHeaderSimulation(req)
    #
    # def setMessageData(self, req):
    #     return self._linstack.setMessageData(req)
    #
    # def getLinStatus(self):
    #     return self._linstack.getLinStatus()
    #
    # def clearLinSubscribe(self):
    #     return self._linstack.clearLinSubscribe()
    #
    # def clearLinSend(self, req):
    #     return self._linstack.clearLinSend()
    #
    # def setLinCrcConfig(self, req):
    #     return self._linstack.clearLinSend(req)
    #
    # def clearLinCrcConfig(self, req):
    #     return self._linstack.clearLinCrcConfig(req)
    #
    # def getDeltaTime(self):
    #     return self._linstack.getDeltaTime()
    #
    # # # lin parser
    #
    # def addDbfile(self, req):
    #     return self._linparser.addDbfile(req)
    #
    # def setChannelConfig(self, req):
    #     return self._linparser.setChannelConfig(req)
    #
    # def setNodeSimulation(self, req):
    #     return self._linparser.setNodeSimulation(req)
    #
    # def setFrameSimulation(self, req):
    #     return self._linparser.setFrameSimulation(req)
    #
    # def setFrameData(self, req):
    #     return self._linparser.setFrameData(req)
    #
    # def SetSignalData(self, req):
    #     return self._linparser.SetSignalData(req)
    #
    # def clearCanParserSubscribe(self):
    #     return self._linparser.clearCanParserSubscribe()
    #
    # def clearDbfile(self):
    #     return self._linparser.clearDbfile()
    #
    # def getLinParserStatus(self):
    #     return self._linparser.getLinParserStatus()
    #
    # def getLdfJsonTree(self):
    #     return self._linparser.getLdfJsonTree()
    #
    # def convertLinDbToPy(self, req):
    #     return self._linparser.convertLinDbToPy(req)
    #
    # def convertLinDbToJson(self, req):
    #     return self._linparser.convertLinDbToJson(req)
    #
    # def setCrcConfig(self, req):
    #     return self._linparser.setCrcConfig(req)
    #
    # def clearCrcConfig(self, req):
    #     return self._linparser.clearCrcConfig(req)


if __name__ == "__main__":
    pass
