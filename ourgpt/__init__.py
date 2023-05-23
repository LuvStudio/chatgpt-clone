from flask import Flask, redirect, send_file

app = Flask(__name__, template_folder='./../client/html')


@app.route('/')
def index():
    return redirect('/chat')

@app.route('/assets/<folder>/<file>')
def assets(folder: str, file: str):
    try:
        return send_file(f"./../client/{folder}/{file}", as_attachment=False)
    except:
        return "File not found", 404
    