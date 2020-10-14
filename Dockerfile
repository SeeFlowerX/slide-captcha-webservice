FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip


# install requirement
WORKDIR /project
COPY requirements.txt /project
RUN pip install -r requirements.txt

# copy applicaton
ADD ./application/ /project


ENV FLASK_APP=main.py

# Expose the port
EXPOSE 8000


CMD ["python","main.py"]
