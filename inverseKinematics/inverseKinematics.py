import math
# from adafruit_motor import stepper
# from adafruit_servokit import ServoKit

#IMPORTANT need to normalize servo values to current arm resting position BEFORE execution

# Constants and variables
theta1 = 0
theta2 = 0
delta = 0
theta3 = 0
psi = 180  # Desired gripper orientation
wrist_pin = 2

# Initialize stepper motors and servo
# kit = ServoKit(channels=16)
# kit.servo[wrist_pin].angle = 0


# Functions
def inverse_kinematics(x, y, z):
    global theta1, theta2, theta3, delta

    pi = math.pi
    j1 = 127  # Length J1 in mm
    j2 = 120  # Length J2 in mm

    # Z move
    delta = math.atan(z / x)  # Angle base needs to move
    delta = math.degrees(delta)  # Radians to degrees

    x2 = math.sqrt(z**2 + x**2) - x
    if z != 0:
        x += x2

    theta2 = -math.acos((x**2 + y**2 - j1**2 - j2**2) / (2 * j1 * j2))

    theta1 = math.atan(y / x) + math.atan((j2 * math.sin(theta2)) / (j1 + j2 * math.cos(theta2)))

    # Convert to degrees
    theta2 = math.degrees(theta2)
    theta1 = math.degrees(theta1)

    # Adjust angles
    if theta2 < 0 and theta1 > 0:
        if theta1 < 90:
            theta1 += (180 - (theta1 * 2))
            theta2 *= -1
        elif theta1 > 90:
            theta1 = theta1 - (2 * (theta1 - 90))
            theta2 *= -1
    elif theta1 < 0 and theta2 < 0:
        theta1 *= -1
        theta2 *= -1

    # Gripper orientation
    theta3 = psi - theta2 - (90 - theta1)
    theta3 = 180 - theta3

# Main loop
def main_loop():
    global x, y, z, theta1, theta2, theta3, delta

    # Set initial position
    x = 170.5
    y = 168
    z = 0

    inverse_kinematics(x, y, z)

    # Calculate and move steppers
    if theta1 > 90:
        print(f"shoulder angle: {(180 - theta1)}")
    else:
        print(f"shoulder angle: {(theta1)}")


    print(f"elbow: {theta2}")
    print(f"base_stepper angle: {delta}")

    if theta3 > 0:
        print(f"wrist servo angle: {theta3 * 0.666667}")


if __name__ == "__main__":
    main_loop()
