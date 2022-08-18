FROM python:3.8-slim-buster

WORKDIR /usr/src/app
COPY py-tweets-lang_v3.py ./
COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./py-tweets-lang_v3.py" ]