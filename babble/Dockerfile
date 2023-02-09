FROM python:3.9-slim-buster

# INSTALLING APT PACKAGES
RUN apt-get -y update
RUN apt-get -y install unzip wget
ARG VERSION_TERRAFORM=1.3.7
RUN wget -q https://releases.hashicorp.com/terraform/${VERSION_TERRAFORM}/terraform_${VERSION_TERRAFORM}_linux_amd64.zip
RUN unzip terraform_${VERSION_TERRAFORM}_linux_amd64.zip
RUN install terraform /usr/local/bin
RUN terraform -v

# INSTALLING PIP PACKAGES
RUN pip install awscli pyyaml simple-term-menu yaspin

# CACHING TERRAFORM PLUGINS
COPY providers /providers
ENV TF_PLUGIN_CACHE_DIR /providers
RUN terraform -chdir=/providers init

COPY scripts /scripts
COPY templates /templates
COPY volumes /volumes
COPY docker_entry.py /docker_entry.py

ENTRYPOINT ["python3", "docker_entry.py"]