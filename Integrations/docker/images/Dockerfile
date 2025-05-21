
ARG VERSION=latest
FROM ghcr.io/project-chip/chip-build:${VERSION} AS build
LABEL org.opencontainers.image.source https://github.com/project-chip/connectedhomeip

# Requirements to clone SDKs in temporary container
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    git \
    git-lfs \
    zip \
    tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    && : # last line

# Download Simplicity SDK v2024.12.1 (da661283f3)
RUN wget https://github.com/SiliconLabs/simplicity_sdk/releases/download/v2024.12.1-0/simplicity-sdk.zip -O /tmp/simplicity_sdk.zip \
    && unzip /tmp/simplicity_sdk.zip -d /tmp/simplicity_sdk \
    && rm -rf /tmp/simplicity_sdk.zip \
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
RUN wget https://www.silabs.com/documents/login/software/slc_cli_linux.zip && \
    unzip ./slc_cli_linux.zip -d /tmp && \
    rm ./slc_cli_linux.zip \
    && : # last line

RUN wget https://www.silabs.com/documents/public/software/SimplicityCommander-Linux.zip && \
    unzip ./SimplicityCommander-Linux.zip -d /tmp/simplicity-commander && \
    rm ./SimplicityCommander-Linux.zip && \
    FILE=$(find /tmp/simplicity-commander -name "*Commander_linux_x86_64*") && \
    if [ -n "$FILE" ]; then \
        tar -xjvf "$FILE" -C /tmp/simplicity-commander; \
    else \
        echo "File not found"; \
    fi && \
    : # last line

# Download ARM GCC toolchain v10.3-2021.07 (aarch64-none-eabi)
RUN wget https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz -O /tmp/arm-gnu-toolchain.tar.xz \
    && tar -xJvf /tmp/arm-gnu-toolchain.tar.xz -C /tmp \
    && rm -rf /tmp/arm-gnu-toolchain.tar.xz \
    && : # last line

# Install java
RUN wget https://corretto.aws/downloads/resources/17.0.8.8.1/amazon-corretto-17.0.8.8.1-linux-x64.tar.gz -O /tmp/java.tar.gz \
    && tar -xzf /tmp/java.tar.gz -C /tmp \
    && rm /tmp/java.tar.gz \
    && ls /tmp \
    && : # last line

# Final SDK container for compiling using Silabs SDK
FROM ghcr.io/project-chip/chip-build:${VERSION}

ADD requirements.txt /tmp/requirements.txt

# Keep GSDK_ROOT name until rename transition to SISDK is completed
ENV GSDK_ROOT=/opt/silabs/simplicity_sdk/
ENV SISDK_ROOT=/opt/silabs/simplicity_sdk/
ENV WISECONNECT_SDK_ROOT=/opt/silabs/wiseconnect-wifi-bt-sdk/
ENV WISECONNECT3_DIR=${SISDK_ROOT}/extension/wiseconnect
ENV ARM_GCC_DIR=/opt/arm-gcc
ENV JAVA17_HOME=/opt/silabs/amazon-corretto-17.0.8.8.1-linux-x64
ENV PATH="${PATH}:/opt/silabs/slc_cli/"
ENV PATH="${PATH}:${ARM_GCC_DIR}/bin"
ENV PATH="${PATH}:${JAVA17_HOME}/bin"
ENV POST_BUILD_EXE=/opt/silabs/simplicity-commander/commander/commander


COPY --from=build /tmp/simplicity_sdk ${SISDK_ROOT}
COPY --from=build /tmp/wiseconnect-wifi-bt-sdk/ ${WISECONNECT_SDK_ROOT}
COPY --from=build /tmp/wifi_sdk ${WISECONNECT3_DIR}
COPY --from=build /tmp/slc_cli /opt/silabs/slc_cli
COPY --from=build /tmp/SimplicityCommander-Linux /opt/silabs/simplicity-commander
COPY --from=build /tmp/arm-gnu-toolchain-* ${ARM_GCC_DIR}
COPY --from=build /tmp/amazon-corretto-17.0.8.8.1-linux-x64 ${JAVA17_HOME}

RUN ls /opt/silabs
RUN ls /opt/silabs/slc_cli
RUN ls ${ARM_GCC_DIR}
RUN ls /opt/silabs/simplicity-commander
RUN ls ${JAVA17_HOME}
RUN echo ${PATH}