from flask import render_template, redirect, Blueprint
from time import time
from os import urandom

bp = Blueprint('website', __name__, template_folder='./../client/html', url_prefix='/chat')

@bp.route('/')
def index():
    return render_template('index.html', chat_id=f'{urandom(4).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{hex(int(time() * 1000))[2:]}')

@bp.route('/<conversation_id>')
def chat(conversation_id):
    if not '-' in conversation_id:
        return redirect(f'/chat')

    return render_template('index.html', chat_id=conversation_id)
