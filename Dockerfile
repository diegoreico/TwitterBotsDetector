FROM python:3.6

# Setup project
WORKDIR /project
COPY ./ars /project/ars
COPY setup.py /project/setup.py
COPY setup.cfg /project/setup.cfg
COPY ./data /project/data

# Install system requirements
RUN pip install .