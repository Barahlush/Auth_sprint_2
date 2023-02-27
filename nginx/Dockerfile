FROM nginx:1.23.2
RUN apt-get update && apt-get install -y nginx-extras
COPY ./nginx.conf /etc/nginx/
COPY ./site.conf /etc/nginx/conf.d/
