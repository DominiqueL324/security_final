FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install --force-reinstall -r requirements.txt
RUN pip3 install pip install djangorestframework-simplejwt
RUN pip3 install xlwt
RUN pip3 install xlrd
COPY . /code/
