# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, jsonify
import rusclasp

__author__ = 'gree-gorey'

# Initialize the Flask application
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/_split_sentence')
def split_sentence():
    s = rusclasp.Splitter()
    sentence = request.args.get('sentence', 0, type=unicode)
    result = s.split(sentence)
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(
        # host="127.0.0.1",
        # port=int("80"),
        debug=True
    )
