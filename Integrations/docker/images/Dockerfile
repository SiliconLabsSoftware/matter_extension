
ARG VERSION=131
FROM ghcr.io/project-chip/chip-build:${VERSION} as build
LABEL org.opencontainers.image.source https://github.com/project-chip/connectedhomeip

# Requirements to clone SDKs in temporary container
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    git \
    git-lfs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    && : # last line


# Download Simplicity SDK v2024.12.1 (da661283f3)
RUN wget https://github.com/SiliconLabs/simplicity_sdk/releases/download/v2024.12.1-0/simplicity-sdk.zip -O /tmp/simplicity_sdk.zip \
    && unzip /tmp/simplicity_sdk.zip -d /tmp/simplicity_sdk \
    && rm -rf /tmp/simplicity_sdk.zip \
    # Deleting files that are not needed to save space
    && rm -rf /tmp/simplicity_sdk/protocol/flex /tmp/simplicity_sdk/protocol/z-wave /tmp/simplicity_sdk/protocol/wisun \
    && find /tmp/simplicity_sdk/protocol/openthread -name "*efr32mg21*" -delete \
    && : # last line

# Clone WiSeConnect Wi-Fi and Bluetooth Software 2.11.4 (bf6b600)
RUN git clone --depth=1 --single-branch --branch=2.11.4 https://github.com/SiliconLabs/wiseconnect-wifi-bt-sdk.git /tmp/wiseconnect-wifi-bt-sdk && \
    cd /tmp/wiseconnect-wifi-bt-sdk && \
    rm -rf .git \
    && : # last line

# Clone WiSeConnect SDK v3.4.1 (f675628e)
RUN git clone --depth=1 --single-branch --branch=v3.4.1 https://github.com/SiliconLabs/wiseconnect.git /tmp/wifi_sdk && \
    cd /tmp/wifi_sdk && \
    rm -rf .git \
    && : # last line

# SLC-cli install
# TODO: figure out a way to make this a fixed version. Currently a moving target.
RUN wget https://www.silabs.com/documents/login/software/slc_cli_linux.zip && \
    unzip ./slc_cli_linux.zip -d /tmp && \
    rm ./slc_cli_linux.zip \
    && : # last line

# TODO: figure out a way to make this a fixed version. Currently a moving target.
RUN wget https://www.silabs.com/documents/public/software/SimplicityCommander-Linux.zip && \
    unzip ./SimplicityCommander-Linux.zip -d /tmp && \
    rm ./SimplicityCommander-Linux.zip && \
    FILE=$(find /tmp -name "*Commander_linux_x86_64*") && \
    if [ -n "$FILE" ]; then \
        echo "$FILE" && \
        tar -xjvf "$FILE" -C /tmp; \
    else \
        echo "File not found"; \
    fi && \
    : # last line

# Final SDK container for compiling using Silabs SDK
FROM ghcr.io/project-chip/chip-build:${VERSION}

ADD requirements.txt /tmp/requirements.txt

# Install Zip
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    git \
    git-lfs \
    zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    && : # last line

# GNU ARM Embedded toolchain, cross compiler for various platform builds
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    gcc-arm-none-eabi \
    binutils-arm-none-eabi \
    openjdk-17-jdk-headless \
    ccache \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    # Install Python Packages
    && pip3 install --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && : # last line

# Keep GSDK_ROOT name until rename transition to SISDK is completed
ENV GSDK_ROOT=/opt/silabs/simplicity_sdk/
ENV SISDK_ROOT=/opt/silabs/simplicity_sdk/
ENV WISECONNECT_SDK_ROOT=/opt/silabs/wiseconnect-wifi-bt-sdk/
ENV WIFI_SDK_ROOT=${SISDK_ROOT}/extension/wiseconnect
ENV PATH="${PATH}:/opt/silabs/slc_cli/"
ENV POST_BUILD_EXE=/opt/silabs/simplicity-commander/commander/commander

COPY --from=build /tmp/simplicity_sdk ${SISDK_ROOT}
COPY --from=build /tmp/wiseconnect-wifi-bt-sdk/ ${WISECONNECT_SDK_ROOT}
COPY --from=build /tmp/wifi_sdk ${WIFI_SDK_ROOT}
COPY --from=build /tmp/slc_cli /opt/silabs/slc_cli
COPY --from=build /tmp/SimplicityCommander-Linux /opt/silabs/simplicity-commander
