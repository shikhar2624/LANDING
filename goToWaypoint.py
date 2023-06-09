from dronekit import connect, VehicleMode, LocationGlobalRelative
import logging
import time

import atexit   ##it provides a way to run another python script within python script
import subprocess 

# Define the function to run the other Python script
def run_aruco_script():
    command = ['python', '/home/shikhar/TechEagle/LANDING/main_final.py']
    subprocess.call(command)

# Register the function to be called at exit
# The main_final.py will be executed when the program exits
atexit.register(run_aruco_script)

## connecting to drone (in this case sitl)
vehicle= connect('udp::14550',wait_ready=True)

def arm_and_takeoff(altitude):
    while not vehicle.is_armable:
        print("waiting to be armable")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")   ## setting guided mode of drone
    vehicle.armed = True

    while vehicle.armed: time.sleep(1)

    print("Taking Off")
    vehicle.simple_takeoff(altitude)

    while True:
        v_alt = vehicle.location.global_relative_frame.alt
        print(">> Altitude = %.1f m" % v_alt)
        if v_alt >= altitude - 1.0:
            print("Target altitude reached")
            break
        time.sleep(1)


arm_and_takeoff(3)

point1 = LocationGlobalRelative(-35.3632689,149.1652301, 1)
vehicle.simple_goto(point1)

time.sleep(6)