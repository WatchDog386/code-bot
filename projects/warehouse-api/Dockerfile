FROM golang:1.27-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -o /warehouse-api ./cmd/server

FROM scratch
COPY --from=build /warehouse-api /warehouse-api
ENV WAREHOUSE_HOST=0.0.0.0
ENV WAREHOUSE_PORT=8080
EXPOSE 8080
ENTRYPOINT ["/warehouse-api"]
