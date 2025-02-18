
# Create a virtual environment
FROM python:3.10.4

WORKDIR /tmp

# Create a virtual environment
RUN python3 -m venv .venv

# Activate the virtual environment
RUN source .venv/bin/activate

COPY . /tmp

# Create Matplotlib config directory inside the image
RUN mkdir -p /root/.config/matplotlib

# Set the environment variable *inside* the Dockerfile
ENV MPLCONFIGDIR="/root/.config/matplotlib"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

# Upgrade httpx and httpcore *before* installing other requirements
RUN pip install --upgrade httpx httpcore

RUN pip install -r requirements.txt

# (Optional) For debugging:
RUN pip freeze | grep httpx > httpx_version.txt
RUN pip freeze | grep httpcore > httpcore_version.txt

ENV GRADIO_SERVER_PORT=8080
ENV GRADIO_SERVER_NAME=0.0.0.0

EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["model_application.py"]
