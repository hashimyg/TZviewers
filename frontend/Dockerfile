FROM nginx:alpine

# Futa ma-file ya default yaliyopo ndani ya Nginx server
RUN rm -rf /usr/share/nginx/html/*

# Nakili ma-file yetu ya HTML/CSS/JS ya ndani ya kompyuta kuja ndani ya Nginx container
COPY . /usr/share/nginx/html

# Fungua port 80 kwa ajili ya traffic ya website ya mbele
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
