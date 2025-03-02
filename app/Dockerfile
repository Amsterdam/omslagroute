ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.12

FROM node:${NODE_VERSION}-bullseye AS node

FROM python:${PYTHON_VERSION}-bullseye

# Copy necessary Node.js binaries from the Node.js image
COPY --from=node /usr/lib /usr/lib
COPY --from=node /usr/local/lib /usr/local/lib
COPY --from=node /usr/local/include /usr/local/include
COPY --from=node /usr/local/bin /usr/local/bin

# Check if Node and npm are available
RUN node -v && npm -v

# Add user and set environment variables
RUN adduser --system datapunt
RUN adduser datapunt sudo
ENV PYTHONUNBUFFERED 1

# Set build-time environment variables
ARG COMMIT_HASH
ARG BRANCH_NAME
ARG INVENTORY
ENV COMMIT_HASH=${COMMIT_HASH} \
    BRANCH_NAME=${BRANCH_NAME} \
    INVENTORY=${INVENTORY}

# update
RUN apt-get update
RUN apt-get install libpq-dev build-essential ca-certificates -y

COPY ./certificates/adp_rootca.crt /usr/local/share/ca-certificates/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/adp_rootca.crt \
  && update-ca-certificates --fresh

RUN pip install --upgrade pip && \
  pip install --no-cache-dir uwsgi
RUN apt install libmagic1 -y
RUN apt-get -y install locales

# install nginx
RUN apt-get install -y nginx

RUN mkdir -p /static
RUN mkdir -p /static/images
RUN mkdir -p /app
RUN mkdir -p /downloads
RUN mkdir -p /certificates
RUN mkdir -p /deploy
RUN mkdir -p /var/log/uwsgi
RUN mkdir -p /var/uwsgi/

RUN chmod -R 777 /static

COPY ./nginx/vhost.conf /etc/nginx/sites-enabled/
COPY . /app/
COPY deploy /deploy/

RUN sed -i -e 's/# nl_NL.UTF-8 UTF-8/nl_NL.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG nl_NL.UTF-8
ENV LANGUAGE nl_NL:nl
ENV LC_ALL nl_NL.UTF-8
WORKDIR /app

RUN npm install

RUN npm rebuild

COPY requirements.txt /app/

RUN ./node_modules/.bin/sass static_src/sass:./assets/bundles/

RUN ./node_modules/.bin/webpack --config webpack.config.js --mode production

RUN pip install --no-cache-dir -r requirements.txt

RUN export REQUEST_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

CMD ["/deploy/docker-run.sh"]
