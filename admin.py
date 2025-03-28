from flask import Flask, render_template, make_response
import os

app = Flask(__name__)

@app.route('/')
def home():
    response = make_response(render_template('admin.html', flag="flag{fake_one_for test}"))
    response.headers['X-Frame-Options'] = 'DENY'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
