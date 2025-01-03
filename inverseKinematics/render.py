import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def calculate_3d_joint_positions(length1, length2, base_angle, theta1, theta2):
    """
    Calculate the 3D positions of the joints and end-effector.
    """
    base_angle_rad = np.radians(base_angle)
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)

    base = (0, 0, 0)

    joint1_x = length1 * np.cos(theta1_rad) * np.cos(base_angle_rad)
    joint1_y = length1 * np.cos(theta1_rad) * np.sin(base_angle_rad)
    joint1_z = length1 * np.sin(theta1_rad)
    joint1 = (joint1_x, joint1_y, joint1_z)

    end_effector_x = joint1_x + length2 * np.cos(theta1_rad + theta2_rad) * np.cos(base_angle_rad)
    end_effector_y = joint1_y + length2 * np.cos(theta1_rad + theta2_rad) * np.sin(base_angle_rad)
    end_effector_z = joint1_z + length2 * np.sin(theta1_rad + theta2_rad)
    end_effector = (end_effector_x, end_effector_y, end_effector_z)

    return base, joint1, end_effector

def visualize_robot_arm(base, joint1, end_effector):
    """
    Visualize the robotic arm in 3D space with three preset views.
    """
    x_coords = [base[0], joint1[0], end_effector[0]]
    y_coords = [base[1], joint1[1], end_effector[1]]
    z_coords = [base[2], joint1[2], end_effector[2]]

    # Create a figure with 3 subplots for different views
    fig = plt.figure(figsize=(15, 5))

    # Default perspective view
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot(x_coords, y_coords, z_coords, marker='o', label='Robot Arm')
    ax1.set_title("Default Perspective")
    ax1.set_xlabel("X-axis")
    ax1.set_ylabel("Y-axis")
    ax1.set_zlabel("Z-axis")
    ax1.view_init(elev=30, azim=45)

    # Side view
    ax2 = fig.add_subplot(132, projection='3d')
    ax2.plot(x_coords, y_coords, z_coords, marker='o', label='Robot Arm')
    ax2.set_title("Side View")
    ax2.set_xlabel("X-axis")
    ax2.set_ylabel("Y-axis")
    ax2.set_zlabel("Z-axis")
    ax2.view_init(elev=0, azim=0)

    # Top view
    ax3 = fig.add_subplot(133, projection='3d')
    ax3.plot(x_coords, y_coords, z_coords, marker='o', label='Robot Arm')
    ax3.set_title("Top View")
    ax3.set_xlabel("X-axis")
    ax3.set_ylabel("Y-axis")
    ax3.set_zlabel("Z-axis")
    ax3.view_init(elev=90, azim=-90)

    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()

def main():
    length1 = 127
    length2 = 120

    base_angle = float(input("Enter base rotation angle (degrees): "))
    theta1 = float(input("Enter angle for Joint 1 (degrees): "))
    theta2 = float(input("Enter angle for Joint 2 (degrees): "))

    base, joint1, end_effector = calculate_3d_joint_positions(length1, length2, base_angle, theta1, theta2)

    print(f"Base: {base}")
    print(f"Joint 1: {joint1}")
    print(f"End Effector: {end_effector}")

    # Visualize all three views
    visualize_robot_arm(base, joint1, end_effector)

if __name__ == "__main__":
    main()
