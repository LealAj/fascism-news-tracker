import socket # i belive this can be removed
from flask import Flask, render_template, abort, url_for, json, jsonify

app = Flask(__name__)

# It is the intention to load us data on page as default
# otherwise it will be based on user input, should be very simple
# There will only be one other page. to desribe project?

# read the json file and parse adn extaract data
with open('/usr/src/app/data/headline_example.json', 'r') as myfile:
    parsed_json = json.load(myfile)
    myfile.close

# The ('/') dicatates that this is the homepage
@app.route('/')
def hello_world():
    return render_template('index.html', articles=parsed_json)


if __name__ == '__main__':
    # Note the extra host argument. If we didn't have it, our Flask app
    # would only respond to requests from inside our container
    app.run(host='0.0.0.0', debug=True)
