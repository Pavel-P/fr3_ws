#!/usr/bin/env python3

import rclpy
from gear_place.gear_place_classes import GearPlace, Error
from gear_place.find_object import FindObject
from gear_place.object_depth import ObjectDepth
from time import sleep


def main(args=None):
    gear_center_target = [0 for i in range(3)]
    rclpy.init(args=args)

    try:
        x_offset = 0.047  # offset from the camera to the gripper
        y_offset = 0.03  # offset from the camera to the gripper
        z_movement = (
            -0.247
        )  # z distance from the home position to where the gripper can grab the gear
        supervisor = GearPlace("gear_place")
        supervisor.wait(0.75)
        supervisor._call_move_to_named_pose_service(
            "home"
        )  # starts in the home position
        sleep(3)
        supervisor._call_move_cartesian_service(
            -0.27, 0.0, 0.0, 0.15, 0.2
        )  # Moves to the center of the cart
        sleep(1)

        while (
            gear_center_target.count(0) == 3 or None in gear_center_target
        ):  # runs until valid coordinates are found
            find_object = FindObject()
            rclpy.spin_once(find_object)  # Finds the gear
            while find_object.ret_cent_gear().count(None)!=0: #Runs and guarantees that none of the coordinates are none type
                find_object.destroy_node()
                find_object = FindObject()
                rclpy.spin_once(find_object)
            object_depth = ObjectDepth(find_object.ret_cent_gear())
            rclpy.spin_once(object_depth)  # Gets the distance from the camera
            object_depth.destroy_node()  # Destroys the node to avoid errors on next loop
            find_object.destroy_node()
            gear_center_target[0] = object_depth.dist_x
            gear_center_target[1] = object_depth.dist_y
            gear_center_target[2] = object_depth.dist_z
            sleep(1)  # sleeps between tries
        sleep(1)
        print(gear_center_target)
        supervisor._call_pick_up_gear_service(
            -1 * object_depth.dist_y + x_offset,
            -1 * object_depth.dist_x + y_offset,
            z_movement,
            0.0095,
        )  # Moves to above the gear, opens the gripper to the maximum, then down to the gear, grabs the gear, then picks it up
        sleep(1.5)
        supervisor._call_put_gear_down_service(
            z_movement
        )  # moves down, releases the gear, and moves back up

    except Error as e:
        print(e)


if __name__ == "__main__":
    main()
