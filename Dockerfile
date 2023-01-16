FROM python:3.7-buster
COPY requirements.txt /
RUN apt-get update
Run apt-get upgrade -y
RUN apt-get install -y pkg-config \
  libboost-python-dev \
  libboost-thread-dev \
  libbluetooth-dev \
  libglib2.0-dev \
  python3-dev
RUN pip install --root-user-action=ignore --upgrade pip
RUN pip install --root-user-action=ignore -r requirements.txt
RUN pip install --root-user-action=ignore gunicorn
RUN pip install --root-user-action=ignore gattlib
COPY . /
CMD [ "python", "-m", "host_page" ]
