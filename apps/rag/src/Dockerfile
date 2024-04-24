FROM python:latest
WORKDIR /genai
COPY . .
RUN pip install -I -r ./requirements.txt
EXPOSE 8080
CMD ["python", "/genai/main.py"]