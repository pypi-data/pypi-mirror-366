# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/18 19:46

from pysmi.reader.localfile import FileReader
from pysmi.writer.localfile import FileWriter
from pysmi.parser.smi import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.compiler import MibCompiler
from pysmi.searcher.stub import StubSearcher
from pysmi.searcher.pypackage import PyPackageSearcher


def mib_covert_python_obj(input_mib_dir, output_py_dir, search_dir, mib_name):
    # 初始化编译器组件
    reader = FileReader(input_mib_dir)  # 读取 MIB 文件
    writer = FileWriter(output_py_dir)  # 输出编译后的 Python 文件
    parser = SmiV2Parser()  # 使用 SMIv2 解析器
    codegen = PySnmpCodeGen()  # 使用 PySNMP 格式代码生成器
    compiler = MibCompiler(parser, codegen, writer)

    # 添加基本 MIB 支持
    compiler.add_searchers(StubSearcher(*PySnmpCodeGen.baseMibs))

    # 添加默认的 MIB 路径
    compiler.add_searchers(PyPackageSearcher(search_dir))

    # 添加 MIB 文件路径
    compiler.add_sources(reader)

    # 编译指定的 MIB 文件（可以是多个文件）
    compiler.compile(mib_name)  # 替换为你要编译的 MIB 文件名


if __name__ == '__main__':
    mib_covert_python_obj("/Users/maoyongfan/sansi/ntcip/mib",
                          "/Users/maoyongfan/sansi/ntcip/compiled_mibs",
                          '/Users/maoyongfan/.pysnmp/mibs',
                          "NTCIP1203v03f-MIB")
