FROM docker.io/library/golang:1.24.2 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY client.go .
RUN go build -o client

FROM docker.io/library/golang:1.24.2

WORKDIR /usr/src/app

COPY --from=builder /app/client ./client

ENTRYPOINT ["./client"]