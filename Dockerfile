FROM conda/miniconda3

# RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
# RUN apk --no-cache --update-cache add gcc gfortran python3 python3-dev py3-pip build-base wget freetype-dev libpng-dev openblas-dev
# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h


# application
WORKDIR /project
ADD ./application/ /project
COPY requirements.txt /project
RUN pip install -r requirements.txt

CMD ["python","main.py"]
