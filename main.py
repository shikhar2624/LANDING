import time
import math
import argparse
import cv2
from dronekit import connect, VehicleMode
from pymavlink import mavutil
from AP.cpp import *
import logging
from flask_main import generate_frames,RegisterGetFramesFunc

## logging part

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


## precise landing class
class precise_landing():
    def __init__(self,vehicle,aruco_tracker):
        self.vehicle=vehicle     ## defining drone vehicle
        self.ArucoTracker=aruco_tracker   
        self.kp_x=0.001
        self.kp_y=0.001
        self.vxBound=1     ##bound for velocity in x
        self.vyBound=1     ##bound for velocity in y

        ##threshold in coordinates
        self.xMax=20
        self.yMax=20

        ##flag for landing
        self.land=0
        self.land2=0

        ## defining camera object
        self.cap = cv2.VideoCapture(0)

    def arm_and_takeoff(self,altitude):
        ''' function for takeoff the drone at given altitude '''

        while not self.vehicle.is_armable:
            print("waiting to be armable")
            time.sleep(1)

        print("Arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")   ## setting guided mode of drone
        self.vehicle.armed = True

        while not self.vehicle.armed: time.sleep(1)

        print("Taking Off")
        self.vehicle.simple_takeoff(altitude)

        while True:
            v_alt = self.vehicle.location.global_relative_frame.alt
            print(">> Altitude = %.1f m" % v_alt)
            if v_alt >= altitude - 1.0:
                print("Target altitude reached")
                break
            time.sleep(1)

    def velocity_calculate(self,x,y):
        ''' function for calculating velocity '''

        ##applying pid control on x and y velocity
        vx=self.kp_x*y
        vy=self.kp_y*x

        ## bounding the x velocity
        if vx>=self.vxBound:
            vx=self.vxBound
        elif vx<=-self.vxBound:
            vx=-self.vxBound

        ## bounding the y velocity
        if vy>=self.vyBound:
            vy=self.vyBound
        elif vy<=-self.vyBound:
            vy=-self.vyBound

        ## applying threshold
        if abs(x)<self.xMax:
            vy=0

        if abs(y)<self.yMax:
            vx=0
        
        ## landing condition
        if abs(x)<self.xMax and abs(y)<self.yMax:
            self.land=1    ##landing enabled
        else:
            self.land=0    ##landing disabled


        return -vx,vy

    def goto_position_target_local_ned(self,vx,vy,vz):
        """ 
        Send SET_POSITION_TARGET_LOCAL_NED command to request the vehicle fly to a specified 
        location in the North, East, Down frame.
        It is important to remember that in this frame, positive altitudes are entered as negative 
        "Down" values. So if down is "10", this will be 10 metres below the home altitude.
        """
        
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            int(0b110111000111), # type_mask (only positions enabled)
            0,0,0, # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
            vx, vy, vz, # x, y, z velocity in m/s  (not used)
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
        
        # send command to vehicle
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()

    def finalloop(self):
        # print("Received an image")
        while True:

            ## reading frames
            ret, frame = self.cap.read()

            ## checking whether camera received image or not
            if ret:
                marker_found, x_cm, y_cm, z_cm = self.ArucoTracker.track(loop=False, frame=frame)
                
                if marker_found:
                    print('aruco detected')
                    
                    ##calculating velocity
                    vx,vy=self.velocity_calculate(x_cm,y_cm)
                    print(f'vx: {vx} | vy: {vy} | xcm: {x_cm} | ycm: {y_cm}')
                    if self.land==1 or self.land2==1:
                        self.land2=1  
                        print('landing to be started')
                        
                        ##land the drone
                        if self.vehicle.location.global_relative_frame.alt>=0.4:
                            print("landing drone with control in z axis")
                            # self.goto_position_target_local_ned(vx,vy,0.1)
                        else:
                            print("landing drone with mode LAND activated")
                            # self.vehicle.mode=VehicleMode("LAND")

                    else:
                        ##giving velocity to go towards aruco
                        print('moving towards aruco')  
                        # self.goto_position_target_local_ned(vx,vy,0)

                # elif  self.vehicle.location.global_relative_frame.alt>=0.95:
                else:
                    print('aruco not detected')
                    # self.goto_position_target_local_ned(0,0,0)  ##giving zero velocity commands
            else:
                print('Camera Frames Not Received')

def main():
    global aruco_tracker
    ##defining drone
    drone = connect('udp::14550',wait_ready=True)
    print('drone connected succesfully')

    ## defining camera callibration files
    calib_path = "AP/"
    camera_matrix = np.loadtxt(calib_path + 'cameraMatrix.txt', delimiter=',')
    camera_distortion = np.loadtxt(calib_path + 'cameraDistortion.txt', delimiter=',')



    ## defining aruco tracker
    aruco_tracker = ArucoSingleTracker(id_to_find=31, marker_size=100, show_video=True, camera_matrix=camera_matrix,
                                    camera_distortion=camera_distortion)

    RegisterGetFramesFunc(aruco_tracker.genFramesFromAruco)

    test=precise_landing(drone,aruco_tracker)

    ## takeoff drone to given altitude
    # test.arm_and_takeoff(1)
    test.finalloop()

if __name__ == '__main__':
    main()
