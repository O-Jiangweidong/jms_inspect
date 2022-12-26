import os

from copy import deepcopy

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont  # 字体类
from reportlab.platypus import (
    Table, SimpleDocTemplate, Paragraph, Image, PageBreak
)  # 报告内容相关类
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm


def register_font(select=3):
    font_mapping = {}
    font_list = [
        'Alibaba-PuHuiTi-Bold.ttf',
        'Alibaba-PuHuiTi-Heavy.ttf',
        'Alibaba-PuHuiTi-Light.ttf',
        'Alibaba-PuHuiTi-Medium.ttf',
        'Alibaba-PuHuiTi-Regular.ttf',
        'HanYiYouYuan.ttf',
        'JiZiJingDianDaHei.ttf'
    ]
    for font_name in font_list:
        base_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'static'
        ))
        font_path = os.path.join(base_path, 'font', font_name)
        font = TTFont(font_name, font_path)
        pdfmetrics.registerFont(font)
        font_mapping[font_name] = font
    return font_list[select], font_mapping.pop(font_list[select])


PAGE_HEIGHT = A4[1]
PAGE_WIDTH = A4[0]
FONT_NAME, FONT = register_font()


class PDFPrinter:
    def __init__(self):
        self.all_style = getSampleStyleSheet()
        self._title = []

    def set_title(self, title):
        self._title.append(title)

    def save(self, filepath, content):
        pdf_obj = SimpleDocTemplate(filepath, pagesize=letter)
        pdf_obj.build(content, onFirstPage=self.first_page, onLaterPages=self.later_pages)

    def draw_head_info(self, c: Canvas):
        font_size = 30
        c.setFillColor(colors.green)
        margin = (PAGE_HEIGHT - 2 * font_size) / 2
        for t in self._title:
            c.setFont(FONT_NAME, font_size)
            c.drawCentredString(300, PAGE_HEIGHT - margin, t)
            margin += font_size * 2
            font_size = font_size if font_size < 20 else font_size - 5

        c.showPage()
        self.draw_page_info(c)

    @staticmethod
    def draw_page_info(c: Canvas):
        """绘制页脚"""
        # 设置边框颜色
        c.setStrokeColor(colors.dimgrey)
        # 绘制线条
        c.line(30, PAGE_HEIGHT - 790, 570, PAGE_HEIGHT - 790)
        # 绘制页脚文字
        c.setFont(FONT_NAME, 8)
        c.setFillColor(colors.black)
        page_number = '第%s页' % (c.getPageNumber() - 1)

        c.drawString(30, PAGE_HEIGHT - 810, page_number)
        length = FONT.stringWidth('JumpServer 堡垒机巡检报告', 8)
        c.drawString(570 - length, PAGE_HEIGHT - 810, 'JumpServer 堡垒机巡检报告')

    def first_page(self, c: Canvas, doc: SimpleDocTemplate):
        c.saveState()
        # 绘制首页
        self.draw_head_info(c)

    def later_pages(self, c: Canvas, doc):
        c.saveState()
        # 绘制页脚
        self.draw_page_info(c)
        c.restoreState()

    def draw_h1(self, title: str):
        """绘制一级标题"""
        ct = self.all_style['h1']
        ct.fontName = FONT_NAME
        ct.fontSize = 18
        ct.leading = 50
        ct.textColor = colors.green
        ct.alignment = 1  # 居中
        ct.bold = True
        return Paragraph(title, ct)

    def draw_h2(self, title: str):
        """
        绘制二级标题
        :param title:
        :return:
        """
        ct = self.all_style['h2']
        ct.fontName = FONT_NAME
        ct.alignment = TA_LEFT
        ct.bold = True
        ct.textColor = colors.darkblue
        return Paragraph(title, ct)

    def draw_h3(self, title: str, color='dodgerblue'):
        """
        绘制三级标题
        :param title:
        :return:
        """
        ct = self.all_style['h3']
        ct.fontName = FONT_NAME
        ct.alignment = TA_LEFT
        ct.textColor = getattr(colors, color, colors.dodgerblue)
        return Paragraph(title, ct)

    def draw_body(self, text: str, alert=False):
        """
        绘制正文
        :param alert: 是否标红
        :param text: 文本内容
        :return:
        """
        # 多余的空格会被删除，使用前端转义符实现空格
        text = text.replace(' ', '&nbsp ')
        ct = deepcopy(self.all_style['BodyText'])
        ct.fontName = FONT_NAME
        ct.fontSize = 8
        ct.wordWrap = 'CJK'  # 设置自动换行
        ct.alignment = TA_LEFT
        ct.firstLineIndent = 12  # 第一行开头空格
        ct.leading = 10
        if alert:
            ct.bold = True
            ct.textColor = colors.white
            ct.backColor = colors.fidred
        return Paragraph(text, ct)

    # 绘制表格
    @staticmethod
    def draw_table(*args):
        style = [
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),  # 字体
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # 第二行到最后一行的字体大小
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 第一行水平居中
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 第二行到最后一行左对齐
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.black),
            # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
        ]
        table = Table(args, style=style, hAlign='LEFT', spaceAfter=10)
        return table

    # 绘制图片
    @staticmethod
    def draw_img(path):
        img = Image(path)
        # img.drawWidth = 21 * cm
        # img.drawHeight = 29.7 * cm
        return img

    @staticmethod
    def get_new_page():
        return PageBreak()
