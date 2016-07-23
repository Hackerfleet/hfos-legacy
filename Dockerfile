# Docker Image for hfos
#
# This image essentially packages up HFOS
# into a Docker Image/Container.
#
# Usage Examples(s)::
#
#     $ docker run -i -t hackerfleet/hfos hfos_launcher.py
#     $ docker run -i -t -p 127.0.0.1:80:80 --name hfos-test-live -t hackerfleet/hfos
#
# VERSION: 1.1.0
#
# Last Updated: 20160723

FROM debian:experimental
MAINTAINER Heiko 'riot' Weinen <riot@hackerfleet.org>

# Install dependencies

RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
        git \
        bzip2 \
        npm \
        nodejs-legacy \
        libfontconfig \
        enchant \
        python3.5 \
        python3-pymongo \
        python3-bson-ext \
        python3-pip \
        python3-wheel \
        python3-setuptools \
        python3-setuptools-scm \
        python3-setuptools-git
RUN apt-get install -qy -t experimental mongodb

RUN apt-get clean

# Get HFOS

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos

# Install HFOS

RUN pip3 install -r requirements-dev.txt
RUN pip3 install .

# Install all modules

WORKDIR modules
RUN python3 install.py --all
WORKDIR ..

# Make sure /var/[cache,lib]/hfos etc exists

RUN python3 setup.py install_var

# Generate & Install Documentation

RUN python3 setup.py build_sphinx
RUN python3 setup.py install_docs

# Install Frontend

RUN git submodule init && git submodule update

#WORKDIR frontend
#RUN npm install
#WORKDIR ..

# Mongo config (smallfiles) and startup

RUN echo smallfiles = true >> /etc/mongodb.conf
RUN /etc/init.d/mongodb start

# Add provisions

RUN python3 setup.py install_provisions

#  Services

EXPOSE 80

# If you want to run the frontend development live server, uncomment this:
# EXPOSE 8081

