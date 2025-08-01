from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from zone.IDL.thrift.ConfigNode.constants import *
from zone.IDL.thrift.SomeIpNode.ttypes import *
from zone.IDL.thrift.CommonNode.ttypes import *
from zone.IDL.thrift.ConfigNode import configNode
from zone import BaseNodeData


class ConfigClient(configNode.Iface):
    """
    Config 的客户端
    """

    def __init__(self) -> None:
        """
        ConfigClient 的构造函数
        """
        transport = TSocket.TSocket(
            BaseNodeData.CONFIG_NODE_IP, BaseNodeData.CONFIG_NODE_PORT
        )
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = configNode.Client(protocol)
        transport.open()

    def getHardwareInfo(self, type_: hardwareType) -> hardwareInfos:
        """
        获取硬件信息

        :return: 硬件信息列表

        :rtype: hardwareInfos，列表
        """
        return self.client.getHardwareInfo(type_)

    def sendCanArxml(self, dbpath: dbPath) -> canCluster:
        """
        发送CAN Arxml

        :param dbpath: 数据库文件路径

        :return: 解析完arxml后返回所有通道名字信息

        :rtype: canCluster，列表
        """
        return self.client.sendCanArxml(dbpath)

    def sendCanConfig(self, config: canConfigInfo) -> result:
        """
        发送CAN配置

        :param config: 多条CAN通道列表

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendCanConfig(config)

    def sendLinConfig(self, configs: linChannelConfigs) -> result:
        """
        发送LIN配置

        :param configs: 多条LIN配置信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendLinConfig(configs)

    def sendEthConfig(self, config: someipStackConfig) -> result:
        """
        发送ETH配置

        :param config: SomeIP配置信息

        :return: 执行结果

        :rtype: result
        """
        return self.client.sendEthConfig(config)


if __name__ == "__main__":
    config_Client = ConfigClient()
    print(f"Client {config_Client} is made.")
