FROM python:3.13-slim
WORKDIR /app
COPY clinic_service ./clinic_service
ENV CLINIC_HOST=0.0.0.0
ENV CLINIC_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "clinic_service"]
