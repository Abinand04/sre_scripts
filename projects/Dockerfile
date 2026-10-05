# 1.import base image
FROM python:3.12-slim

# 2.Runtime settings for container
# - no .pyc files cluttering the image
# - unbuffered output , so logs show up immediately in docker logs 
# - pip doesn't keep its download cache in the image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 3.working directory of the app. all the commands are executed in this directory
WORKDIR /app

# 4. Create an unprivileged user to run app (never a root)
RUN useradd --create-home --uid 1000 appuser

# 5. Install dependencies before copying source code
COPY requirements.txt .
RUN pip install -r requirements.txt

# 6. copy application code
COPY healthchecker.py .

# 7. Drop root privileges from here on for appuser
USER appuser

# 8. The part that never changes as ENTRYPOINT and CMD with default url if no arguments are passed
ENTRYPOINT [ "python3", "healthchecker.py"  ]
CMD [ "https://google.com" ]





