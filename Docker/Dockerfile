ARG VERSION=latest
FROM ghcr.io/project-chip/chip-build:${VERSION} as build
LABEL org.opencontainers.image.source https://github.com/SiliconLabsSoftware/matter_extension

# Requirements to clone SDKs in temporary container
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    git \
    git-lfs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    && : # last line

# Install Arm GNU Toolchain
RUN wget -O gcc.tar.xz "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz?rev=7bd049b7a3034e64885fa1a71c12f91d&hash=732D909FA8F68C0E1D0D17D08E057619" \
    && tar -xJf ./gcc.tar.xz -C /tmp \
    && rm ./gcc.tar.xz \
    && : # last line

# Download Simplicity Commander
RUN wget https://www.silabs.com/documents/login/software/SimplicityCommander-Linux.zip \
    && unzip ./SimplicityCommander-Linux.zip -d /tmp \
    && find /tmp/SimplicityCommander-Linux -name 'Commander_linux_x86_64*' -exec tar -xvjf {} -C /tmp/SimplicityCommander-Linux \; \
    && rm ./SimplicityCommander-Linux.zip \
    && : # last line

# Download Simplicity SDK v2024.6.1 (a1a37fa)
RUN wget https://github.com/SiliconLabs/simplicity_sdk/releases/download/v2024.6.2/gecko-sdk.zip -O /tmp/simplicity_sdk.zip \
    && unzip /tmp/simplicity_sdk.zip -d /tmp/simplicity_sdk \
    && rm -rf /tmp/simplicity_sdk.zip \
    && rm -rf /tmp/simplicity_sdk/protocol/flex /tmp/simplicity_sdk/protocol/z-wave /tmp/simplicity_sdk/protocol/wisun \
    && find /tmp/simplicity_sdk/protocol/openthread -name "*efr32mg21*" -delete \
    && : # last line

# Clone WiSeConnect Wi-Fi and Bluetooth Software 2.10.0 (f94b83d)
RUN git clone --depth=1 --single-branch --branch=2.10.0 https://github.com/SiliconLabs/wiseconnect-wifi-bt-sdk.git /tmp/wiseconnect-wifi-bt-sdk \
    && cd /tmp/wiseconnect-wifi-bt-sdk \
    && rm -rf .git \
    && : # last line

# Clone WiSeConnect SDK v3.3.1 (841ea3f)
RUN git clone --depth=1 --single-branch --branch=v3.3.1 https://github.com/SiliconLabs/wiseconnect.git /tmp/wifi_sdk \
    && cd /tmp/wifi_sdk \
    && rm -rf .git \
    && : # last line

# SLC-cli install
RUN wget https://www.silabs.com/documents/login/software/slc_cli_linux.zip \
    && unzip ./slc_cli_linux.zip -d /tmp \
    && rm ./slc_cli_linux.zip \
    && : # last line

# Final SDK container for compiling using Silabs SDK
FROM ghcr.io/project-chip/chip-build:${VERSION}

ADD Docker/requirements.txt /tmp/requirements.txt

# Cross compiler for various platform builds
RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -fy --no-install-recommends \
    openjdk-17-jdk-headless \
    ccache \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/ \
    # Install Python Packages
    && pip3 install --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && : # last line

ENV SISDK_ROOT=/opt/silabs/simplicity_sdk/
ENV WISECONNECT_SDK_ROOT=/opt/silabs/wiseconnect-wifi-bt-sdk/
ENV WIFI_SDK_ROOT=${SISDK_ROOT}/extension/wiseconnect
ENV POST_BUILD_EXE="/opt/silabs/SimplicityCommander/commander/commander"
ENV PATH="${PATH}:/opt/silabs/slc_cli/"
ENV ARM_GCC_DIR="/opt/silabs/arm-gcc-dir/"
ENV PATH="${PATH}:${ARM_GCC_DIR}/bin"

COPY --from=build /tmp/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi ${ARM_GCC_DIR}
COPY --from=build /tmp/SimplicityCommander-Linux /opt/silabs/SimplicityCommander/
COPY --from=build /tmp/simplicity_sdk ${SISDK_ROOT}
COPY --from=build /tmp/wiseconnect-wifi-bt-sdk/ ${WISECONNECT_SDK_ROOT}
COPY --from=build /tmp/wifi_sdk ${WIFI_SDK_ROOT}
COPY --from=build /tmp/slc_cli /opt/silabs/slc_cli