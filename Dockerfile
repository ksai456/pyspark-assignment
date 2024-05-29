FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
LABEL Name=pyspark Version=0.0.1

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD Assessment.ipynb /app/Assessment.ipynb
ADD manage.py /app/manage.py
ADD requirements.txt /app/requirements.txt
# ADD local-packages /app/local-packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends openjdk-17-jdk

# Download and install the Postgres JDBC driver
# RUN wget  https://jdbc.postgresql.org/download/postgresql-42.7.3.jar
# RUN mv postgresql-42.7.3.jar /app/jars/postgresql-42.7.3.jar

# Download and install Spark
# RUN apt-get update && apt-get install -y wget
# RUN wget https://downloads.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz
# RUN tar xvf spark-3.1.2-bin-hadoop3.2.tgz
# RUN mv spark-3.1.2-bin-hadoop3.2 /opt/spark

# Set environment variables for Spark
# ENV SPARK_HOME=/opt/spark
# ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
# ENV PYSPARK_PYTHON=python3

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
# RUN pip install --no-index --find-links /app/local-packages -r requirements.txt

# Create a non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Run app.py when the container launches
CMD ["python", "manage.py"]


# RUN apt-get -y update && apt-get install -y fortunes
# CMD ["sh", "-c", "/usr/games/fortune -a | cowsay"]
