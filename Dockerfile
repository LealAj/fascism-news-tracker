# Dockerfile for docker-flask web application
# It is likley that this will be the template for the
# fascism news tracker

# Add a base image to build this image off of
FROM ubuntu:22.04

# Add Python via pip install and other python dependencies
# TODO: ADD the API packages, double check if we
# need the other python package check READ ME
RUN apt-get update && apt-get install -y \
 python3 \
 python3-pip \
 python3-dev \
 build-essential

# Add the files that will make up the flask application
COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

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
