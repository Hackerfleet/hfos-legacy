# Docker Image for HFOS
#
# This image essentially packages up HFOS along with mongodb
# into a Docker Image/Container.
#
# Usage Examples::
#
# To run your instance and see if the backend starts:
#     $ docker run -i -t hackerfleet/hfos /bin/bash -c "/etc/init.d/mongodb start && hfos_launcher.py"
#
# To investigate problems on the docker container, i.e. get a shell:
#     $ docker run -i -t --name hfos-test-live -t hackerfleet/hfos
#
# If you want to run a productive instance with working SSL:
#     $ docker run -i -p 127.0.0.1:443:443 -t hackerfleet/hfos /bin/bash -c "/etc/init.d/mongodb start && \
#       python3 hfos_launcher.py --port 443 --cert /etc/ssl/certs/hfos/selfsigned.pem --log 10 --dev"
#
# VERSION: 1.1.2
#
# Last Updated: 20170712

FROM debian:experimental
MAINTAINER Heiko 'riot' Weinen <riot@c-base.org>

# Install dependencies

RUN echo "deb ftp://ftp2.de.debian.org/debian unstable main" > /etc/apt/sources.list
RUN echo "deb ftp://ftp2.de.debian.org/debian experimental main" > /etc/apt/sources.list.d/experimental.list

RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
        git \
        bzip2 \
        npm \
        nodejs-legacy \
        libfontconfig \
        build-essential \
        gdal-bin \
        locales \
        python-gdal \
        enchant \
        python3-virtualenv \
        python3-dev \
        python3-pymongo \
        python3-bson-ext \
        python3-pip \
        python3-wheel \
        python3-urwid \
        python3-setuptools \
        python3-setuptools-scm \
        python3-setuptools-git \
        python3-serial \
        python3-openssl


RUN echo "C.UTF-8" > /etc/locale.gen
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN locale-gen

# Get a very recent mongodb

RUN apt-get install -qy -t experimental mongodb

RUN apt-get clean

# Activate mongodb

RUN echo smallfiles = true >> /etc/mongodb.conf

# The next one was necessary on one installation, but that could've been due to a weird mongodb release
#RUN echo setParameter = textSearchEnabled = true >> /etc/mongodb.conf

# Create virtual environment

#RUN python3 /usr/lib/python3/dist-packages/virtualenv.py -p /usr/bin/python3.5 --system-site-packages venv

RUN useradd -ms /bin/bash hfos
WORKDIR /home/hfos

# Copy repository

COPY . hfos
WORKDIR hfos

# Fetch Frontend

RUN git submodule init && git submodule update

# Install HFOS

RUN pip3 install -r requirements-dev.txt
RUN python3 setup.py develop

# Upgrade npm (from ancient Debian version to 4.6.1 which has a proven track record at assembling the frontend)

RUN npm install -g npm@4.6.1

# Install HFOS

RUN python3 -u hfos_manage.py install cert
RUN python3 -u hfos_manage.py install var
# Rest might need a running db
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install modules
# Temporary hack, until we have provisioning obey dependencies again:
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install provisions -p system
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install provisions -p user
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install provisions
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install docs
RUN /etc/init.d/mongodb start && python3 -u hfos_manage.py install frontend --rebuild --dev

#  Services

EXPOSE 443

# There is a frontend development server with hot reloading which can be started with
#   $ hfos/frontend/npm run start
# If you want to run the frontend development live server, uncomment this:
#
# EXPOSE 8081

