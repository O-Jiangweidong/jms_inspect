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


class HtmlPrinter:
    def __init__(self, template_name):
        env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
        self.template = env.get_template(template_name)

    def save(self, filepath, context):
        res = self.template.render(context)
        self._save_file(filepath, res)

    @staticmethod
    def _save_file(filepath, text):
        with open(filepath, 'w') as f:
            f.write(text)
