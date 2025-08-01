from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from zone.IDL.thrift.LinStackNode.ttypes import *
from zone.IDL.thrift.LinStackNode import linStackNode
from zone.IDL.thrift.CommonNode.ttypes import *
from zone import BaseNodeData
from zone.utils import singleton


class LinStackClient(linStackNode.Iface):
    """class LinStackNodeClient docstring"""

    def __init__(self) -> None:
        """constructor docstring"""
        transport = TSocket.TSocket(
            BaseNodeData.LIN_STACK_NODE_IP, BaseNodeData.LIN_STACK_NODE_PORT
        )
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = linStackNode.Client(protocol)
        # self.transport.open()

    def connect(self):
        try:
            print("linstack connecting...")
            self.transport.open()
            return result(result=0, reason="connected")
        except:
            self.transport.close()
            return result(result=1, reason="not connected")

    def disconnect(self):
        try:
            print("linstack disconnecting...")
            self.transport.close()
            return result(result=0, reason="disconnected")
        except:
            return result(result=1, reason="still connected")

    def reset(self) -> result:
        return self.client.reset()

    def setConfig(self, req: genericString) -> result:
        """
        配置lin通道信息

        :param req

        :return: 执行结果

        :rtype: result
        """
        return self.client.setConfig(req)

    def setChannelConig(self, req: linChannelConfigs) -> result:
        """
        配置lin通道信息

        :param req: lin通道配置信息（多个）

        :return: 执行结果

        :rtype: result
        """
        return self.client.setChannelConig(req)

    def start(self) -> result:
        return self.startLinStack()

    def stop(self) -> result:
        return self.stopLinStack()

    def startLinStack(self) -> result:
        """
        启动LIN协议栈

        :return: 执行结果

        :rtype: result
        """
        return self.client.startLinStack()

    def stopLinStack(self) -> result:
        """
        停止LIN协议栈

        :return: 执行结果

        :rtype: result
        """
        return self.client.stopLinStack()

    def setMessageSimulation(self, req: linMessageConfig) -> result:
        return self.client.setMessageSimulation(req)

    def setHeaderSimulation(self, req: linHeaderConfig) -> result:
        return self.client.setHeaderSimulation(req)

    def setMessageData(self, req: linMessageDataT) -> result:
        return self.client.setMessageData(req)

    def getStatus(self) -> linStackStatus:
        return self.client.getStatus()

    def checkAlive(self) -> result:
        """ """
        return result(result=0, reason="lin stack alive unknown")

    def clearSubscribe(self) -> result:
        """
        取消订阅

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearSubscribe()

    def clearSend(self, req: genericInt) -> result:
        return self.client.clearSend(req)

    def setLinCrcConfig(self, req: linCrcConfig) -> result:
        """
        设置CRC配置

        :param config: 需要设置的LIN CRC的软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.setLinCrcConfig(req)

    def clearLinCrcConfig(self, req: linCrcConfig) -> result:
        """
        清除所有CRC配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearLinCrcConfig(req)

    def getDeltaTime(self) -> genericInt64:
        return self.client.getDeltaTime()


linstackclient = singleton(LinStackClient)()


if __name__ == "__main__":
    linStack_Client = LinStackClient()
    print(f"Client {linStack_Client} is made.")
