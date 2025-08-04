# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/17 13:04
from pybaselib.interfaces.imgs.img import Img
from pybaselib.utils.imgs.img import ImgFactory
from pybaselib.utils import IntType


class OneBitImg(ImgFactory, Img):
    def __init__(self, img_path: str):
        super().__init__(img_path)
        self.img_size_byte = self.get_img_size()

    @property
    def bitmap_hex(self) -> str:
        return IntType.bits_to_hex(self.one_bit_image_to_bits())

    def get_img_size(self):
        pixels = self.width * self.height
        return IntType.custom_round_division(pixels, 8)

    def one_bit_image_to_bits(self):
        """将 1-bit 单色图像转换为比特流，不足8位补0 1bit对应1像素"""
        pixels = self.base_img.load()

        bit_string = ""

        for y in range(self.height):
            for x in range(self.width):
                bit_string += '1' if pixels[x, y] == 255 else '0'  # 白色(255) -> '1'，黑色(0) -> '0'

        # 补齐到8位对齐
        padding_length = (8 - len(bit_string) % 8) % 8
        bit_string += '0' * padding_length  # 末尾补0
        return bit_string

    def get_bitmap_list(self, block_size=1024):
        # bit_data = self.one_bit_image_to_bits()
        # hex_data = IntType.bits_to_hex(bit_data)
        # return self.split_hex_data(hex_data, block_size)
        return self.split_hex_data(self.bitmap_hex, block_size)
