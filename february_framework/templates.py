from jinja2 import Template, FileSystemLoader
from jinja2.environment import Environment
import os


def render(template_name, folder='templates', **kwargs):
    """
    :param template_name: имя шаблона
    :param folder: папка в которой ищем шаблон
    :param kwargs: параметры
    :return:
    """

    environ = Environment()
    environ.loader = FileSystemLoader(folder)
    tmpl = environ.get_template(template_name)
    return tmpl.render(**kwargs)