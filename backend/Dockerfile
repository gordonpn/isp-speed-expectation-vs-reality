FROM node:14-alpine
RUN apk --no-cache add curl
RUN mkdir -p /usr/src/app && chown -R node:node /usr/src/app
WORKDIR /usr/src/app
ENV PATH /usr/src/app/node_modules/.bin:$PATH
COPY --chown=node:node package*.json ./
USER node
RUN npm ci --only=production
RUN npm prune --production
RUN npm cache clean --force --loglevel=error
COPY --chown=node:node . .
EXPOSE 3000
CMD [ "node", "server.js" ]
