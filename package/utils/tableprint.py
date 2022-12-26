import math


class TablePrint(object):
    def __init__(self):
        self.headers = None
        self.row_list = []
        self.headers_length_list = []

    def __refresh_headers_length_list(self, row):
        current_headers_list_length = len(self.headers_length_list)
        for index, value in enumerate(row):
            value = self.__type_converse(value)
            padding = math.ceil((len(value.encode('utf8')) - len(value)) / 3)
            value_length = len(value) + padding
            if len(row) > current_headers_list_length:
                self.headers_length_list.append(value_length)
            else:
                self.headers_length_list[index] = max([value_length, self.headers_length_list[index]])

    def __get_margin_layer_display(self):
        margin_layer = ''
        for length in self.headers_length_list:
            margin_layer += '+ %s +' % ('-' * length)
        return margin_layer

    @staticmethod
    def __type_converse(value):
        if value is True:
            return '✔'
        elif value is False:
            return '×'
        else:
            return value

    def __get_middle_layer_display(self, row):
        middle_layer = ''
        for i, h in enumerate(row):
            h = self.__type_converse(h)
            padding = math.ceil((len(h.encode('utf8')) - len(h)) / 3)
            middle_layer += '| {:^{}} |'.format(h, self.headers_length_list[i] - padding)
        return middle_layer

    def __calc_table_header_display(self):
        margin_layer = self.__get_margin_layer_display()
        middle_layer = self.__get_middle_layer_display(self.headers)

        print(margin_layer)
        print(middle_layer)
        print(margin_layer)

    def __calc_table_value_display(self):
        for row in self.row_list:
            middle_layer = self.__get_middle_layer_display(row)
            print(middle_layer)

    def __calc_table_bottom_display(self):
        bottom_layer = self.__get_margin_layer_display()
        print(bottom_layer)

    def add_headers(self, headers):
        self.headers = list(headers)
        self.__refresh_headers_length_list(headers)

    def add_row(self, row):
        if len(row) != len(self.headers):
            raise ValueError('表内容和表头不对应，请检查!')
        self.__refresh_headers_length_list(row)
        self.row_list.append(row)

    def show(self):
        self.__calc_table_header_display()
        self.__calc_table_value_display()
        self.__calc_table_bottom_display()
