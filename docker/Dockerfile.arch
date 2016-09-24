# Docker Image for hfos - Arch Linux x64 version
#
# This image essentially packages up HFOS
# into a Docker Image/Container running Arch Linux OS x64.
#
# Usage Examples(s)::
#
#     $ docker run -i -t hackerfleet/hfos hfos_launcher.py
#     $ docker run -i -t -p 127.0.0.1:80:80 --name hfos-test-live -t hackerfleet/hfos
#
# VERSION: 1.1.0
#
# Last Updated: 20160818

FROM nfnty/arch-mini

MAINTAINER Heiko 'riot' Weinen <riot@c-base.org>

# Install dependencies

RUN pacman -Syyu --noconfirm

#RUN pacman-db-upgrade

RUN pacman -S --noconfirm --force \
        git \
        npm \
        enchant \
        mongodb \
        python-pip \
        python-setuptools \
        python-pymongo \
        python-urwid \
        python-pyserial

RUN pacman -Sc --noconfirm

# Mongo config (smallfiles), database startup and provisioning

RUN echo smallfiles = true >> /etc/mongodb.conf

# The next one was necessary on one installation, but that could've been due to a weird mongodb release
#RUN echo setParameter = textSearchEnabled = true >> /etc/mongodb.conf

RUN mongod -f /etc/mongodb.conf --fork & && python setup.py install_provisions

# Add user account and group

RUN useradd -Ums /bin/sh hfos

# Get HFOS

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos

# Install HFOS

RUN pip install -r requirements-dev.txt
RUN pip install .

# Install all modules

WORKDIR modules
RUN python install.py --all --dev
WORKDIR ..

# Make sure /var/[cache,lib]/hfos etc exists

RUN python setup.py install_var

# Generate & Install Documentation

#RUN python setup.py build_sphinx
#RUN python setup.py install_docs

# Install Frontend

RUN git submodule init && git submodule update

# Upgrade npm (from ancient Debian version to current)

RUN npm install npm -g

WORKDIR frontend
RUN npm install
WORKDIR ..

#  Services

EXPOSE 80

# If you want to run the frontend development live server, uncomment this:
# EXPOSE 8081

