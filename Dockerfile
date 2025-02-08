FROM node:18-alpine

WORKDIR /app

COPY data/website/package.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]