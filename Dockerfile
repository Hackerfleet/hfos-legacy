# Docker Image for hfos
#
# This image essentially packages up HFOS
# into a Docker Image/Container.
#
# Usage Examples(s)::
#
#     $ docker run -i -t hackerfleet/hfos hfos_launcher.py
#     $ docker run -i -t -p 127.0.0.1:8055:8055 --name hfos-test-live -t hackerfleet/hfos
#
# VERSION: 0.0.1
#
# Last Updated: 20150626

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
        python-pip && \
    apt-get clean

# Get HFOS

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos

# Install HFOS

RUN pip install -r requirements.txt
RUN pip install .

# Make sure /var/[cache,lib]/hfos etc exists

RUN python setup.py install_var
RUN python setup.py install_provisions

# Install Frontend

RUN git submodule init && git submodule update

WORKDIR frontend
RUN npm install
RUN npm -g install bower grunt-cli
RUN bower install --config.interactive=false --allow-root
RUN grunt copy:dev --force

# Mongo config (smallfiles) and startup

RUN echo smallfiles = true >> /etc/mongodb.conf
RUN /etc/init.d/mongodb start

#  Services

EXPOSE 80 8055 9000

