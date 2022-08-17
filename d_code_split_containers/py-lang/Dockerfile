FROM python:3.8-slim-buster

WORKDIR /usr/src/app
COPY py-lang_v1.py ./
COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./py-lang_v1.py" ]