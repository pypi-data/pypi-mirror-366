# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/16 18:12
from typing import Protocol, Self, final
from PIL import Image


class Img(Protocol):
    base_img: Image
    width: int
    height: int
    img_type: str
    img_size_byte: int

    def get_img_type(self):
        """
        获取图片类型
        类型               ｜ Pillow mode ｜每像素位数 ｜颜色数｜特点
        monochrome1bit    ｜ “1”          ｜ 1-bit    ｜ 2（黑/白）          ｜仅黑色两色，最小存储
        monochrome8bit    ｜ “L”          ｜ 8-bit    ｜ 256 级灰度          ｜ 适用于黑白照片，医学影像
        colorClassic      ｜ “P"          ｜ 8-bit    ｜256 （基于调色板）    ｜ 经典8-bit颜色模式，如GIF
        color24bit        ｜ “RGB"        ｜ 24-bit   ｜ 16,777,216         ｜ 标准全彩色
        color32bit        ｜ “RGBA"       ｜ 32-bit   ｜16，777，216 + Alpha ｜ 带透明通道的全彩色
        :return:
        """
        pass

    def get_img_size(self) -> int:
        """
        返回单位字节
        由于暂不支持monochrome8bit,colorClassic, 只处理monochrome1bit，color24bit
        其他类型都转为color24bit计算大小
        dmsGraphicType 的值为“monochrome1bit”
            B = ((dmsGraphicWidth * dmsGraphicHeight) + 7)/8

        dmsGraphicType 的值为“monochrome8bit”
            B = (dmsGraphicWidth*dmsGraphicHeight)

        dmsGraphicType 的值为“colorClassic"
            B = (dmsGraphicWidth*dmsGraphicHeight)

        dmsGraphicType 的值为 'color24bit'
            B = (dmsGraphicWidth*dmsGraphicHeight)*3
        :return:
        """
        pass


    def get_bitmap_list(self, block_size: int) -> list:
        """
        图像的位图(八位字节倍数,不足八位补0，不足块大小补0)按块大小切割为list
        color24bit 1个像素点 对应3字节
        monochrome1bit  1个像素为1bit
        color24bit 不存在不足八位补0
        :param block_size:
        :return:
        """
        pass
