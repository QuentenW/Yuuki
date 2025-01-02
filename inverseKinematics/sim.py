import matplotlib.pyplot as plt
import numpy as np

def calculate_joint_positions(length1, length2, theta1, theta2):
    """
    Calculate the positions of the joints and end-effector.
    
    :param length1: Length of the first segment of the arm
    :param length2: Length of the second segment of the arm
    :param theta1: Angle of the first joint (in degrees)
    :param theta2: Angle of the second joint (in degrees)
    :return: Coordinates of the base, first joint, and end-effector
    """
    # Convert angles to radians
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)

    # Base position (assume it's at origin)
    base = (0, 0)

    # Position of the first joint
    joint1 = (length1 * np.cos(theta1_rad), length1 * np.sin(theta1_rad))

    # Position of the end-effector
    end_effector = (
        joint1[0] + length2 * np.cos(theta1_rad + theta2_rad),
        joint1[1] + length2 * np.sin(theta1_rad + theta2_rad),
    )

    return base, joint1, end_effector

def plot_arm(base, joint1, end_effector):
    """
    Plot the arm in a 2D plane.
    
    :param base: Coordinates of the base
    :param joint1: Coordinates of the first joint
    :param end_effector: Coordinates of the end-effector
    """
    # Create the figure
    plt.figure(figsize=(6, 6))
    plt.plot([base[0], joint1[0]], [base[1], joint1[1]], 'o-', label="Segment 1")
    plt.plot([joint1[0], end_effector[0]], [joint1[1], end_effector[1]], 'o-', label="Segment 2")

    # Add labels
    plt.scatter(*base, color='red', label="Base")
    plt.scatter(*end_effector, color='green', label="End-Effector")
    plt.title("2D Robotic Arm Simulation")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid()
    plt.legend()
    plt.axis("equal")
    plt.show()

def main():
    # Arm segment lengths
    length1 = 127  # Length of the first segment
    length2 = 120  # Length of the second segment

    # Joint angles
    theta1 = float(input("Enter angle for Joint 1 (degrees): "))
    theta2 = float(input("Enter angle for Joint 2 (degrees): "))

    # Calculate positions
    base, joint1, end_effector = calculate_joint_positions(length1, length2, theta1, theta2)

    # Display positions
    print(f"Base: {base}")
    print(f"Joint 1: {joint1}")
    print(f"End Effector: {end_effector}")

    # Plot the arm
    plot_arm(base, joint1, end_effector)

if __name__ == "__main__":
    main()
