from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from zone.IDL.thrift.CanStackNode.ttypes import canMessage
from zone.IDL.thrift.CanParserNode import canParserNode
from zone.IDL.thrift.CanParserNode.constants import *
from zone.IDL.thrift.CommonNode.ttypes import *
from zone import BaseNodeData
from zone.utils.decorator import singleton


# @singleton
class CanParserClient(canParserNode.Iface):
    """class CanParserClient docstring"""

    def __init__(self) -> None:
        """constructor docstring"""
        transport = TSocket.TSocket(
            BaseNodeData.CAN_PARSER_NODE_IP, BaseNodeData.CAN_PARSER_NODE_PORT
        )
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = canParserNode.Client(protocol)
        # self.transport.open()

    def connect(self):
        try:
            print("canparser connecting...")
            self.transport.open()
            return result(result=0, reason="connected")
        except:
            self.transport.close()
            return result(result=1, reason="not connected")

    def disconnect(self):
        try:
            print("canparser disconnecting...")
            self.transport.close()
            return result(result=0, reason="disconnected")
        except:
            return result(result=1, reason="still connected")

    def checkAlive(self) -> result:
        """
        检查存活度

        :return: 执行结果

        :rtype: result
        """
        return self.client.checkAlive()

    def getStatus(self) -> result:
        """
        获取CAN协议栈状态，result中result为1时表示正在运行

        :return: 执行结果

        :rtype: result
        """
        return result(result=0, reason="canparser status unknown.")

    def setCrcRcConfig(self, config: pduCrcRcConfig) -> result:
        """
        设置CRC配置

        :param config: 需要设置的pdu的软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.setCrcRcConfig(config)

    def clearAllCrcRcConfig(self) -> result:
        """
        清除所有CRC配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearAllCrcRcConfig()

    def clearCrcRcConfig(self, config: pduCrcRcConfig) -> result:
        """
        清除CRC配置

        :param config: 需要设置的pdu的软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearCrcRcConfig(config)

    def sendCanFrameCyc(self, msg: canMessage) -> result:
        """
        发送CAN帧循环

        :param msg: can报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanFrameCyc(msg)

    def sendCanPduCyc(self, msg: pduMessage) -> result:
        """
        发送CAN PDU循环

        :param msg: PDU报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.send_sendCanPduCyc(msg)

    def sendCanPduCycList(self, msgs: pduMessages) -> result:
        """
        发送CAN PDU 循环列表

        :param msgs: 全部PDU报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanPduCycList(msgs)

    def sendCanPdu(self, msg: pduMessage) -> result:
        """
        发送CAN PDU

        :param msg: PDU报文通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanPdu(msg)

    def addDbFile(self, dbpath: dbPath) -> result:
        """
        添加数据库文件

        :param dbpath: 数据库路径

        :return: 执行结果
        :rtype: result
        """
        return self.client.addDbFile(dbpath)

    def setConfig(self, configs: dbConfigs) -> result:
        """
        设置配置

        :param configs: 多个数据库配置

        :return: 执行结果

        :rtype: result
        """
        return self.client.setConfig(configs)

    def getCanDbConfigs(self) -> dbConfigs:
        """
        获取CAN数据库配置

        :return: 数据库配置

        :rtype: dbConfigs
        """
        return self.client.getCanDbConfigs()

    def getCanDbPath(self) -> dbPath:
        """
        获取CAN数据库路径

        :return: 数据库路径

        :rtype: dbPath
        """
        return self.client.getCanDbPath()

    def subscribeMsg(self, info: subscribeInfo) -> result:
        """
        订阅消息

        :param info: 订阅信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.subscribeMsg(info)

    def unSubscribeMsg(self, info: subscribeInfo) -> result:
        """
        取消消息订阅

        :param info: 订阅信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.unSubscribeMsg(info)

    def getCanDbInfo(self) -> canDbInfo:
        """
        获取CAN数据库信息

        :return: CAN数据库信息

        :rtype: canDbInfo
        """
        return self.client.getCanDbInfo()

    def clear(self) -> result:
        """
        清理

        :return: 执行结果

        :rtype: result
        """
        return self.client.clear()

    def clearSubscribe(self) -> result:
        """
        清理订阅

        :return: 执行结果

        :rtype: result
        """
        return self.client.clearSubscribe()

    def encodePdu(self, req: iSignalIPduObj) -> iSignalIPduEncode:
        """
        编码PDU

        :param req: iSignalIPduObj

        :return: iSignalIPduEncode结构：{result, length, data数组}

        :rtype: iSignalIPduEncode
        """
        return self.client.encodePdu(req)

    def convertCanDbToPy(self, dbpath: convertInput) -> result:
        """
        将CAN数据库转换成python文件

        :param dbpath: CAN数据库源文件地址，绝对路径，字符串

        :return: 执行结果

        :rtype: result
        """
        return self.client.convertCanDbToPy(dbpath)

    def convertCanDbToJson(self, dbpath: convertInput) -> result:
        """
        将CAN数据库转换成JSON

        :param dbpath: CAN数据库源文件地址，绝对路径，字符串

        :return: 执行结果

        :rtype: result
        """
        return self.client.convertCanDbToJson(dbpath)

    def updateCanPdu(self, info: pduUpdate) -> result:
        """
        更新CAN PDU

        :param info: 更新pdu对象所在的软件通道信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.updateCanPdu(info)

    def AddCanDbFile(self, db_path: "str") -> "int":
        return self.client.addDbFile(
            dbPath(
                dbPath=db_path,
            )
        )


canparserclient = singleton(CanParserClient)()

if __name__ == "__main__":
    canParser_Client = CanParserClient()
    print(f"Client {canParser_Client} is made.")
