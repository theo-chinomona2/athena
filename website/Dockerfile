# Athena docs site — Docusaurus build served by nginx.
# Build context is website/ (the repo-root .dockerignore excludes website/, so a
# repo-root context can't be used here anyway). The Docusaurus prebuild
# (scripts/prebuild.mjs) generates llms.txt via python+pyyaml; it degrades
# gracefully (empty skills hub) when the repo's skills/ dir isn't in context,
# and onBrokenLinks='warn' keeps the build green without the skill-doc generator.
FROM node:22-bookworm-slim AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-yaml ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /site
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runner
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /site/build /usr/share/nginx/html
EXPOSE 80
