FROM node:12-slim

RUN npm install -g @vue/cli @vue/cli-service-global

RUN mkdir /www
WORKDIR /www
COPY . /www

RUN npm install

CMD npm run serve
