#!/bin/bash
# ArionX Environment Sanitizer
# Force Python 3.10 and System Paths to avoid Conda conflicts
export PATH=/usr/bin:/usr/local/bin:/bin:/sbin:$PATH
source /opt/ros/humble/setup.bash
echo "Environment Sanitized: Python 3.10 + ROS 2 Humble Active"
