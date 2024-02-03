#This file is part of ElectricEye.
#SPDX-License-Identifier: Apache-2.0

#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

# latest hash as of 25 JAN 2024 - Alpine 3.19.1
# https://hub.docker.com/layers/library/alpine/3.19.1/images/sha256-6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0?context=explore&tab=vulnerabilities
# use as builder image to pull in required deps
FROM alpine@sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0 AS builder

LABEL org.opencontainers.image.source="https://github.com/alpinelinux/docker-alpine"

ENV PYTHONUNBUFFERED=1

COPY requirements-docker.txt /tmp/requirements-docker.txt

RUN \
    apk update && \
    apk add --no-cache python3 postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc zlib-dev python3-dev musl-dev postgresql-dev && \
    python3 -m venv /opt/venv && \
    source /opt/venv/bin/activate && \
    python3 -m ensurepip && \
    pip install --no-cache --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements-docker.txt --no-cache-dir && \
    apk --purge del .build-deps && \
    rm -rf /tmp/* && \
    rm -f /var/cache/apk/*

# latest hash as of 25 JAN 2024 - Alpine 3.19.1
# https://hub.docker.com/layers/library/alpine/3.19.1/images/sha256-6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0?context=explore&tab=vulnerabilities
FROM alpine@sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0 as electriceye

COPY --from=builder /usr /usr

# NOTE: This will copy all application files and auditors to the container
# IMPORTANT: ADD YOUR TOML CONFIGURATIONS BEFORE YOU BUILD THIS! - or use docker run -v options to override

COPY ./eeauditor /eeauditor

RUN \
    apk add --no-cache bash nmap py3-pandas py3-matplotlib && \
    rm -f /var/cache/apk/*

LABEL \ 
    maintainer="opensource@electriceye.cloud" \
    version="3.0" \
    license="Apache-2.0" \
    description="ElectricEye is a multi-cloud, multi-SaaS Python CLI tool for Asset Management, Security Posture Management & Attack Surface Monitoring supporting 100s of services and evaluations to harden your CSP & SaaS environments with controls mapped to over 20 industry, regulatory, and best practice controls frameworks."

# Create a System Group and User for ElectricEye so we don't run as root
RUN \
    addgroup -S eeuser && \ 
    adduser -S -G eeuser eeuser && \
    chown eeuser /eeauditor && \
    chown eeuser /eeauditor/* && \
    chgrp eeuser /eeauditor && \
    chown -R eeuser:eeuser /eeauditor/* && \
    chown -R eeuser:eeuser /eeauditor

USER eeuser

# IMPORTANT: Modify the controller.py command to run other clouds/SaaS or modify outputs
CMD ["sh", "-c", "source /opt/venv/bin/activate && python3 eeauditor/controller.py"]