FROM node:lts-bookworm

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY .next .next

EXPOSE 3100

CMD ["npm", "run", "start"]