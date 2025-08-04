# HOLOSPOOKY - cool stuff to do with your old Cozmo!! :3

import pycozmo
import pygame
import cv2
import numpy as np

def deploy():
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    if joystick.get_init():
        print("Controller connected!")
        buttonpress = True
    else:
        print("Controller not connected. Try checking Bluetooth connection, wired connection, battery life, controller functionality, or controller brand (ONLY PLAYSTATION/XBOX WORKS WITH HOLOSPOOKY)")
        return  # Exit if no controller is detected

    # Last image, received from the robot.
    last_im = None

    def on_camera_image(cli, new_im):
        """ Handle new images, coming from the robot. """
        nonlocal last_im  # Fix variable scope issue
        last_im = new_im

    with pycozmo.connect(enable_procedural_face=False) as cli:
        # Raise head.
        angle = (pycozmo.robot.MAX_HEAD_ANGLE.radians - pycozmo.robot.MIN_HEAD_ANGLE.radians) / 2.0
        cli.set_head_angle(angle)

        # Register to receive new camera images.
        cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

        # Enable camera.
        cli.enable_camera(enable=True, color=True)

        # Run at Cozmo’s native camera FPS (14 FPS).
        timer = pycozmo.util.FPSTimer(14)
    
        while True:
            if last_im:
                # Convert PIL image to OpenCV format
                opencv_image = np.array(last_im)  # Convert PIL Image to numpy array
                opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
                # Set the OpenCV window to fullscreen
                cv2.namedWindow("Cozmo Camera", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Cozmo Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                # Show the image in a window
                cv2.imshow("Cozmo Camera", opencv_image)

            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            timer.sleep()

            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:  # JOYSTICKS
                    if event.axis == 1:  # LEFT JOYSTICK
                        if event.value < -0.5:
                            cli.set_head_angle(angle=100, accel=100)
                        if event.value > 0.5:
                            cli.set_head_angle(angle=-100, accel=100)
                    if event.axis == 0:
                        cli.set_head_angle(angle=0, accel=100)

                    if event.axis == 3:  # RIGHT JOYSTICK
                        if event.value < -0.5:
                            cli.set_lift_height(height=100, accel=100)
                        if event.value > 0.5:
                            cli.set_lift_height(height=-100, accel=100)
                            
                if buttonpress:  # ARROW BUTTONS
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 11:
                            cli.drive_wheels(lwheel_speed=1000, rwheel_speed=1000)
                        if event.button == 12:
                            cli.drive_wheels(lwheel_speed=-1000, rwheel_speed=-1000)
                        if event.button == 13:
                            cli.drive_wheels(lwheel_speed=-1000, rwheel_speed=1000)
                        if event.button == 14:
                            cli.drive_wheels(lwheel_speed=1000, rwheel_speed=-1000)

                    if event.type == pygame.JOYBUTTONUP:
                        if 11 <= event.button <= 14:
                            cli.drive_wheels(lwheel_speed=0, rwheel_speed=0)

        # Cleanup OpenCV window when finished
        cv2.destroyAllWindows()

def joystick_test():
    # Run this program while connected to your controller to test controls
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    if joystick.get_init():
        print("Controller connected! [TEST MODE] Begin testing")
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                print("Axis:", event.axis, "Value:", event.value)
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Button:", event.button, "pressed")
            elif event.type == pygame.JOYBUTTONUP:
                print("Button:", event.button, "released")