import os
from typing import Dict, List, Optional, Union, Tuple
import numpy as np

from gymnasium.utils.ezpickle import EzPickle

from Curriculum.envs.fetch_curriculum import MujocoFetchEnv, MujocoPyFetchEnv

# Ensure we get the path separator correct on windows
MODEL_XML_PATH = os.path.join("fetch", "push.xml")


class MujocoPyFetchPushEnv(MujocoPyFetchEnv, EzPickle):
    def __init__(self, reward_type="sparse", **kwargs):
        initial_qpos = {
            "robot0:slide0": 0.405,
            "robot0:slide1": 0.48,
            "robot0:slide2": 0.0,
            "object0:joint": [1.25, 0.53, 0.4, 1.0, 0.0, 0.0, 0.0],
        }
        MujocoPyFetchEnv.__init__(
            self,
            model_path=MODEL_XML_PATH,
            has_object=True,
            block_gripper=True,
            n_substeps=20,
            gripper_extra_height=0.0,
            target_in_the_air=False,
            target_offset=0.0,
            obj_range=0.15,
            target_range=0.15,
            distance_threshold=0.05,
            initial_qpos=initial_qpos,
            reward_type=reward_type,
            **kwargs,
        )
        EzPickle.__init__(self, reward_type=reward_type, **kwargs)


class MujocoFetchPushEnv(MujocoFetchEnv, EzPickle):
    """
    ## Description

    This environment was introduced in ["Multi-Goal Reinforcement Learning: Challenging Robotics Environments and Request for Research"](https://arxiv.org/abs/1802.09464).

    The task in the environment is for a manipulator to move a block to a target position on top of a table by pushing with its gripper. The robot is a 7-DoF [Fetch Mobile Manipulator](https://fetchrobotics.com/) with a two-fingered parallel gripper.
    The robot is controlled by small displacements of the gripper in Cartesian coordinates and the inverse kinematics are computed internally by the MuJoCo framework. The gripper is locked in a closed configuration in order to perform the push task.
    The task is also continuing which means that the robot has to maintain the block in the target position for an indefinite period of time.

    The control frequency of the robot is of `f = 25 Hz`. This is achieved by applying the same action in 20 subsequent simulator step (with a time step of `dt = 0.002 s`) before returning the control to the robot.

    ## Action Space

    The action space is a `Box(-1.0, 1.0, (4,), float32)`. An action represents the Cartesian displacement dx, dy, and dz of the end effector. In addition to a last action that controls closing and opening of the gripper.

    | Num | Action                                                 | Control Min | Control Max | Name (in corresponding XML file)                                | Joint | Unit         |
    | --- | ------------------------------------------------------ | ----------- | ----------- | --------------------------------------------------------------- | ----- | ------------ |
    | 0   | Displacement of the end effector in the x direction dx | -1          | 1           | robot0:mocap                                                    | hinge | position (m) |
    | 1   | Displacement of the end effector in the y direction dy | -1          | 1           | robot0:mocap                                                    | hinge | position (m) |
    | 2   | Displacement of the end effector in the z direction dz | -1          | 1           | robot0:mocap                                                    | hinge | position (m) |
    | 3   | -                                                      | -1          | 1           | -                                                               | hinge | position (m) |

    ## Observation Space

    The observation is a `goal-aware observation space`. It consists of a dictionary with information about the robot's end effector state and goal. The kinematics observations are derived from Mujoco bodies known as [sites](https://mujoco.readthedocs.io/en/latest/XMLreference.html?highlight=site#body-site) attached to the body of interest such as the block or the end effector.
    Also to take into account the temporal influence of the step time, velocity values are multiplied by the step time dt=number_of_sub_steps*sub_step_time. The dictionary consists of the following 3 keys:

    * `observation`: its value is an `ndarray` of shape `(25,)`. It consists of kinematic information of the block object and gripper. The elements of the array correspond to the following:

    | Num | Observation                                                                                                                           | Min    | Max    | Site Name (in corresponding XML file) | Joint Name (in corresponding XML file) |Joint Type| Unit                     |
    |-----|---------------------------------------------------------------------------------------------------------------------------------------|--------|--------|---------------------------------------|----------------------------------------|----------|--------------------------|
    | 0   | End effector x position in global coordinates                                                                                         | -Inf   | Inf    | robot0:grip                           |-                                       |-         | position (m)             |
    | 1   | End effector y position in global coordinates                                                                                         | -Inf   | Inf    | robot0:grip                           |-                                       |-         | position (m)             |
    | 2   | End effector z position in global coordinates                                                                                         | -Inf   | Inf    | robot0:grip                           |-                                       |-         | position (m)             |
    | 3   | Block x position in global coordinates                                                                                                | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 4   | Block y position in global coordinates                                                                                                | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 5   | Block z position in global coordinates                                                                                                | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 6   | Relative block x position with respect to gripper x position in global coordinates. Equals to x<sub>block</sub> - x<sub>gripper</sub> | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 7   | Relative block y position with respect to gripper y position in global coordinates. Equals to y<sub>block</sub> - y<sub>gripper</sub> | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 8   | Relative block z position with respect to gripper z position in global coordinates. Equals to z<sub>block</sub> - z<sub>gripper</sub> | -Inf   | Inf    | object0                               |-                                       |-         | position (m)             |
    | 9   | Joint displacement of the right gripper finger                                                                                        | -Inf   | Inf    |-                                      | robot0:r_gripper_finger_joint          | hinge    | position (m)             |
    | 10  | Joint displacement of the left gripper finger                                                                                         | -Inf   | Inf    |-                                      | robot0:l_gripper_finger_joint          | hinge    | position (m)             |
    | 11  | Global x rotation of the block in a XYZ Euler frame rotation                                                                          | -Inf   | Inf    | object0                               |-                                       |-         | angle (rad)              |
    | 12  | Global y rotation of the block in a XYZ Euler frame rotation                                                                          | -Inf   | Inf    | object0                               |-                                       |-         | angle (rad)              |
    | 13  | Global z rotation of the block in a XYZ Euler frame rotation                                                                          | -Inf   | Inf    | object0                               |-                                       |-         | angle (rad)              |
    | 14  | Relative block linear velocity in x direction with respect to the gripper                                                              | -Inf   | Inf    | object0                               |-                                       |-         | velocity (m/s)           |
    | 15  | Relative block linear velocity in y direction with respect to the gripper                                                              | -Inf   | Inf    | object0                               |-                                       |-         | velocity (m/s)           |
    | 16  | Relative block linear velocity in z direction                                                                                         | -Inf   | Inf    | object0                               |-                                       |-         | velocity (m/s)           |
    | 17  | Block angular velocity along the x axis                                                                                               | -Inf   | Inf    | object0                               |-                                       |-         | angular velocity (rad/s) |
    | 18  | Block angular velocity along the y axis                                                                                               | -Inf   | Inf    | object0                               |-                                       |-         | angular velocity (rad/s) |
    | 19  | Block angular velocity along the z axis                                                                                               | -Inf   | Inf    | object0                               |-                                       |-         | angular velocity (rad/s) |
    | 20  | End effector linear velocity x direction                                                                                              | -Inf   | Inf    | robot0:grip                           |-                                       |-         | velocity (m/s)           |
    | 21  | End effector linear velocity y direction                                                                                              | -Inf   | Inf    | robot0:grip                           |-                                       |-         | velocity (m/s)           |
    | 22  | End effector linear velocity z direction                                                                                              | -Inf   | Inf    | robot0:grip                           |-                                       |-         | velocity (m/s)           |
    | 23  | Right gripper finger linear velocity                                                                                                  | -Inf   | Inf    |-                                      | robot0:r_gripper_finger_joint          | hinge    | velocity (m/s)           |
    | 24  | Left gripper finger linear velocity                                                                                                   | -Inf   | Inf    |-                                      | robot0:l_gripper_finger_joint          | hinge    | velocity (m/s)           |

    * `desired_goal`: this key represents the final goal to be achieved. In this environment it is a 3-dimensional `ndarray`, `(3,)`, that consists of the three cartesian coordinates of the desired final block position `[x,y,z]`. In order for the robot to perform a push trajectory, the goal position can only be placed on top of the table. The elements of the array are the following:

    | Num | Observation                                                                                                                           | Min    | Max    | Site Name (in corresponding XML file) |Unit          |
    |-----|---------------------------------------------------------------------------------------------------------------------------------------|--------|--------|---------------------------------------|--------------|
    | 0   | Final goal block position in the x coordinate                                                                                         | -Inf   | Inf    | target0                               | position (m) |
    | 1   | Final goal block position in the y coordinate                                                                                         | -Inf   | Inf    | target0                               | position (m) |
    | 2   | Final goal block position in the z coordinate                                                                                         | -Inf   | Inf    | target0                               | position (m) |

    * `achieved_goal`: this key represents the current state of the block, as if it would have achieved a goal. This is useful for goal orientated learning algorithms such as those that use [Hindsight Experience Replay](https://arxiv.org/abs/1707.01495) (HER). The value is an `ndarray` with shape `(3,)`. The elements of the array are the following:

    | Num | Observation                                                                                                                           | Min    | Max    | Site Name (in corresponding XML file) |Unit          |
    |-----|---------------------------------------------------------------------------------------------------------------------------------------|--------|--------|---------------------------------------|--------------|
    | 0   | Current block position in the x coordinate                                                                                            | -Inf   | Inf    | object0                               | position (m) |
    | 1   | Current block position in the y coordinate                                                                                            | -Inf   | Inf    | object0                               | position (m) |
    | 2   | Current block position in the z coordinate                                                                                            | -Inf   | Inf    | object0                               | position (m) |


    ## Rewards

    The reward can be initialized as `sparse` or `dense`:
    - *sparse*: the returned reward can have two values: `-1` if the block hasn't reached its final target position, and `0` if the block is in the final target position (the block is considered to have reached the goal if the Euclidean distance between both is lower than 0.05 m).
    - *dense*: the returned reward is the negative Euclidean distance between the achieved goal position and the desired goal.

    To initialize this environment with one of the mentioned reward functions the type of reward must be specified in the id string when the environment is initialized. For `sparse` reward the id is the default of the environment, `FetchPush-v2`. However, for `dense` reward the id must be modified to `FetchPush-v2` and initialized as follows:

    ```python
    import gymnasium as gym
    import gymnasium_robotics

    gym.register_envs(gymnasium_robotics)

    env = gym.make('FetchPushDense-v2')
    ```

    ## Starting State

    When the environment is reset the gripper is placed in the following global cartesian coordinates `(x,y,z) = [1.3419 0.7491 0.555] m`, and its orientation in quaternions is `(w,x,y,z) = [1.0, 0.0, 1.0, 0.0]`. The joint positions are computed by inverse kinematics internally by MuJoCo. The base of the robot will always be fixed at `(x,y,z) = [0.405, 0.48, 0]` in global coordinates.

    The block's position has a fixed height of `(z) = [0.42] m ` (on top of the table). The initial `(x,y)` position of the block is the gripper's x and y coordinates plus an offset sampled from a uniform distribution with a range of `[-0.15, 0.15] m`. Offset samples are generated until the 2-dimensional Euclidean distance from the gripper to the block is greater than `0.1 m`.
    The initial orientation of the block is the same as for the gripper, `(w,x,y,z) = [1.0, 0.0, 1.0, 0.0]`.

    Finally the target position where the robot has to move the block is generated. The target can be in mid-air or over the table. The random target is also generated by adding an offset to the initial grippers position `(x,y)` sampled from a uniform distribution with a range of `[-0.15, 0.15] m`. The height of the target is initialized at `(z) = [0.42] m ` on the table.


    ## Episode End

    The episode will be `truncated` when the duration reaches a total of `max_episode_steps` which by default is set to 50 timesteps.
    The episode is never `terminated` since the task is continuing with infinite horizon.

    ## Arguments

    To increase/decrease the maximum number of timesteps before the episode is `truncated` the `max_episode_steps` argument can be set at initialization.
    The default value is 50. For example, to increase the total number of timesteps to 100 make the environment as follows:

    ```python
    import gymnasium as gym
    import gymnasium_robotics

    gym.register_envs(gymnasium_robotics)

    env = gym.make('FetchPush-v2', max_episode_steps=100)
    ```

    ## Version History

    * v2: the environment depends on the newest [mujoco python bindings](https://mujoco.readthedocs.io/en/latest/python.html) maintained by the MuJoCo team in Deepmind.
    * v1: the environment depends on `mujoco_py` which is no longer maintained.
    """

    def __init__(self, reward_type="sparse", **kwargs):
        initial_qpos = {
            "robot0:slide0": 0.405,
            "robot0:slide1": 0.48,
            "robot0:slide2": 0.0,
            "object0:joint": [1.25, 0.53, 0.4, 1.0, 0.0, 0.0, 0.0],
        }
        MujocoFetchEnv.__init__(
            self,
            model_path=MODEL_XML_PATH,
            has_object=True,
            block_gripper=True,
            n_substeps=20,
            gripper_extra_height=0.0,
            target_in_the_air=False,
            target_offset=0.0,
            obj_range=0.15,
            target_range=0.15,
            distance_threshold=0.05,
            initial_qpos=initial_qpos,
            reward_type=reward_type,
            **kwargs,
        )
        EzPickle.__init__(self, reward_type=reward_type, **kwargs)

    def set_task(self, task: str):
        self.task = task

    def step(self, action):
        """Run one timestep of the environment's dynamics using the agent actions.

        Args:
            action (np.ndarray): Control action to be applied to the agent and update the simulation. Should be of shape :attr:`action_space`.

        Returns:
            observation (dictionary): Next observation due to the agent actions .It should satisfy the `GoalEnv` :attr:`observation_space`.
            reward (integer): The reward as a result of taking the action. This is calculated by :meth:`compute_reward` of `GoalEnv`.
            terminated (boolean): Whether the agent reaches the terminal state. This is calculated by :meth:`compute_terminated` of `GoalEnv`.
            truncated (boolean): Whether the truncation condition outside the scope of the MDP is satisfied. Timically, due to a timelimit, but
            it is also calculated in :meth:`compute_truncated` of `GoalEnv`.
            info (dictionary): Contains auxiliary diagnostic information (helpful for debugging, learning, and logging). In this case there is a single
            key `is_success` with a boolean value, True if the `achieved_goal` is the same as the `desired_goal`.
        """
        if np.array(action).shape != self.action_space.shape:
            raise ValueError("Action dimension mismatch")

        action = np.clip(action, self.action_space.low, self.action_space.high)
        self._set_action(action)

        self._mujoco_step(action)

        self._step_callback()

        if self.render_mode == "human":
            self.render()
        obs = self._get_obs()

        info = {
            "success": self._is_success(obs["achieved_goal"], self.goal),
        }

        terminated = self.compute_terminated(obs["achieved_goal"], self.goal, info)
        truncated = self.compute_truncated(obs["achieved_goal"], self.goal, info)

        reward, reward_dict = self.compute_reward(obs["achieved_goal"], self.goal, info)

        info["reward_main"] = reward
        info["reward_task"] = reward
        info["reward_dict"] = reward_dict

        return obs, reward, terminated, truncated, info

    def compute_reward(self, achieved_goal, goal, info) -> np.float64:
        if self.task == "align_end_effector_with_block":
            reward, reward_dict = self.align_end_effector_with_block()
            return reward, reward_dict
        elif self.task == "match_end_effector_velocity_with_block":
            reward_1, reward_dict_1 = self.match_end_effector_velocity_with_block()
            reward_2, reward_dict_2 = self.align_end_effector_with_block()
            reward = reward_1 + 5*reward_2
            reward_dict = {**reward_dict_1, **reward_dict_2}
            return reward, reward_dict
        elif self.task == "reduced_distance_to_goal":
            reward_1, reward_dict_1 = self.reduce_distance_to_goal()
            reward_2, reward_dict_2 = self.match_end_effector_velocity_with_block()
            reward = reward_1 + 5*reward_2
            reward_dict = {**reward_dict_1, **reward_dict_2}
            return reward, reward_dict
        elif self.task == "move_block_to_target_position":
            reward_1, reward_dict_1 = self.original_task_reward()
            reward_2, reward_dict_2 = self.reduce_distance_to_goal()
            reward = reward_1 + 5*reward_2
            reward_dict = {**reward_dict_1, **reward_dict_2}
            return reward, reward_dict
        else:
            raise ValueError(f"Task {self.task} not recognized.")

    def align_end_effector_with_block(self) -> Tuple[np.float64, Dict[str, np.float64]]:
        # Extract the positions of the end effector and the block
        end_effector_pos = self.end_effector_position()
        block_pos = self.block_position()
        
        # Compute the distance between the end effector and the block
        distance = np.linalg.norm(end_effector_pos - block_pos)
        
        # Define a weight for the distance penalty
        distance_weight = 1.0

        # Compute the reward based on the distance. The closer the end effector is to the block, the higher the reward.
        reward = -distance_weight * distance

        # Create a dictionary to store the components of the reward
        reward_components = {"distance_to_block": -distance}

        return reward, reward_components
    
    def match_end_effector_velocity_with_block(self) -> Tuple[np.float64, Dict[str, np.float64]]:
        # Observing the End effector and block velocity
        block_velocity_relative_to_end_effector = self.block_relative_linear_velocity()

        # Computing the difference in velocities to minimize it
        velocity_difference = np.linalg.norm(block_velocity_relative_to_end_effector)

        # Reward is higher when the difference is smaller. We can use negative velocity_difference for this, but using -np.tanh() to constrain the value between -1 and 0
        reward_velocity_match = -np.tanh(velocity_difference)
        
        # Detailed rewards for inspection purposes
        detailed_rewards = {
            "velocity_match": reward_velocity_match,
        }

        total_reward = reward_velocity_match
        return total_reward, detailed_rewards
    
    def reduce_distance_to_goal(self) -> Tuple[np.float64, Dict[str, np.float64]]:
        block_position = self.block_position()
        goal_position = self.goal_position()
        distance_to_goal = np.linalg.norm(block_position - goal_position)
        
        # Set a weighting factor to scale the importance of this component
        distance_weight = 1.0
        
        # Minimize the distance using -tanh to ensure the reward increases as distance decreases
        reward = -np.tanh(distance_weight * distance_to_goal)
        
        # It's helpful to break down the reward components for debugging and understanding the contributions 
        reward_components = {
            "distance_to_goal": -distance_to_goal  # Negative to indicate minimization
        }
        
        return reward, reward_components
    
    def original_task_reward(self) -> Tuple[np.float64, Dict[str, np.float64]]:
        # Define weight parameters
        distance_weight = 1.0
        velocity_weight = 0.1
        
        # Get positions and velocities
        block_pos = self.block_position()
        goal_pos = self.goal_position()
        block_vel = self.block_relative_linear_velocity()
        ee_vel = self.end_effector_linear_velocity()
        
        # Compute distance to goal (ignore z axis)
        distance_to_goal = np.linalg.norm(block_pos[:2] - goal_pos[:2])
        
        # Compute reward components
        distance_reward = -distance_weight * distance_to_goal  # Reward for moving block closer to goal
        
        # Also, we want to control the velocity at which the block is pushed towards the goal
        # Reward for keeping a slow and steady pace in the direction of the goal
        block_velocity_reward = -velocity_weight * np.linalg.norm(block_vel)
        
        # Encourage the end effector to move at a reasonable speed to ensure precise control
        ee_velocity_reward = -velocity_weight * np.linalg.norm(ee_vel)
        
        # Compute total reward
        total_reward = distance_reward + block_velocity_reward + ee_velocity_reward
        
        # Reward components dictionary
        reward_components = {
            "distance_reward": distance_reward,
            "block_velocity_reward": block_velocity_reward,
            "ee_velocity_reward": ee_velocity_reward
        }
        
        return total_reward, reward_components

    def end_effector_position(self):
        (
            grip_pos,
            object_pos,
            object_rel_pos,
            gripper_state,
            object_rot,
            object_velp,
            object_velr,
            grip_velp,
            gripper_vel,
        ) = self.generate_mujoco_observations()    

        return grip_pos  

    def block_position(self):
        (
            grip_pos,
            object_pos,
            object_rel_pos,
            gripper_state,
            object_rot,
            object_velp,
            object_velr,
            grip_velp,
            gripper_vel,
        ) = self.generate_mujoco_observations()    

        return object_pos  

    def block_relative_linear_velocity(self):
        (
            grip_pos,
            object_pos,
            object_rel_pos,
            gripper_state,
            object_rot,
            object_velp,
            object_velr,
            grip_velp,
            gripper_vel,
        ) = self.generate_mujoco_observations()    

        return object_velp

    def end_effector_linear_velocity(self):
        (
            grip_pos,
            object_pos,
            object_rel_pos,
            gripper_state,
            object_rot,
            object_velp,
            object_velr,
            grip_velp,
            gripper_vel,
        ) = self.generate_mujoco_observations()    

        return grip_velp

    def goal_position(self):
        return self.goal.copy()