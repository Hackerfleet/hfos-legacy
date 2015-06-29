# Docker Image for hfos
#
# This image essentially packages up HFOS
# into a Docker Image/Container.
#
# Usage Examples(s)::
#
#     $ docker run -i -t hackerfleet/hfos hfos_launcher.py
#
# VERSION: 0.0.1
#
# Last Updated: 20150626

FROM library/debian
MAINTAINER Heiko 'riot' Weinen <riot@hackerfleet.org>

RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
        mongodb \
        git \
        bzip2 \
        npm \
        nodejs-legacy \
        python-pip \
        python-bson \
        python-bson-ext \
        python-grib && \
    apt-get clean

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos
RUN pip install -r requirements.txt
RUN pip install .
RUN git submodule init && git submodule update
WORKDIR frontend
RUN npm config set prefix /usr/local && npm install -g --prefix=/usr/local
RUN npm -g install bower grunt-cli
RUN bower install --config.interactive=false --allow-root
RUN grunt install

#  Services
EXPOSE 8055 9000

# Volumes
VOLUME /var/www
