# Docker Image for hfos
#
# This image essentially packages up HFOS
# into a Docker Image/Container.
#
# Usage Examples(s)::
#     
#     $ docker run -d -v /path/to/www:/var/www Hackerfleet/hfos hfos.web /var/www
#     $ docker run -i -t Hackerfleet/hfos hfos_test
#
# VERSION: 0.0.2
#
# Last Updated: 20141115

FROM library/debian
MAINTAINER Heiko 'riot' Weinen <riot@hackerfleet.org>

RUN apt-get update && \
    apt-get install -qy \
        mongodb \
        git \
        python3.4 \
        python3-pip \
        python3-grib \
        npm && \
    apt-get clean

RUN pip3 install -r requirements.txt
RUN python3 setup.py install

#  Services
EXPOSE 8055 9000

# Volumes
VOLUME /var/www
