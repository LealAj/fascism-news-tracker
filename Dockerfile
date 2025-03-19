# Dockerfile for docker-flask web application
# It is likley that this will be the template for the
# fascism news tracker

# Add a base image to build this image off of
FROM ubuntu:22.04

# Add Python via pip install and other python dependencies
# TODO: Adapt the container to run as a service
# This should allow the docker secret to be used for api key
# or i can use dotenv and .env file to make enviorment (better for git push)
# docker build --secret id=my_api_key,src=api_key.txt . ???
# docker build secret are consumed on during app's build process
RUN apt-get update && apt-get install -y \
 python3 \
 python3-pip \
 python3-dev \
 build-essential

# Add the files that will make up the flask application
# Add a run command with the keyring to generate key in the container??
COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
RUN pip3 install  spacy

COPY data.py /usr/src/app/

# This is necesssary to use spacy
RUN python3 -m spacy download en_core_web_lg
# copy over the application itself and the css file (CSS FILE NOT GOING TO CONTAINER?)
COPY app.py /usr/src/app/

# copy over the data (JSON file), templates (Html file), and styling (CSS file)
ADD /assets/headline_example.json /usr/src/app/data/
ADD index.html /usr/src/app/templates/
ADD style.css usr/src/app/static/

# Add a default port containers from this image should expose
# Does the number matter? -- Look into 
# NOTE: EXPOSE does not actually publish the port. It functions
# as a documentation between the person who builds the image and the
# user of the container 
EXPOSE 5000

# Add a default command for this image
CMD ["python3", "/usr/src/app/app.py"]
