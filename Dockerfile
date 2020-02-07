FROM edxops/xenial-common:latest
RUN apt-get update && apt-get install -y \
    python-setuptools \
#     gettext \
#     lib32z1-dev \
#     libjpeg62-dev \
#     libxslt-dev \
#     libz-dev \
#     python3-dev \
#     python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN easy_install pip
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
&& rm /tmp/requirements.txt
ADD test_requirements.txt /tmp/test_requirements.txt
RUN pip install -r /tmp/test_requirements.txt \
&& rm /tmp/test_requirements.txt

RUN mkdir -p /usr/local/src/certs/certificates
WORKDIR /usr/local/src/certs/certificates
ADD . .
RUN make install
# EXPOSE 8000
ENTRYPOINT ["make", "coverage"]
# CMD ["-e", "py27"]
