# Cloud Deployment Guide (AWS EC2 + Isaac Sim)

This guide covers deploying the Teleoperation System and Isaac Sim on an AWS EC2 instance with GPU support.

## 1. Prerequisites

### AWS EC2 Instance
- **Instance Type**: `g4dn.2xlarge` (minimum) or `g5.4xlarge` (recommended).
- **AMI**: Ubuntu 22.04 LTS or 24.04 LTS.
- **Disk Size**: At least 100GB (Isaac Sim is large).
- **Security Group**:
  - Inbound:
    - `SSH (22)`: Your IP.
    - `TCP (8000)`: Your IP (or 0.0.0.0/0).

### Local Machine
- SSH Key (`.pem` file) for the EC2 instance.
- This codebase.

## 2. Deployment Steps

We have automated scripts to handle the deployment.

### Step 1: Upload Code to EC2

From your local machine, run the deployment script:

```bash
cd deployment
chmod +x deploy_remote.sh

# Replace with your EC2 IP and Key Path
EC2_HOST=1.2.3.4 SSH_KEY=~/.ssh/my-key.pem ./deploy_remote.sh
```

This will upload the code and setup scripts to `~/teleop_system` on the EC2 instance.

### Step 2: Setup GPU Environment (On EC2)

SSH into your EC2 instance:
```bash
ssh -i ~/.ssh/my-key.pem ubuntu@1.2.3.4
```

Run the GPU setup script. This installs NVIDIA Drivers, Docker, and the NVIDIA Container Toolkit.

```bash
./aws_gpu_setup.sh
```

**IMPORTANT**: If the script installs NVIDIA drivers, it will ask you to reboot.
```bash
sudo reboot
```

After reboot, SSH back in and verify the GPU setup:
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```
If both commands show your GPU, you are ready.

### Step 3: Start the Full System

Run the start script to launch the Teleop Server and Isaac Sim (headless):

```bash
cd ~/teleop_system/deployment
./start_full_system.sh
```

This will:
1.  Pull the Isaac Sim Docker image (approx. 10GB+).
2.  Build the Teleop Server.
3.  Start both containers.

## 3. Verification

### Check Status
```bash
docker ps
docker logs -f teleop-server
docker logs -f isaac-sim
```

### Access API
Open your browser to: `http://<EC2_IP>:8000/docs`

### Control the Robot
Run the client on your **local machine**:

```bash
# Install dependencies
pip install -r client/requirements.txt

# Run client
python client/keyboard_client.py --server http://<EC2_IP>:8000
```

- Press `W/S/A/D` to move the robot.
- You should see the coordinates changing in the server logs.
- If you have a way to view the Isaac Sim stream (e.g. via Omniverse Streaming Client), you can connect to the EC2 IP (if configured). By default, this setup runs headless for control logic verification.

## 4. Troubleshooting

- **Isaac Sim not starting**: Check `docker logs isaac-sim`. Ensure you are using a GPU instance.
- **Docker Permission Denied**: Run `newgrp docker` or log out and log back in.
- **Disk Full**: Run `docker system prune -a` or increase EBS volume size.
