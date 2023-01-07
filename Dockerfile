FROM python:3
COPY requirements.txt /
RUN pip install gunicorn
RUN pip install -r requirements.txt
COPY gunicorn.conf /
COPY . /
CMD [ "gunicorn", "-c", "gunicorn.conf", "host_page:init_app" ]
