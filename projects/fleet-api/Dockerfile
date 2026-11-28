FROM golang:1.27-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -o /fleet-api ./cmd/server

FROM scratch
COPY --from=build /fleet-api /fleet-api
ENV FLEET_HOST=0.0.0.0
ENV FLEET_PORT=8080
EXPOSE 8080
ENTRYPOINT ["/fleet-api"]
