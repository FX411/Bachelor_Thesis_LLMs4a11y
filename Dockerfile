FROM node:18-alpine

WORKDIR /app

COPY webshop.package.json ./package.json
RUN npm install

COPY . .

EXPOSE 3000
CMD ["node", "src/server.js"]