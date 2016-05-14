# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, jsonify
import time
from rusclasp import rusclasp

__author__ = 'gree-gorey'

# Initialize the Flask application
app = Flask(__name__)


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the AJAX request, sum up two
# integer numbers (defaulted to zero) and return the
# result as a proper JSON response (Content-Type, etc.)
@app.route('/_split_sentence')
def add_numbers():
    t1 = time.time()
    sentence = request.args.get('sentence', 0, type=unicode)
    result = [sentence]
    t2 = time.time()
    while t2 - t1 < 0.5:
        t2 = time.time()
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(
        # host="127.0.0.1",
        # port=int("80"),
        debug=True
    )
