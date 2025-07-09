FROM openjdk:17-jdk-slim

ENV ICEBERG_VERSION=1.4.2

RUN apt-get update && apt-get install -y curl && \
    curl -L -o iceberg-rest-catalog.jar https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-rest-catalog/${ICEBERG_VERSION}/iceberg-rest-catalog-${ICEBERG_VERSION}-all.jar && \
    apt-get clean

EXPOSE 8181

ENTRYPOINT ["java", "-jar", "iceberg-rest-catalog.jar", "server"]
