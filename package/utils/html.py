"""
content = {
    page: {
        h1: '',
        div: '',
        ul: {
            li: ''
        }
        img: ('path', ('height', 'width'))
}
"""
import os

from jinja2 import Environment, FileSystemLoader

from package.const import STATIC_PATH


TEMPLATE_PATH = os.path.join(STATIC_PATH, 'templates')


class PageFilter:
    def __init__(self):
        self.cur_page = 0

    def get_page(self, arg):
        self.cur_page += 1
        return self.cur_page


class HtmlPrinter:
    def __init__(self, template_name):
        env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
        self._init_filter(env)
        self.template = env.get_template(template_name)

    @staticmethod
    def _init_filter(env):
        env.filters['get_page'] = PageFilter().get_page

    def save(self, filepath, context):
        save_path = '%s.html' % filepath
        res = self.template.render(context)
        self._save_file(save_path, res)
        return save_path

    @staticmethod
    def _save_file(filepath, text):
        with open(filepath, 'w') as f:
            f.write(text)
