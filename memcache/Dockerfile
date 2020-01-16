FROM ubuntu
RUN apt-get update
RUN apt-get install -y memcached
CMD ["memcached -m", "256"]
USER daemon
ENTRYPOINT memcached 