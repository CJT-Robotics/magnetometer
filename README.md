# Yahboom Magnetometer ROS Node

This package provides a ROS1 node for reading raw magnetometer data from a Yahboom IMU via serial interface, performing a simple calibration, and publishing the data as a `sensor_msgs/MagneticField` topic.

## Requirements

Install dependencies:

```bash
sudo apt install python3-serial
```

## Installation

1. Clone this package:

```bash
cd ~/catkin_ws/src
git clone git@github.com:CJT-Robotics/magnetometer.git
sudo chmod +x ~/catkin_ws/src/magnetometer/src/mag_pub.py
```

2. Build the workspace:

```bash
cd ~/catkin_ws
catkin build
source devel/setup.bash
```

## udev Rule

To ensure the magnetometer is always accessible under a fixed device name, create a udev rule.

### 1. Find your USB device

```bash
lsusb
```

Example output:

```
Bus 001 Device 014: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
```

* `1a86` = idVendor
* `7523` = idProduct

---

### 2. Create udev rule

```bash
sudo nano /etc/udev/rules.d/99-magnetometer.rules
```

Add:

```bash
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="mag_yahboom", MODE="0666"
```

### 3. Reload rules

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the device. Check:

```bash
ls -l /dev/mag_yahboom
```

## Usage

Run the node:

```bash
rosrun magnetometer mag_pub.py
```

Published topic:

```
{namesapce}/imu/mag (sensor_msgs/MagneticField)
```

## Calibration

On startup, the node performs a calibration for a few seconds.

## Data Processing

* Raw values are read from serial
* Packet structure is validated via checksum
* Magnetometer values are extracted
* Offset is subtracted
* Values are scaled

## Notes

* Ensure correct permissions (`MODE="0666"`) or add your user to `dialout`
* If no data appears, verify:
  * correct baud rate (115200)
  * correct device path
  * serial cable / adapter
