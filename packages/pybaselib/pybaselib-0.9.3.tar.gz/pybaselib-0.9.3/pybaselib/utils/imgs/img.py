# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/16 18:38
import sys

from pybaselib.interfaces.imgs.img import Img
from PIL import Image, ImageDraw
from pybaselib.utils import IntType


class ImgFactory:
    @staticmethod
    def get_size(width, height, img_type) -> int:
        if img_type == "monochrome1bit":
            pixels = width * height
            return IntType.custom_round_division(pixels, 8)
        else:
            return (width * height) * 3

    def __init__(self, img_path: str) -> None:
        self.img_path = img_path
        self.base_img = Image.open(img_path)
        # self.set_image_size()
        self.width, self.height = self.base_img.size
        self.img_type = self.get_img_type()


    def get_img_type(self):
        img_type = self.base_img.mode
        if img_type == "1":
            return "monochrome1bit"
        elif img_type == "L":
            return "monochrome8bit"
        elif img_type == "P":
            return "colorClassic"
        elif img_type == "RGB":
            return "color24bit"
        elif img_type == "RGBA":
            return "color32bit"
        else:
            return img_type

    def update_img_type(self):
        self.img_type = self.get_img_type()

    def get_instance(self):
        if self.img_type == "monochrome1bit":
            from pybaselib.utils.imgs.one_bit_img import OneBitImg
            return OneBitImg(self.img_path)
        # elif self.img_type == "color24bit":
        #     from pybaselib.utils.imgs.rgb_img import RGBImg
        #     return RGBImg(self.img_path)
        else:
            from pybaselib.utils.imgs.rgb_img import RGBImg
            return RGBImg(self.img_path)

    def get_graphic_infos(self):
        print(self.width, self.height, self.img_type, self.img_size_byte)
        return self.width, self.height, self.img_type, self.img_size_byte

    # def get_img_to_hex(self, graphic_type):
    #     hex_data = None
    #     if graphic_type == "monochrome1bit":
    #         # 获取图片的二进制数据
    #         img_data = self.base_img.tobytes()
    #         # 以十六进制格式输出  00代表全黑 FF代表全白
    #         hex_data = img_data.hex()
    #     return hex_data

    def split_hex_data(self, hex_data, chunk_size=1024):
        """将十六进制字符串按 1KB (1024字节 = 2048 hex字符) 进行分割"""
        hex_chunk_size = chunk_size * 2  # 1 字节 = 2 hex 字符
        chunks = [hex_data[i:i + hex_chunk_size] for i in range(0, len(hex_data), hex_chunk_size)]

        # 如果最后一块数据不足 1KB，则补 00
        if len(chunks[-1]) < hex_chunk_size:
            chunks[-1] = chunks[-1].ljust(hex_chunk_size, '0')

        return chunks


if __name__ == '__main__':
    # img_path = '/Users/maoyongfan/Downloads/2.bmp'
    # img_path = '/Users/maoyongfan/Downloads/1.bmp'
    img_path = '/Users/maoyongfan/Downloads/AAa.jpg'
    # img_path = '/Users/maoyongfan/Downloads/xstudiopro_与软件通信介绍.png'
    # img_path = '/Users/maoyongfan/Downloads/4.png'
    i = ImgFactory(img_path)
    # 生成 100x100 的黑白 1-bit 图片
    # i.create_monochrome_1bit_image(100, 100, img_path)
    # i.create_monochrome_1bit_image_2(img_path)
    # i.hex_to_1bit_image("000C000007000001E03FFFF80001E0000700000C00", 24, 7, img_path)
    # i.create_monochrome_image("84926308C248A170", 10, 6, img_path)
    print(i.width, i.height, i.get_img_type())
    # i.get_pixels()
    # print(i.get_bitmap_list(i.get_img_type(), 1024))
    # bit_data = i.one_bit_image_to_bits()
    # print("Bit Data:", bit_data)
    # print("Length:", len(bit_data), "bits ({} bytes)".format(len(bit_data) // 8))
    # hex_data = IntType.bits_to_hex(bit_data)
    # print("Hex Data:", hex_data)
    # print(i.split_hex_data(hex_data))
    bitmap = i.get_instance().get_bitmap_list()
    # print(bitmap)
    print(len(bitmap))
