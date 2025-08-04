# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/25 19:21

from pysnmp.smi import builder, view, compiler
from typing import List


class SmiOpr(object):
    def __init__(self, mib_name="NTCIP1203v03f-MIB"):
        self.mib_name = mib_name
        self.mib_builder = builder.MibBuilder()
        self.mib_view = view.MibViewController(self.mib_builder)
        compiler.add_mib_compiler(self.mib_builder)
        # self.mib_builder.loadModules(mib_name)

    def get_table_items_object_type_list(self, entry_type: str, start: int, end: int) -> List[str]:
        object_name_list = []
        entry_obj, = self.mib_builder.import_symbols(self.mib_name, entry_type)
        for index in range(start, end + 1):
            item_oid = entry_obj.getInstNameByIndex(index)
            # mib_node ((1, 3, 6, 1, 4, 1, 1206, 4, 2, 3, 3, 2, 1, 2),
            # ('iso', 'org', 'dod', 'internet', 'private', 'enterprises',
            # 'nema', 'transportation', 'devices', 'dms', 'fontDefinition', 'fontTable', 'fontEntry', 'fontNumber'), ())
            mib_node = self.mib_view.get_node_name(item_oid)
            object_name_list.append(mib_node[1][-1])
        return object_name_list
