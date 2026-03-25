# ArionX: Autonomous Flight Stack

## 🚀 Mission Overview
Autonomous navigation in GPS-denied environments (Mars-like scenarios). This logic performs a fully autonomous mission: **Takeoff -> Hover (3m) -> Land.**

## 🛠️ System Architecture
- **Brain:** Jetson Orin Nano (ROS 2 Humble)
- **Nervous System:** Micro-XRCE-DDS Agent
- **Muscle:** Pixhawk 6C Mini (PX4 Autopilot)
- **Vision:** RealSense D435i + Waveshare Stereo Cam

## 📂 File Structure
- `takeoff.py`: Finite State Machine managing 3D flight setpoints.
- `setup_env.sh`: Script to resolve Conda/System path conflicts.

## ⚙️ How to Run (Simulation)
1. **Sanitize Terminal:** `source setup_env.sh`
2. **Launch PX4 SITL:** 
   ```bash
   cd ~/PX4-Autopilot && export GZ_VERSION=fortress && make px4_sitl_default gz_x500

       Configure PX4 (in pxh terminal):
    param set NAV_DLL_ACT 0
    param set EKF2_HGT_MODE 2
    param set EKF2_AID_MASK 1

    Start Agent: MicroXRCEAgent udp4 -p 8888

    Run Mission: python3 takeoff.py
