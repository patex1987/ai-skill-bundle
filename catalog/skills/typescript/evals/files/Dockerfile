FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json tsconfig.json ./
RUN npm ci
COPY src ./src
RUN npm run build

FROM node:22-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
CMD ["node", "dist/index.js"]
