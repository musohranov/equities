"""
Реализация интерфейса 'web страница'
"""

import os
from flask import Flask, render_template, request

from src.interface.core.commands.manager import run_help_cmd, run_cmd, UnknownCmd

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.config.from_object(__name__)


@app.route('/', methods=['post', 'get'])
def _index():
    """
    Обработчик web страницы
    """

    command_line = request.form.get('cl')
    params = str(command_line or '').split()

    result_list = []
    if len(params) < 1:
        result_list = run_help_cmd()
    else:
        try:
            result_list = (run_cmd(params[0], params[1:]))
        except UnknownCmd as err:
            result_list = [f'Ошибка! {str(err)}'] + run_help_cmd()

    return render_template('index.html', **locals())


def run():
    """
    Запустить сервер
    """

    app.run(debug=True)


if __name__ == "__main__":
    run()
