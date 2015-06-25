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
    apt-get install -qy --no-install-recommends \
        mongodb \
        git \
        python-pip \
        python-grib && \
    apt-get clean

RUN git clone https://github.com/Hackerfleet/hfos
WORKDIR hfos
RUN pip install -r requirements.txt
RUN pip install .

#  Services
EXPOSE 8055 9000

# Volumes
VOLUME /var/www
