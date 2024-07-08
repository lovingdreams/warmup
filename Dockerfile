FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    git \
    libcairo2-dev \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE src.settings
ENV DEBUG_MODE False
ENV CONFIG_PATH=common/configs/stage.cfg

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
# RUN pip install --upgrade pip
# RUN pip install bottle
# RUN pip install sanic
# RUN pip install tornado
# RUN pip install pyramid
# RUN pip install starlette
# RUN pip install fastapi
# RUN pip install Flask
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://workemasteradmin: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@github.com/worketeam/BaseWorke
RUN pip install celery
RUN pip install gunicorn
# Copy the rest of the application code into the container at /app
COPY . /app/

# Run Django migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Expose the port your app runs on (Gunicorn default is 8000)
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.wsgi:application"]
