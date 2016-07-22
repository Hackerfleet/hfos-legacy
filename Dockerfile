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

FROM library/debian
MAINTAINER Heiko 'riot' Weinen <riot@hackerfleet.org>

# Install dependencies

RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
        mongodb \
        git \
        bzip2 \
        npm \
        nodejs-legacy \
        libfontconfig \
        python3-pip && \
    apt-get clean

# Get HFOS

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos

# Install HFOS

RUN pip install -r requirements.txt
RUN pip install .

# Install all modules

WORKDIR modules
RUN python install.py --all

# Make sure /var/[cache,lib]/hfos etc exists

RUN python setup.py install_var
RUN python setup.py install_provisions

# Generate & Install Documentation

RUN python setup.py build_sphinx
RUN python setup.py install_docs

# Install Frontend

RUN git submodule init && git submodule update

WORKDIR ../frontend
RUN npm install

# Mongo config (smallfiles) and startup

RUN echo smallfiles = true >> /etc/mongodb.conf
RUN /etc/init.d/mongodb start

#  Services

EXPOSE 80

# If you want to run the frontend development live server, uncomment this:
# EXPOSE 8081

