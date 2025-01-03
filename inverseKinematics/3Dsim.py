import numpy as np

def calculate_3d_joint_positions(length1, length2, base_angle, theta1, theta2):
    """
    Calculate the 3D positions of the joints and end-effector.
    
    :param length1: Length of the first segment of the arm
    :param length2: Length of the second segment of the arm
    :param base_angle: Rotation angle of the base (in degrees)
    :param theta1: Angle of the first joint (in degrees)
    :param theta2: Angle of the second joint (in degrees)
    :return: Coordinates of the base, first joint, and end-effector in 3D space
    """
    # Convert angles to radians
    base_angle_rad = np.radians(base_angle)
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)

    # Base position (assume it's at origin)
    base = (0, 0, 0)

    # Position of the first joint in 3D
    joint1_x = length1 * np.cos(theta1_rad) * np.cos(base_angle_rad)
    joint1_y = length1 * np.cos(theta1_rad) * np.sin(base_angle_rad)
    joint1_z = length1 * np.sin(theta1_rad)
    joint1 = (joint1_x, joint1_y, joint1_z)

    # Position of the end-effector in 3D
    end_effector_x = joint1_x + length2 * np.cos(theta1_rad + theta2_rad) * np.cos(base_angle_rad)
    end_effector_z = joint1_y + length2 * np.cos(theta1_rad + theta2_rad) * np.sin(base_angle_rad)
    end_effector_y = joint1_z + length2 * np.sin(theta1_rad + theta2_rad)
    end_effector = (end_effector_x, end_effector_y, end_effector_z)

    return base, joint1, end_effector

def main():
    # Arm segment lengths
    length1 = 127  # Length of the first segment
    length2 = 120  # Length of the second segment

    # Input joint angles
    base_angle = float(input("Enter base rotation angle (degrees): "))
    theta1 = float(input("Enter angle for Joint 1 (degrees): "))
    theta2 = float(input("Enter angle for Joint 2 (degrees): "))

    # Calculate positions
    base, joint1, end_effector = calculate_3d_joint_positions(length1, length2, base_angle, theta1, theta2)

    # Display positions
    print(f"Base: {base}")
    # print(f"Joint 1: {joint1}")
    print(f"End Effector: {end_effector}")

if __name__ == "__main__":
    main()