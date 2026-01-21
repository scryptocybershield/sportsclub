# docker/nginx/Dockerfile
FROM nginx:stable-trixie
EXPOSE 80

# Install gettext for envsubst command
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# Set default active color for blue-green deployment
ENV ACTIVE_COLOR=blue

# COPY is relative to the context defined in the `docker-compose.yml` file,
# i.e., the project root, not the Dockerfile location.
# Copy template and process with environment variables
COPY docker/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
RUN envsubst '${ACTIVE_COLOR}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
