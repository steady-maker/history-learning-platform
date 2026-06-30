import base64
import io
import json
import logging
import math
import os
import traceback
from PIL import Image, ImageDraw, ImageShow
import random

from django_redis import get_redis_connection
from rest_framework.views import APIView

from history_web_backend import settings
from utils.exception import BizException

logger = logging.getLogger('error')

# 随机生成滑块验证码
class SliderCaptcha:
    def __init__(self):
        self.bg_color = (255, 255, 255)  # 背景色
        self.slider_color = (125, 125, 125)  # 滑块颜色
        self.img_size = (310, 155)  # 图片尺寸

        self.block_size = (45, 45)  # 滑块尺寸
        self.blockX = 0  # 滑块的横坐标
        self.blockY = 0  # 滑块的纵坐标
        self.block_radius = 5  # 滑块凹凸半径
        self.block_position = self.generate_block_position()  # 生成滑块位置

    def generate_block_position(self):
        block_x = random.randint(0, self.img_size[0] - self.block_size[0])  # 随机生成滑块起始横坐标
        block_y = random.randint(0, self.img_size[1] - self.block_size[1])  # 随机生成滑块起始纵坐标
        return block_x, block_y

    @staticmethod
    def get_random_resized_image(folder_path, image_start, image_end, width, height):
        """
        从指定文件夹随机选择一张图片，并调整到指定尺寸。

        :param folder_path: 图片所在文件夹路径
        :param image_start: 图片文件名起始序号（整数）
        :param image_end: 图片文件名结束序号（整数）
        :param width: 目标宽度
        :param height: 目标高度
        :return: 调整尺寸后的 PIL Image 对象
        """
        # 随机选择图片序号
        image_index = random.randint(image_start, image_end)
        image_path = os.path.join(folder_path, f"{image_index}.jpg")

        # 打开并调整图片尺寸
        image = Image.open(image_path)
        resized_image = image.resize((width, height))

        return resized_image


    # 抠图，并生成阻塞块
    def cut_by_template(self,canvas_image, block_image, block_width, block_height, block_radius, block_x, block_y):
        water_image = Image.new("RGBA", (block_width, block_height), (0, 0, 0, 0))
        # 阻滑块的轮廓图
        block_data = self.get_block_data(block_width, block_height, block_radius)
        # 防止数组越界，保证边界为0
        block_data[0] = [0] * len(block_data[0])
        block_data[-1] = [0] * len(block_data[-1])
        # 创建滑块具体形状
        for i in range(block_width):
            # 将第1列 和 最后1列，设置为0，防止数组越界，保证边界为0
            block_data[i][0] = 0
            block_data[i][-1] = 0
            for j in range(block_height):
                # 原图中对应位置变色处理
                if block_data[i][j] == 1:
                    # 背景设置为黑色
                    water_image.putpixel((i, j), (0, 0, 0, 255))
                    block_image.putpixel((i, j), canvas_image.getpixel((block_x + i, block_y + j)))
                    # 轮廓设置为白色，取带像素和无像素的界点，判断该点是不是临界轮廓点
                    if block_data[i + 1][j] == 0 or block_data[i][j + 1] == 0 or block_data[i - 1][j] == 0 or \
                            block_data[i][j - 1] == 0:
                        block_image.putpixel((i, j), (255, 255, 255, 255))
                        water_image.putpixel((i, j), (255, 255, 255, 255))
                # 把背景设为透明
                else:
                    block_image.putpixel((i, j), (0, 0, 0, 0))
                    water_image.putpixel((i, j), (0, 0, 0, 0))
        # 在画布上添加阻塞块水印
        self.add_block_watermark(canvas_image, water_image, block_x, block_y)


    # 构建拼图轮廓轨迹
    def get_block_data(self, block_width, block_height, block_radius):
        """
        先创建一个二维数组data，然后随机生成两个圆的坐标，并在4个方向上随机找到2个方向添加凸/凹
        它获取凸/凹起位置坐标，并随机选择凸/凹类型。
        最后，计算需要的小图轮廓，用二维数组来表示，二维数组有两张值，0和1，其中0表示没有颜色，1有颜色。
        """
        data = [[0 for _ in range(block_width)] for _ in range(block_height)]  # 初始化二维数组，元素为0
        po = math.pow(block_radius, 2)
        # 随机生成两个圆的坐标，在4个方向上 随机找到2个方向添加凸/凹
        # 凸/凹1
        face1 = random.randint(0, 4)
        # 凸/凹2
        face2 = random.randint(0, 4)
        # 保证两个凸/凹不在同一位置
        while face1 == face2:
            face2 = random.randint(0, 4)
        # 获取凸/凹起位置坐标
        circle1 = self.get_circle_coords(face1, block_width, block_height, block_radius)
        circle2 = self.get_circle_coords(face2, block_width, block_height, block_radius)
        # 随机凸/凹类型
        shape = random.randint(0, 1)
        # 圆的标准方程 (x-a)²+(y-b)²=r²，标识圆心（a,b），半径为r的圆
        # 计算需要的小图轮廓，用二维数组来表示，二维数组有两张值，0和1，其中0表示没有颜色，1有颜色
        for i in range(block_width):
            for j in range(block_height):
                # 创建中间的方形区域
                if (i >= block_radius and i <= block_width - block_radius and j >= block_radius and j <= block_height - block_radius):
                    data[i][j] = 1
                double_d1 = math.pow(i - circle1[0], 2) + math.pow(j - circle1[1], 2)
                double_d2 = math.pow(i - circle2[0], 2) + math.pow(j - circle2[1], 2)
                # 创建两个凸/凹
                if double_d1 <= po or double_d2 <= po:
                    data[i][j] = shape
        return data


    # 根据朝向获取圆心坐标
    @staticmethod
    def get_circle_coords(face, block_width, block_height, block_radius):
        """
        根据传入的face值（0表示上，1表示左，2表示下，3表示右），
        返回一个包含两个整数的数组，分别表示圆心的 横坐标 和 纵坐标。
        """
        if face == 0:  # 上
            return [block_width // 2 - 1, block_radius]
        elif face == 1:  # 左
            return [block_radius, block_height // 2 - 1]
        elif face == 2:  # 下
            return [block_width // 2 - 1, block_height - block_radius - 1]
        # elif face == 3:  # 右
        #     return [block_width - block_radius - 1, block_height // 2 - 1]
        else:
            return [block_width - block_radius - 1, block_height // 2 - 1]  # face == 4, 按3处理


    # 在画布上添加阻塞块水印
    @staticmethod
    def add_block_watermark(canvas_image, block_image, x, y):
        draw = ImageDraw.Draw(canvas_image)
        canvas_image.paste(block_image, (x, y), block_image)


    # 将图片转换为base64
    @staticmethod
    def image_to_base64(image):
        buffered = io.BytesIO()
        image.save(buffered, format="png")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str.decode('utf-8')

    def generate_captcha_images(self):
        """
        生成验证码画布图和滑块图，并返回 Base64 字符串和滑块Y坐标
        """
        canvas_width, canvas_height = self.img_size
        block_width, block_height = self.block_size
        block_radius = self.block_radius

        # 获取随机画布
        canvas_image = self.get_random_resized_image(CAPTCHA_PATH, 1, CAPTCHA_COUNT, canvas_width, canvas_height)

        # 随机生成滑块坐标
        block_x = random.randint(block_width, canvas_width - block_width - 10)
        block_y = random.randint(10, canvas_height - block_height + 1)
        self.blockX = block_x
        self.blockY = block_y

        # 新建滑块图
        block_image = Image.new("RGBA", (block_width, block_height))
        self.cut_by_template(canvas_image, block_image, block_width, block_height, block_radius, block_x, block_y)

        # 转为 Base64
        canvas_str = self.image_to_base64(canvas_image)
        block_str = self.image_to_base64(block_image)

        return {
            "canvas_str": canvas_str,
            "block_str": block_str,
            "block_x": block_x,
            "block_y": block_y
        }