FROM node:14

WORKDIR /usr/iotstack_api

# node_modules is ignored with this copy, as specified in .dockerignore
COPY ./.internal/api ./
RUN npm install

EXPOSE 32128
CMD [ "npm", "start" ]
