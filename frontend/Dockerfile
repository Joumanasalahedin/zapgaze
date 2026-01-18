FROM node:20-alpine

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

ARG VITE_API_URL
ARG VITE_FRONTEND_API_KEY

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_FRONTEND_API_KEY=${VITE_FRONTEND_API_KEY}

EXPOSE 5173

CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "5173"] 
