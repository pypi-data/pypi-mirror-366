# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/17 13:28
from pybaselib.interfaces.imgs.img import Img
from pybaselib.utils.imgs.img import ImgFactory
from pybaselib.utils import IntType


class RGBImg(ImgFactory, Img):
    def __init__(self, img_path: str):
        super().__init__(img_path)
        self.img_size_byte = self.get_img_size()

    @property
    def bitmap_hex(self) -> str:
        return self.rgb_to_hex()

    def get_img_size(self):
        return (self.width * self.height) * 3

    def rgb_to_hex(self):
        if self.img_type != "color24bit":
            self.base_img = self.base_img.convert("RGB")
            self.update_img_type()
        rgb_pixels = list(self.base_img.getdata())
        hex_pixels = []
        for r, g, b in rgb_pixels:
            hex_pixel = f"{b:02x}{g:02x}{r:02x}"  # 将每个颜色值转换为两位十六进制
            hex_pixels.append(hex_pixel)

        # 将所有像素的十六进制表示合并为一个字符串
        hex_data = ''.join(hex_pixels)

        return hex_data

    def rgb_to_hex_n(self):
        """
        按行扫描
        :return:
        """
        hex_data = []
        for y in range(self.height):  # 遍历行（从上到下）
            for x in range(self.width):  # 遍历列（从左到右）
                r, g, b = self.base_img.getpixel((x, y))
                hex_data.append(f"{b:02X}{g:02X}{r:02X}")  # 格式化为两位 16 进制数

        # 拼接并输出十六进制数据
        hex_string = "".join(hex_data)
        return hex_string

    def get_bitmap_list(self, block_size=1024):
        # hex_data = self.rgb_to_hex()
        # return self.split_hex_data(hex_data, block_size)
        return self.split_hex_data(self.bitmap_hex, block_size)
