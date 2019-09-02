FROM python:3.7
LABEL maintainer="dev@cuenca.com"

# Install app
ADD Makefile requirements.txt /hub/
WORKDIR /hub
RUN make install
ADD hub /hub/
