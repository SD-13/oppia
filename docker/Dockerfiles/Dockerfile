FROM ubuntu:20.04

EXPOSE 8001
RUN apt-get update
RUN apt-get update --fix-missing
RUN apt-get install software-properties-common apt-utils -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update --fix-missing
RUN apt-get install --no-install-recommends python3-pip python3.8-distutils python3.8-venv python3.8 python3.8-dev build-essential npm curl git wget postgresql-client psmisc libpq-dev -y
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN pip install --upgrade pip
RUN pip install --upgrade virtualenv
RUN apt install bash
RUN apt install bash
RUN useradd --create-home app
USER app
RUN mkdir /home/app/oppia
WORKDIR /home/app
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/4164fced49af78c6275cb436c64369eb39c6acb1/bin/pyenv-installer | bash
RUN echo 'eval "$(pyenv virtualenv-init -)"' > .bashrc
ENV LANG=C.UTF-8
ENV HOME /home/app
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH;$HOME/.local/bin
RUN pyenv virtualenv system oppia
WORKDIR /home/app/oppia/
ADD ./requirements.txt ./requirements.txt
ADD ./docker/entry_point.sh ../dev-tools/docker/entry_point.sh
ADD ./setup_gae.py ../dev-tools/setup_gae.py

RUN echo oppia > /home/app/.python-version
RUN pip install --upgrade pip
RUN pip install -r /home/app/oppia/requirements.txt
WORKDIR /home/app/oppia/
RUN python ../dev-tools/setup_gae.py

ENTRYPOINT ["python", "../oppia_tools/google-cloud-sdk-364.0.0/google-cloud-sdk/bin/dev_appserver.py"]
