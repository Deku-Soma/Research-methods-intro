FROM osrf/ros:humble-desktop

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV DISPLAY=:1
ENV VNC_PORT=5901
ENV NO_VNC_PORT=6080

# Install system dependencies, Gazebo, desktop tools, and noVNC for browser GUI
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-vcstool \
    # Gazebo Classic and ROS 2 plugins
    gazebo \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    # GUI and Virtual Display for macOS browser access
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    # Mathematics, optimization, and plotting
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    # Utilities
    curl \
    wget \
    nano \
    sudo \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install python libraries for MPC and robotics
RUN pip3 install --no-cache-dir \
    osqp \
    transforms3d \
    pandas

# Set up non-root user for safe workspace usage
ARG USERNAME=rosuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash 2>/dev/null || true && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create workspace directory
WORKDIR /ros2_ws

# Setup entrypoint and startup scripts
COPY entrypoint.sh /entrypoint.sh
COPY start_novnc.sh /start_novnc.sh
RUN sed -i 's/\r$//' /entrypoint.sh /start_novnc.sh && \
    chmod +x /entrypoint.sh /start_novnc.sh

USER $USERNAME

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
