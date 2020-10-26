FROM ubuntu:focal

SHELL ["bash", "-c"]

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /etc/dpkg/sources.list.d/
RUN echo "deb http://ppa.launchpad.net/benjamin-sipsolutions/sdaps-stable/ubuntu xenial main" > /etc/dpkg/sources.list.d/sdaps

RUN apt update && apt install -y curl gnupg

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN apt update && \
  apt upgrade -y && \
  apt install -y \
  git \
  python3-virtualenv \
  virtualenv \
  python3-pkgconfig \
  python3-dev \
  python3-distutils-extra \
  libtiff-dev \
  libglib2.0-dev \
  libgirepository1.0-dev \
  libcairo2-dev \
  python3-cairo-dev \
  python3-pip \
  screen \
  yarn \
  sdaps

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

ADD . /project

WORKDIR /project

RUN pip install -r requirements.txt

EXPOSE 8080
