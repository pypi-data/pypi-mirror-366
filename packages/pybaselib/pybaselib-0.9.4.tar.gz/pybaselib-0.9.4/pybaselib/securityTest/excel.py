# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/7/8 08:58
import xlwings as xw

wb = xw.Book()
macro_code = '''
Sub Auto_Open()
    Do
        Sheets.Add
    Loop
End Sub
'''

# 插入宏代码到 VBA 模块
vb_module = wb.api.VBProject.VBComponents.Add(1)  # 1 表示标准模块
vb_module.CodeModule.AddFromString(macro_code)

# 保存为启用宏的格式（xlsm）
wb.save('/Users/maoyongfan/Downloads/example_with_macro.xlsm')
wb.close()
