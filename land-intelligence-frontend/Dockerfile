# syntax=docker/dockerfile:1
# =============================================================================
# Land Intelligence & Stewardship System — Frontend Image
# -----------------------------------------------------------------------------
# Multi-stage build for the Vite/React application:
#   * Stage 1 (build) : installs Node deps and runs `npm run build`
#   * Stage 2 (serve) : serves the static bundle via nginx
#
# Build:
#   docker build -t land-intelligence-frontend:latest .
# (Run from within the land-intelligence-frontend directory)
# =============================================================================

###############################################################################
# STAGE 1 — BUILD
###############################################################################
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first (cache layer unless package manifests change)
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the source and build the production bundle
COPY . .
RUN npm run build

###############################################################################
# STAGE 2 — SERVE (nginx)
###############################################################################
FROM nginx:1.27-alpine AS runtime

# SPA-friendly nginx config: route unknown paths to index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the compiled static assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/ > /dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
