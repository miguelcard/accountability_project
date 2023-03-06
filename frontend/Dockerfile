FROM node:16.16.0-alpine
WORKDIR /code/frontend

COPY package.json package-lock.json ./
RUN npm config set legacy-peer-deps true
RUN npm install
RUN npm install react-scripts@4.0.3 -g
RUN npm install typescript
COPY . ./