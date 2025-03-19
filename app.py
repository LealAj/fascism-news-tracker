from data import *
from flask import Flask, render_template, abort, url_for, json, jsonify
import os

app = Flask(__name__)

# It is the intention to load us data on page as default
# otherwise it will be based on user input, should be very simple
# There will only be one other page. to desribe project?

# This works! However I am concerned that the api is in the container
# I have not been able to find it within image - 1/1/25
# Check again, check documentation for storage, it could be that
# current way consumes on run
api_key = os.getenv("API_KEY")


# This is a temporary solution for the API key to be solved with os.getenv?
# This prevents pushing the actual api code to git hub
# HOWEVER, it does place it in the container and is accesible??? 
news_data = GetNewsData(api_key).make_request()
parsed_json = ArticleScorer(news_data, "fascism").calc_scores(True)



# The ('/') dicatates that this is the homepage
@app.route('/')
def hello_world():
    return render_template('index.html', articles=parsed_json)


if __name__ == '__main__':
    # Note the extra host argument. If we didn't have it, our Flask app
    # would only respond to requests from inside our container
    app.run(host='0.0.0.0', debug=True)
