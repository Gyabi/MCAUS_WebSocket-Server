FROM python:3.8-alpine

WORKDIR /usr/src/client
ADD requirements.txt .

# コンテナ内で必要なパッケージをインストール
# RUN apk add --no-cache build-base mariadb-connector-c-dev
# requirements.txtにリストされたパッケージをインストールする
RUN pip install --trusted-host pypi.python.org -r requirements.txt