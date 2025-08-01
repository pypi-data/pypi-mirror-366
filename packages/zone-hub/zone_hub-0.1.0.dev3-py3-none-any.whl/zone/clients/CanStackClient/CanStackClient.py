from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from zone.IDL.thrift.CanStackNode import canStackNode
from zone.IDL.thrift.CanStackNode.constants import *
from zone.IDL.thrift.CommonNode.ttypes import *
from zone import BaseNodeData
from zone.utils.decorator import singleton


class CANStackClient(canStackNode.Iface):
    """定义一个CAN Stack的客户端实例"""

    def __init__(self) -> None:
        """初始化CAN Stack的客户端"""
        transport = TSocket.TSocket(
            BaseNodeData.CAN_STACK_NODE_IP, BaseNodeData.CAN_STACK_NODE_PORT
        )
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = canStackNode.Client(protocol)
        # self.transport.open()

    def connect(self):
        try:
            print("canstack connecting...")
            self.transport.open()
            return result(result=0, reason="connected")
        except:
            self.transport.close()
            return result(result=1, reason="not connected")

    def disconnect(self):
        try:
            print("canstack disconnecting...")
            self.transport.close()
            return result(result=0, reason="disconnected")
        except:
            return result(result=1, reason="still connected")

    def checkAlive(self) -> result:
        """
        检查活跃度

        :return: 执行结果

        :rtype: result
        """
        return self.client.checkAlive()

    def getVersion(self) -> version:
        """
        获取版本

        :return: 执行结果

        :rtype: version
        """
        return self.client.getVersion()

    def setConfigs(self, configs: canChannelConfigs) -> result:
        """
        配置can通道信息

        :param configs: can通道配置信息（多个）

        :return: 执行结果

        :rtype: result
        """
        return self.client.setConfigs(configs)

    def start(self) -> result:
        return self.startCanStack()

    def stop(self) -> result:
        return self.stopCanStack()

    def startCanStack(self) -> result:
        """
        启动CAN协议栈

        :return: 执行结果

        :rtype: result
        """
        return self.client.startCanStack()

    def stopCanStack(self) -> result:
        """
        停止CAN协议栈

        :return: 执行结果

        :rtype: result
        """
        return self.client.stopCanStack()

    def clearSend(self) -> result:
        """
        清除所有发送任务

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearSend()

    def setCrcRcConfig(self, config: frameCrcRcConfig) -> result:
        """
        设置特定Crc/Rc信息

        :param config: 软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.setCrcRcConfig(config)

    def clearCrcRcConfig(self, config: frameCrcRcConfig) -> result:
        """
        清除特定Crc/Rc信息

        :param config: 软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearCrcRcConfig(config)

    def clearAllCrcRcConfig(self) -> result:
        """
        清除所有Crc/Rc信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearAllCrcRcConfig()

    def sendCanMessageCyc(self, msg: canMessage) -> result:
        """
        发送周期CAN报文

        :param msg: can报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanMessageCyc(msg)

    def sendCanMessage(self, msg: canMessage) -> result:
        """
        发送单帧CAN报文

        :param msg: can报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanMessage(msg)

    def sendCanMessages(self, msgs: canMessages, stmin: int) -> result:
        """
        诊断发送连续帧使用

        :param msgs: 多条can报文集合

        :param stmin: 单位毫秒

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanMessages(msgs, stmin)

    def getStatus(self) -> result:
        """
        获取CAN协议栈状态，result中result为1时表示正在运行

        :return: 执行结果

        :rtype: result
        """
        return self.client.getStackStatus()

    def stopChannelSendCyc(self, req: channel) -> result:
        """
        停止某条软件通道上所有发送任务

        :param req: can通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.stopChannelSendCyc(req)

    def sendCan(self, msg: canMessage) -> result:
        """
        发送CAN消息

        :param msg: can报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCan(msg)

    def getChannelBusloadCurrent(self, req: channel) -> busload:
        """
        获取
        :param req: can通道信息

        :return: CAN通道负载

        :rtype: busload
        """
        return self.client.getChannelBusloadCurrent(req)

    def getChannelBusloadMax(self, req: channel) -> busload:
        """

        :param req: can通道信息

        :return: CAN通道负载

        :rtype: busload
        """
        return self.client.getChannelBusloadMax(req)

    def getChannelBusloadAvg(self, req: channel) -> busload:
        """

        :param req: can通道信息

        :return: CAN通道负载

        :rtype: busload
        """
        return self.client.getChannelBusloadAvg(req)

    def getChannelErrorFrameTotal(self, req: channel) -> errorFrameTotal:
        """

        :param req: can通道信息

        :return: 所有can通道错误帧

        :rtype: errorFrameTotal
        """
        return self.client.getChannelErrorFrameTotal(req)


canstackclient = singleton(CANStackClient)()

if __name__ == "__main__":
    canStack_Client = CANStackClient()
    print(f"Client {canStack_Client} is made.")
