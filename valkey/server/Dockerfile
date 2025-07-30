FROM docker.io/valkey/valkey:8.1.1

RUN export MALLOC_CONF="purge:decay_time:9223372036854775807"

CMD ["valkey-server", "--save", "", "--maxmemory", "512mb", "--maxmemory-policy", "allkeys-random", "--loglevel", "warning"]