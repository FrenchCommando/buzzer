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
RUN apt-get install -y bluez
#RUN apt-get install -y python3-setuptools
#RUN apt-get upgrade -y
RUN pip install --upgrade pip
RUN pip install --root-user-action=ignore -r requirements.txt
RUN pip install --root-user-action=ignore gunicorn
#ADD gattlib-0.20210616.tar.gz /
#RUN cd gattlib-0.20210616 && pip install . && cd ..
RUN pip install --root-user-action=ignore gattlib
COPY gunicorn.conf /
COPY . /
#CMD ["python", "-u", "timeimport.py"]
#CMD ["python", "-u", "gattimport.py"]
CMD [ "gunicorn", "-c", "gunicorn.conf", "host_page:init_app" ]
VOLUME /var/run/dbus:/var/run/dbus:z
