FROM node:lts-bookworm

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build

EXPOSE 3100

CMD ["npm", "run", "start"]