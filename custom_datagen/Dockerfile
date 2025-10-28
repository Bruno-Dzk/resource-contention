# Use the official Go image to build the binary
FROM docker.io/golang:1.25-alpine AS builder
WORKDIR /src

# install native deps needed by goczmq
RUN apk add --no-cache \
      czmq-dev \
      zeromq-dev \
      pkgconfig \
      build-base \
      ca-certificates
      
# git is needed to download modules on alpine
RUN apk add --no-cache git

# Copy go.mod/go.sum first to cache module download step
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build a static binary
COPY . .
RUN CGO_ENABLED=1 GOOS=linux go build -ldflags="-s -w" -o /app ./ 

# Final image: small alpine with ca-certificates
FROM docker.io/alpine:3.22
RUN apk add --no-cache \
      czmq \
      libzmq \
      ca-certificates

# Copy binary from builder stage
COPY --from=builder /app /app

# Run the binary
ENTRYPOINT ["/app"]
