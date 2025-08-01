from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from zone.IDL.thrift.LinParserNode.ttypes import *
from zone.IDL.thrift.CanParserNode.ttypes import *
from zone.IDL.thrift.LinParserNode import linParserNode
from zone.IDL.thrift.LinParserNode.constants import *
from zone.IDL.thrift.CommonNode.ttypes import *
from zone import BaseNodeData
from zone.utils import singleton


class LinParserClient(linParserNode.Iface):
    """class LinParserClient docstring"""

    def __init__(self) -> None:
        """constructor docstring"""
        transport = TSocket.TSocket(
            BaseNodeData.LIN_PARSER_NODE_IP, BaseNodeData.LIN_PARSER_NODE_PORT
        )
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = linParserNode.Client(protocol)
        # self.transport.open()

    def connect(self):
        try:
            print("linparser connecting...")
            self.transport.open()
            return result(result=0, reason="connected")
        except:
            self.transport.close()
            return result(result=1, reason="not connected")

    def disconnect(self):
        try:
            print("linparser disconnecting...")
            self.transport.close()
            return result(result=0, reason="disconnected")
        except:
            return result(result=1, reason="still connected")

    def addDbfile(self, dbpath: dbPath) -> result:
        """
        添加数据库文件

        :param dbpath: 数据库路径

        :return: 执行结果

        :rtype: result
        """
        return self.client.addDbfile(dbpath)

    def setChannelConfig(self, configs: linChannelConfigs) -> result:
        """
        配置lin通道信息

        :param configs: 多个数据库配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.setChannelConfig(configs)

    def setNodeSimulation(self, config: linNodeConfig) -> result:
        """
        XXX

        :param config: LIN节点通道配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.setNodeSimulation(config)

    def setFrameSimulation(self, config: linFrameConfig) -> result:
        """
        XXX

        :param config:

        :return: 执行结果

        :rtype: result
        """
        return self.client.setFrameSimulation(config)

    def setFrameData(self, data: linFrameData) -> result:
        """
        XXX

        :param data: linFrameData

        :return: 执行结果

        :rtype: result
        """
        return self.client.setFrameData(data)

    def SetSignalData(self, signal: linSignalData) -> result:
        """
        设置lin信号

        :param signal: linSignalData

        :return: 执行结果

        :rtype: result
        """
        return self.client.SetSignalData(signal)

    def clearSubscribe(self) -> result:
        """
        取消订阅

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearSubscribe()

    def clearDbfile(self) -> result:
        """
        清空lin数据库

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearDbfile()

    def getStatus(self) -> linParserStatus:
        """
        获取LIN解析状态，result中result为1时表示正在运行

        :return: 执行结果

        :rtype: result
        """
        return self.client.getStatus()

    def checkAlive(self) -> result:
        """
        """
        return result(result=0, reason="lin parser alive unknown")


    def getLdfJsonTree(self) -> linLdfJson:
        """
        获取ldf文件解析数据
        """
        return self.client.getLdfJsonTree()

    def convertLinDbToPy(self, req: convertInput) -> result:
        """
        将LIN数据库转换成python文件

        :param: LIN数据库

        :return: 执行结果

        :rtype: result
        """
        return self.client.convertLinDbToPy(req)

    def convertLinDbToJson(self, req: convertInput) -> result:
        """
        将LIN数据库转换成JSON

        :param dbpath: LIN数据库源文件地址，绝对路径，字符串

        :return: 执行结果

        :rtype: result
        """
        return self.client.convertLinDbToJson(req)

    def setCrcConfig(self, config: linCrcConfigParser) -> result:
        """
        设置CRC配置

        :param config: 需要设置的LIN Frame的软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.setCrcConfig(config)

    def clearCrcConfig(self, req: linCrcConfigParser) -> result:
        """
        清除所有CRC配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearCrcConfig(req)


linparserclient = singleton(LinParserClient)()

if __name__ == "__main__":
    linParser_Client = LinParserClient()
    print(f"Client {linParser_Client} is made.")
