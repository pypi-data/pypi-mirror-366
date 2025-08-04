# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/9 23:53
import asyncio
import logging
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi import builder, view, compiler, rfc1902
from pybaselib.utils import BugException


class SNMPManager:
    def __init__(self, ipaddr, central_port=161, local_port=161, community="public", mib_name="NTCIP1203v03f-MIB"):
        # self.snmpEngine = SnmpEngine()
        self.ipaddr = ipaddr
        self.port = central_port
        self.community = community
        self.mib_name = mib_name
        self.local_port = local_port
        self.central_port = central_port

    def switch_to_local(self, local_port=None):
        if local_port is None:
            self.port = self.local_port
        else:
            self.port = local_port

    def switch_to_central(self):
        self.port = self.central_port

    def set_community(self, community):
        self.community = community

    def deal_value(self, oid, value, prettyPrint, request_type):
        # print(" = ".join([x.prettyPrint() for x in (oid, value)]))
        logging.info(f"  {request_type} {oid.prettyPrint()} = {value.prettyPrint()}")
        logging.info(f"类型为：{type(value).__name__}")

        expect_rule = value.subtypeSpec
        if len(expect_rule) != 0:   # 由于expect_rule长度可能为0，增加下面代码
            sub_expect_rule = expect_rule[-1]
        else:
            sub_expect_rule = expect_rule

        try:
            sub_expect_rule(value)
        except Exception as e:  # ValueConstraintError
            raiseBug = True
            import re
            match = re.search(r"::([^\.]+)\.", oid.prettyPrint())
            if match:
                if match.group(1) == "dmsGraphicTransparentColor" and value.prettyPrint() == "":
                    raiseBug = False
            if raiseBug:
                raise BugException(
                    f"{oid.prettyPrint()}返回值不符合预期范围||{oid.prettyPrint()}返回值不符合预期范围|返回值的范围为{sub_expect_rule},实际却为{value.prettyPrint()}||P1")

        if prettyPrint:  # 把枚举数字转为可理解字符串
            # 多处理mib情况
            if isinstance(value, OctetString):
                return value.prettyPrint().replace("0x", "")
            try:
                # 处理多次mib请求时,把返回int的值也prettyPrint()为string了
                tmp = int(value.prettyPrint())
                return tmp
            except Exception as e:
                return value.prettyPrint()
        elif isinstance(value, Integer32) or isinstance(value, Counter32) \
                or isinstance(value, Counter64) or isinstance(value, Integer):
            return int(value)
        elif isinstance(value, OctetString):
            return value.prettyPrint().replace("0x", "")
        else:
            logging.info('else')
            return value.prettyPrint()

    def deal_error(self, errorIndication, errorStatus, errorIndex, varBinds):
        if errorIndication:
            raise Exception("snmp 响应发生错误:", errorIndication)
        elif errorStatus:
            # print(
            #     f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
            # )
            if varBinds:
                raise BugException("%s at %s" % (errorStatus.prettyPrint(),
                                                 errorIndex and varBinds[int(errorIndex) - 1][0] or "?",))
            else:
                raise Exception("%s at %s" % (errorStatus.prettyPrint(), str(varBinds)))
        else:
            pass

    def deal_mib_name(self, mib_name):
        if self.mib_name is None:
            return mib_name
        else:
            return self.mib_name

    def deal_set_object_type(self, varBinds, mib_name, check_value=False):
        objectTypeList = []
        for mib, value in varBinds:
            if isinstance(value, int):
                value = Integer32(value)
            if isinstance(value, str):
                if mib[0] in ["dmsActivateMessage", "dmsGraphicTransparentColor", "dmsGraphicBlockBitmap",
                              "characterBitmap", "defaultBackgroundRGB", "defaultForegroundRGB", "dmsResetMessage",
                              "dmsShortPowerRecoveryMessage", "dmsCommunicationsLossMessage", "dmsEndDurationMessage"]:
                    value = OctetString(hexValue=value)
                else:
                    value = OctetString(value)

            if check_value:
                from pysnmp.smi import builder, view, compiler
                mibBuilder = builder.MibBuilder()
                mibViewController = view.MibViewController(mibBuilder)
                compiler.add_mib_compiler(
                    mibBuilder,
                    sources=["file:///usr/share/snmp/mibs"],
                )
                mibBuilder.load_modules("NTCIP1203v03f-MIB")

                if isinstance(mib, tuple):
                    mib_obj = ObjectType(
                        ObjectIdentity(*((mib_name,) + mib)), value
                    ).resolve_with_mib(mibViewController)
                else:
                    mib_obj = ObjectType(
                        ObjectIdentity(*([mib_name, ] + mib)), value
                    ).resolve_with_mib(mibViewController)

                expect_rule = mib_obj[1].subtypeSpec
                sub_expect_rule = expect_rule[-1]
                try:
                    sub_expect_rule(mib_obj[1])
                except Exception as e:  # ValueConstraintError
                    raise Exception(f"返回值的范围为{sub_expect_rule},实际却为{mib_obj[1]}")
            else:
                if isinstance(mib, tuple):
                    objectTypeList.append(ObjectType(
                        ObjectIdentity(*((mib_name,) + mib)), value
                    ))
                else:
                    objectTypeList.append(ObjectType(
                        ObjectIdentity(*([mib_name, ] + mib)), value
                    ))
        return objectTypeList

    def deal_object_type(self, varBinds, mib_name):
        objectTypeList = []
        for mib in varBinds:  # mib 为元组或列表
            if isinstance(mib, tuple):
                objectTypeList.append(
                    ObjectType(
                        ObjectIdentity(*((mib_name,) + mib))
                    )
                )
            else:
                objectTypeList.append(ObjectType(
                    ObjectIdentity(
                        ObjectIdentity(*([mib_name, ] + mib))
                    )
                ))
        return objectTypeList

    async def get_mib(self, varBinds, mib_name="NTCIP1203v03f-MIB",
                      prettyPrint=False):
        mib_name = self.deal_mib_name(mib_name)
        objectTypeList = self.deal_object_type(varBinds, mib_name)

        resultList = []
        iterator = get_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port), timeout=5),
            ContextData(),
            *objectTypeList
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint, "get_request")
            resultList.append(result)

        if len(objectTypeList) == 1:
            return resultList[0]
        else:
            logging.info(resultList)
            return resultList

    async def set_mib(self, varBinds, mib_name="NTCIP1203v03f-MIB", prettyPrint=False, check_value=False):
        resultList = []
        mib_name = self.deal_mib_name(mib_name)
        objectTypeList = self.deal_set_object_type(varBinds, mib_name, check_value=check_value)
        iterator = set_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port), timeout=10),
            ContextData(),
            *objectTypeList
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint, "set-request")
            resultList.append(result)
        logging.info(resultList)
        return resultList

    async def get_oid(self, varBinds, mib_name="NTCIP1203v03f-MIB", prettyPrint=False):
        """
        多个oid为一组请求，按oid方式
        :param varBinds:
        :param mib_name:
        :param prettyPrint:
        :return:
        """
        resultList = []
        iterator = get_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            *[ObjectType(ObjectIdentity(oid)) for oid in varBinds]
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint, "get-request")
            resultList.append(result)

        if len(resultList) == 1:
            return resultList[0]
        else:
            logging.info(resultList)
            return resultList

    async def set_oid(self, oid, value, prettyPrint=False):
        if isinstance(value, int):
            value = Integer32(value)
        if isinstance(value, str):
            value = OctetString(value)
        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)
        )
        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint, "set-request")
            logging.info(result)
            return result

    async def next_cmd(self, object_type, index=0, mib_name="NTCIP1203v03f-MIB", prettyPrint=False, get_oid=None,
                       response="value"):
        mib_name = self.deal_mib_name(mib_name)
        if get_oid is None:
            from pysnmp.smi import builder, view, compiler
            mibBuilder = builder.MibBuilder()
            mibViewController = view.MibViewController(mibBuilder)
            obj = ObjectType(ObjectIdentity(mib_name, object_type, index))
            get_oid = (obj.resolve_with_mib(mibViewController))[0].get_oid()
            logging.info(f"get_next请求oid为: {get_oid}")
        else:
            obj = ObjectType(ObjectIdentity(get_oid))
        errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            obj,
            # lexicographicMode=True,
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            logging.info(f"get_next返回oid为: {oid}")
            print(f"get_next返回oid为: {oid}")
            result = self.deal_value(oid, value, prettyPrint, "next-request")
            logging.info(result)
            if response == "oid":
                return get_oid, oid
            else:
                return result

    async def bulk_cmd(self, nonRepeaters, maxRepetitions, varBinds, prettyPrint=False):
        resultList = []
        objectTypeList = self.deal_object_type(varBinds, self.mib_name)

        errorIndication, errorStatus, errorIndex, varBindTable = await bulk_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            nonRepeaters, maxRepetitions,
            *objectTypeList
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBindTable)

        for oid, value in varBindTable:
            result = self.deal_value(oid, value, prettyPrint, 'bulk-request')
            resultList.append(result)

        logging.info(resultList)
        return resultList


if __name__ == "__main__":
    snmpObject = SNMPManager("192.168.1.138")  # 192.168.1.105 192.168.1.120
    asyncio.run(snmpObject.next_cmd(None))
    # asyncio.run(snmpObject.next_cmd(None, oid="1.3.6.1.4.1.1206.4.2.3.1.1.0"))
    # asyncio.run(snmpObject.get_cmd_many([
    #     ObjectType(ObjectIdentity("1.3.6.1.4.1.1206.4.2.3.3.1.0")),
    #     ObjectType(ObjectIdentity("1.3.6.1.4.1.1206.4.2.3.6.8.0"))]))

    # a = [("dmsMaxChangeableMsg", 0), ("dmsFreeChangeableMemory", 0)]
    # result = asyncio.run(snmpObject.get_cmd_many_mib(a))

    # asyncio.run(snmpObject.get_cmd_single_mib("dmsMessageStatus", 3, 1))
    # asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.3.1.0"))
    # 字体名称
    # print("返回",asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.3.2.1.3.3")))
    # asyncio.run(snmpObject.set_cmd("1.3.6.1.4.1.1206.4.2.3.6.1.0",4))
    # result = asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.6.1.0"))
    # print("result: ", result)

    # from pysnmp.hlapi import *
    #
    # # SNMP请求的目标设备和社区字符串
    # target = '192.168.1.120'  # 目标设备的IP地址
    # community = 'public'  # 社区字符串
    # oids = ['1.3.6.1.4.1.1206.4.2.3.3.1.0', '1.3.6.1.4.1.1206.4.2.3.6.8.0']  # 你需要请求的OID列表
    # mib_name = "NTCIP1203v03f-MIB"
    #
    # async def snmp_get():
    #     # 创建UDP传输目标对象，并调用 .create() 进行初始化
    #
    #
    #     # 创建SNMP GET请求
    #     result = get_cmd(
    #         SnmpEngine(),
    #         CommunityData(community,mpModel=0),
    #         await UdpTransportTarget.create((target, 161)),  # 使用已创建的传输目标对象
    #         ContextData(),
    #         # *[ObjectType(ObjectIdentity(oid)) for oid in oids]  # 确保 ObjectType 完全初始化
    #         *(
    #         ObjectType(ObjectIdentity(mib_name, "dmsMaxChangeableMsg",0)),
    #         ObjectType(ObjectIdentity(mib_name, "dmsFreeChangeableMemory",0))
    #         )
    #     )
    #
    #     # 发送请求并处理响应
    #     errorIndication, errorStatus, errorIndex, varBinds = await result
    #
    #     if errorIndication:
    #         print(f"Error: {errorIndication}")
    #     else:
    #         if errorStatus:
    #             print(f"Error: {errorStatus.prettyPrint()}")
    #         else:
    #             for varBind in varBinds:
    #                 print(f'{varBind[0]} = {varBind[1]}')

    # # 启动异步事件循环
    # asyncio.run(snmp_get())
