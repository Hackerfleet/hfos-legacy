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

# Install Frontend

RUN git submodule init && git submodule update

WORKDIR frontend
RUN npm install
RUN npm -g install bower grunt-cli
RUN bower install --config.interactive=false --allow-root
RUN grunt copy:dev --force

#  Services

EXPOSE 80 8055 9000

