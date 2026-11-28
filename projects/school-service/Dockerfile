FROM python:3.13-slim
WORKDIR /app
COPY school_service ./school_service
ENV SCHOOL_HOST=0.0.0.0
ENV SCHOOL_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "school_service"]
