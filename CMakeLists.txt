cmake_minimum_required(VERSION 3.0.2)
project(magnetometer)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  rospy
  sensor_msgs
  std_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  src/mag_pub.py 
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)