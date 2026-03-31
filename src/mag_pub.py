#!/usr/bin/env python3
import rospy
import serial
import struct
import time
from sensor_msgs.msg import MagneticField

def calibrate_mag(ser, duration=3):
    rospy.loginfo(f"Calibration {duration} secs")
    start_time = time.time()
    
    min_x, max_x = 32767, -32768
    min_y, max_y = 32767, -32768
    min_z, max_z = 32767, -32768

    while time.time() - start_time < duration:
        if ser.read(1) == b'\x7E':
            if ser.read(1) == b'\x23':
                length_byte = ser.read(1)
                if not length_byte: continue
                length = ord(length_byte)
                payload = ser.read(length - 3)
                
                if len(payload) >= 19 and payload[0] == 0x04:
                    mag_data = payload[13:19]
                    mx, my, mz = struct.unpack('<hhh', mag_data)
                    
                    min_x, max_x = min(min_x, mx), max(max_x, mx)
                    min_y, max_y = min(min_y, my), max(max_y, my)
                    min_z, max_z = min(min_z, mz), max(max_z, mz)
                    
                    remaining = int(duration - (time.time() - start_time))
                    print(f"Calibration {remaining}sec remaining", end='\r')

    offset_x = (max_x + min_x) / 2
    offset_y = (max_y + min_y) / 2
    offset_z = (max_z + min_z) / 2
    
    rospy.loginfo(f"\nCalibration completed")
    return offset_x, offset_y, offset_z

def yahboom_precise_node():
    
    rospy.init_node('yahboom_mag_node')

    port = rospy.get_param('~port', '/dev/mag_yahboom')
    baud = rospy.get_param('~baud', 115200)
    frame_id = rospy.get_param('~frame_id', 'mag_link')
    calib_duration = rospy.get_param('~calibration_duration', 3)

    pub = rospy.Publisher('imu/mag', MagneticField, queue_size=1)
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        rospy.logerr(f"Error: {e}")
        return

    off_x, off_y, off_z = calibrate_mag(ser, duration=calib_duration)
    
    msg = MagneticField()
    msg.header.frame_id = frame_id
    mag_scale = 800.0 / 32767.0

    while not rospy.is_shutdown():
        if ser.read(1) == b'\x7E':
            if ser.read(1) == b'\x23':
                length_byte = ser.read(1)
                if not length_byte: continue
                length = ord(length_byte)
                remaining_payload = ser.read(length - 3)
                
                if len(remaining_payload) < (length - 3): continue
                
                if (sum(b'\x7E\x23' + length_byte + remaining_payload[:-1]) & 0xFF) != remaining_payload[-1]:
                    continue

                if remaining_payload[0] == 0x04:
                    mag_data = remaining_payload[13:19]
                    mx, my, mz = struct.unpack('<hhh', mag_data)
                    
                    msg.header.stamp = rospy.Time.now()
                    msg.magnetic_field.x = (mx - off_x) * mag_scale
                    msg.magnetic_field.y = (my - off_y) * mag_scale
                    msg.magnetic_field.z = (mz - off_z) * mag_scale
                    
                    pub.publish(msg)

    ser.close()

if __name__ == '__main__':
    try:
        yahboom_precise_node()
    except rospy.ROSInterruptException:
        pass