"""An Adroit arm environment with ball relocation task using the Gymnasium API.

The code is inspired by the D4RL repository hosted on GitHub (https://github.com/Farama-Foundation/D4RL), published in the paper
'D4RL: Datasets for Deep Data-Driven Reinforcement Learning' by Justin Fu, Aviral Kumar, Ofir Nachum, George Tucker, Sergey Levine.

Original Author of the code: Justin Fu

The modifications made involve organizing the code into different files adding support for the Gymnasium API.

This project is covered by the Apache 2.0 License.
"""

from os import path
from typing import Optional
import sys

import numpy as np
from gymnasium import spaces
from gymnasium.envs.mujoco.mujoco_env import MujocoEnv
from gymnasium.utils.ezpickle import EzPickle

from gymnasium_robotics.utils.mujoco_utils import MujocoModelNames

from gymnasium_robotics.envs.adroit_hand.adroit_pen import AdroitHandPenEnv

DEFAULT_CAMERA_CONFIG = {
    "distance": 1.5,
    "azimuth": 90.0,
}


class AdroitHandRelocateEnv(MujocoEnv, EzPickle):
    """
    ## Description

    This environment was introduced in ["Learning Complex Dexterous Manipulation with Deep Reinforcement Learning and Demonstrations"](https://arxiv.org/abs/1709.10087)
    by Aravind Rajeswaran, Vikash Kumar, Abhishek Gupta, Giulia Vezzani, John Schulman, Emanuel Todorov, and Sergey Levine.

    The environment is based on the [Adroit manipulation platform](https://github.com/vikashplus/Adroit), a30 degree of freedom system which consists of a 24 degrees of freedom
    ShadowHand and a 6 degree of freedom arm. The task to be completed consists on moving the blue ball to the green target. The positions of the ball and target are randomized over the entire
    workspace. The task will be considered successful when the object is within epsilon-ball of the target.

    ## Action Space

    The action space is a `Box(-1.0, 1.0, (30,), float32)`. The control actions are absolute angular positions of the Adroit hand joints. The input of the control actions is set to a range between -1 and 1 by scaling the real actuator angle ranges in radians.
    The elements of the action array are the following:

    | Num | Action                                                                                  | Control Min | Control Max | Angle Min    | Angle Max   | Name (in corresponding XML file) | Joint | Unit        |
    | --- | --------------------------------------------------------------------------------------- | ----------- | ----------- | ------------ | ----------  |--------------------------------- | ----- | ----------- |
    | 0   | Linear translation of the full arm in x direction                                       | -1          | 1           | -0.3 (m)     | 0.5 (m)     | A_ARTx                           | slide | position (m)|
    | 1   | Linear translation of the full arm in y direction                                       | -1          | 1           | -0.3 (m)     | 0.5 (m)     | A_ARTy                           | slide | position (m)|
    | 2   | Linear translation of the full arm in z direction                                       | -1          | 1           | -0.3 (m)     | 0.5 (m)     | A_ARTz                           | slide | position (m)|
    | 3   | Angular up and down movement of the full arm                                            | -1          | 1           | -0.4 (rad)   | 0.25 (rad)  | A_ARRx                           | hinge | angle (rad) |
    | 4   | Angular left and right and down movement of the full arm                                | -1          | 1           | -0.3 (rad)   | 0.3 (rad)   | A_ARRy                           | hinge | angle (rad) |
    | 5   | Roll angular movement of the full arm                                                   | -1          | 1           | -1.0 (rad)   | 2.0 (rad)   | A_ARRz                           | hinge | angle (rad) |
    | 6   | Angular position of the horizontal wrist joint (radial/ulnar deviation)                 | -1          | 1           | -0.524 (rad) | 0.175 (rad) | A_WRJ1                           | hinge | angle (rad) |
    | 7   | Angular position of the horizontal wrist joint (flexion/extension)                      | -1          | 1           | -0.79 (rad)  | 0.61 (rad)  | A_WRJ0                           | hinge | angle (rad) |
    | 8   | Horizontal angular position of the MCP joint of the forefinger (adduction/abduction)    | -1          | 1           | -0.44 (rad)  | 0.44(rad)   | A_FFJ3                           | hinge | angle (rad) |
    | 9   | Vertical angular position of the MCP joint of the forefinger (flexion/extension)        | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_FFJ2                           | hinge | angle (rad) |
    | 10  | Angular position of the PIP joint of the forefinger (flexion/extension)                 | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_FFJ1                           | hinge | angle (rad) |
    | 11  | Angular position of the DIP joint of the forefinger                                     | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_FFJ0                           | hinge | angle (rad) |
    | 12  | Horizontal angular position of the MCP joint of the middle finger (adduction/abduction) | -1          | 1           | -0.44 (rad)  | 0.44(rad)   | A_MFJ3                           | hinge | angle (rad) |
    | 13  | Vertical angular position of the MCP joint of the middle finger (flexion/extension)     | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_MFJ2                           | hinge | angle (rad) |
    | 14  | Angular position of the PIP joint of the middle finger (flexion/extension)              | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_MFJ1                           | hinge | angle (rad) |
    | 15  | Angular position of the DIP joint of the middle finger                                  | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_MFJ0                           | hinge | angle (rad) |
    | 16  | Horizontal angular position of the MCP joint of the ring finger (adduction/abduction)   | -1          | 1           | -0.44 (rad)  | 0.44(rad)   | A_RFJ3                           | hinge | angle (rad) |
    | 17  | Vertical angular position of the MCP joint of the ring finger (flexion/extension)       | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_RFJ2                           | hinge | angle (rad) |
    | 18  | Angular position of the PIP joint of the ring finger                                    | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_RFJ1                           | hinge | angle (rad) |
    | 19  | Angular position of the DIP joint of the ring finger                                    | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_RFJ0                           | hinge | angle (rad) |
    | 20  | Angular position of the CMC joint of the little finger                                  | -1          | 1           | 0 (rad)      | 0.7(rad)    | A_LFJ4                           | hinge | angle (rad) |
    | 21  | Horizontal angular position of the MCP joint of the little finger (adduction/abduction) | -1          | 1           | -0.44 (rad)  | 0.44(rad)   | A_LFJ3                           | hinge | angle (rad) |
    | 22  | Vertical angular position of the MCP joint of the little finger (flexion/extension)     | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_LFJ2                           | hinge | angle (rad) |
    | 23  | Angular position of the PIP joint of the little finger (flexion/extension)              | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_LFJ1                           | hinge | angle (rad) |
    | 24  | Angular position of the DIP joint of the little finger                                  | -1          | 1           | 0 (rad)      | 1.6 (rad)   | A_LFJ0                           | hinge | angle (rad) |
    | 25  | Horizontal angular position of the CMC joint of the thumb finger                        | -1          | 1           | -1.047 (rad) | 1.047 (rad) | A_THJ4                           | hinge | angle (rad) |
    | 26  | Vertical Angular position of the CMC joint of the thumb finger                          | -1          | 1           | 0 (rad)      | 1.3 (rad)   | A_THJ3                           | hinge | angle (rad) |
    | 27  | Horizontal angular position of the MCP joint of the thumb finger (adduction/abduction)  | -1          | 1           | -0.26 (rad)  | 0.26(rad)   | A_THJ2                           | hinge | angle (rad) |
    | 28  | Vertical angular position of the MCP joint of the thumb finger (flexion/extension)      | -1          | 1           | -0.52 (rad)  | 0.52 (rad)  | A_THJ1                           | hinge | angle (rad) |
    | 29  | Angular position of the IP joint of the thumb finger (flexion/extension)                | -1          | 1           | -1.571 (rad) | 0 (rad)     | A_THJ0                           | hinge | angle (rad) |


    ## Observation Space

    The observation space is of the type `Box(-inf, inf, (39,), float64)`. It contains information about the angular position of the finger joints, the pose of the palm of the hand, as well as kinematic information about the ball and target.

    | Num | Observation                                                                 | Min    | Max    | Joint Name (in corresponding XML file) | Site/Body Name (in corresponding XML file) | Joint Type| Unit                     |
    |-----|-----------------------------------------------------------------------------|--------|--------|----------------------------------------|--------------------------------------------|-----------|------------------------- |
    | 0   | Translation of the arm in the x direction                                   | -Inf   | Inf    | ARTx                                   | -                                          | slide     | position (m)             |
    | 1   | Translation of the arm in the y direction                                   | -Inf   | Inf    | ARTy                                   | -                                          | slide     | position (m)             |
    | 2   | Translation of the arm in the z direction                                   | -Inf   | Inf    | ARTz                                   | -                                          | slide     | position (m)             |
    | 3   | Angular position of the vertical arm joint                                  | -Inf   | Inf    | ARRx                                   | -                                          | hinge     | angle (rad)              |
    | 4   | Angular position of the horizontal arm joint                                | -Inf   | Inf    | ARRy                                   | -                                          | hinge     | angle (rad)              |
    | 5   | Roll angular value of the arm                                               | -Inf   | Inf    | ARRz                                   | -                                          | hinge     | angle (rad)              |
    | 6   | Angular position of the horizontal wrist joint                              | -Inf   | Inf    | WRJ1                                   | -                                          | hinge     | angle (rad)              |
    | 7   | Angular position of the vertical wrist joint                                | -Inf   | Inf    | WRJ0                                   | -                                          | hinge     | angle (rad)              |
    | 8   | Horizontal angular position of the MCP joint of the forefinger              | -Inf   | Inf    | FFJ3                                   | -                                          | hinge     | angle (rad)              |
    | 9   | Vertical angular position of the MCP joint of the forefinge                 | -Inf   | Inf    | FFJ2                                   | -                                          | hinge     | angle (rad)              |
    | 10  | Angular position of the PIP joint of the forefinger                         | -Inf   | Inf    | FFJ1                                   | -                                          | hinge     | angle (rad)              |
    | 11  | Angular position of the DIP joint of the forefinger                         | -Inf   | Inf    | FFJ0                                   | -                                          | hinge     | angle (rad)              |
    | 12  | Horizontal angular position of the MCP joint of the middle finger           | -Inf   | Inf    | MFJ3                                   | -                                          | hinge     | angle (rad)              |
    | 13  | Vertical angular position of the MCP joint of the middle finger             | -Inf   | Inf    | MFJ2                                   | -                                          | hinge     | angle (rad)              |
    | 14  | Angular position of the PIP joint of the middle finger                      | -Inf   | Inf    | MFJ1                                   | -                                          | hinge     | angle (rad)              |
    | 15  | Angular position of the DIP joint of the middle finger                      | -Inf   | Inf    | MFJ0                                   | -                                          | hinge     | angle (rad)              |
    | 16  | Horizontal angular position of the MCP joint of the ring finger             | -Inf   | Inf    | RFJ3                                   | -                                          | hinge     | angle (rad)              |
    | 17  | Vertical angular position of the MCP joint of the ring finger               | -Inf   | Inf    | RFJ2                                   | -                                          | hinge     | angle (rad)              |
    | 18  | Angular position of the PIP joint of the ring finger                        | -Inf   | Inf    | RFJ1                                   | -                                          | hinge     | angle (rad)              |
    | 19  | Angular position of the DIP joint of the ring finger                        | -Inf   | Inf    | RFJ0                                   | -                                          | hinge     | angle (rad)              |
    | 20  | Angular position of the CMC joint of the little finger                      | -Inf   | Inf    | LFJ4                                   | -                                          | hinge     | angle (rad)              |
    | 21  | Horizontal angular position of the MCP joint of the little finger           | -Inf   | Inf    | LFJ3                                   | -                                          | hinge     | angle (rad)              |
    | 22  | Vertical angular position of the MCP joint of the little finger             | -Inf   | Inf    | LFJ2                                   | -                                          | hinge     | angle (rad)              |
    | 23  | Angular position of the PIP joint of the little finger                      | -Inf   | Inf    | LFJ1                                   | -                                          | hinge     | angle (rad)              |
    | 24  | Angular position of the DIP joint of the little finger                      | -Inf   | Inf    | LFJ0                                   | -                                          | hinge     | angle (rad)              |
    | 25  | Horizontal angular position of the CMC joint of the thumb finger            | -Inf   | Inf    | THJ4                                   | -                                          | hinge     | angle (rad)              |
    | 26  | Vertical Angular position of the CMC joint of the thumb finger              | -Inf   | Inf    | THJ3                                   | -                                          | hinge     | angle (rad)              |
    | 27  | Horizontal angular position of the MCP joint of the thumb finger            | -Inf   | Inf    | THJ2                                   | -                                          | hinge     | angle (rad)              |
    | 28  | Vertical angular position of the MCP joint of the thumb finger              | -Inf   | Inf    | THJ1                                   | -                                          | hinge     | angle (rad)              |
    | 29  | Angular position of the IP joint of the thumb finger                        | -Inf   | Inf    | THJ0                                   | -                                          | hinge     | angle (rad)              |
    | 30  | x positional difference from the palm of the hand to the ball               | -Inf   | Inf    | -                                      | Object,S_grasp                             | -         | position (m)             |
    | 31  | y positional difference from the palm of the hand to the ball               | -Inf   | Inf    | -                                      | Object,S_grasp                             | -         | position (m)             |
    | 32  | z positional difference from the palm of the hand to the ball               | -Inf   | Inf    | -                                      | Object,S_grasp                             | -         | position (m)             |
    | 33  | x positional difference from the palm of the hand to the target             | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |
    | 34  | y positional difference from the palm of the hand to the target             | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |
    | 35  | z positional difference from the palm of the hand to the target             | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |
    | 36  | x positional difference from the ball to the target                         | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |
    | 37  | y positional difference from the ball to the target                         | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |
    | 38  | z positional difference from the ball to the target                         | -Inf   | Inf    | -                                      | Object,target                              | -         | position (m)             |

    ## Rewards

    The environment can be initialized in either a `dense` or `sparse` reward variant.

    In the `dense` reward setting, the environment returns a `dense` reward function that consists of the following parts:
    - `get_to_ball`: increasing negative reward the further away the palm of the hand is from the ball. This is computed as the 3 dimensional Euclidean distance between both body frames.
        This penalty is scaled by a factor of `0.1` in the final reward.
    - `ball_off_table`: add a positive reward of 1 if the ball is lifted from the table (`z` greater than `0.04` meters). If this condition is met two additional rewards are added:
        - `make_hand_go_to_target`: negative reward equal to the 3 dimensional Euclidean distance from the palm to the target ball position. This reward is scaled by a factor of `0.5`.
        -` make_ball_go_to_target`: negative reward equal to the 3 dimensional Euclidean distance from the ball to its target position. This reward is also scaled by a factor of `0.5`.
    - `ball_close_to_target`: bonus of `10` if the ball's Euclidean distance to its target is less than `0.1` meters. Bonus of `20` if the distance is less than `0.05` meters.

    The `sparse` reward variant of the environment can be initialized by calling `gym.make('AdroitHandReloateSparse-v1')`.
    In this variant, the environment returns a reward of 10 for environment success and -0.1 otherwise.

    ## Starting State

    The ball is set randomly over the table at reset. The ranges of the uniform distribution from which the position is samples are `[-0.15,0.15]` for the `x` coordinate, and `[-0.15,0.3]` got the `y` coordinate.
    The target position is also sampled from uniform distributions with ranges `[-0.2,0.2]` for the `x` coordinate, `[-0.2,0.2]` for the `y` coordinate, and `[0.15,0.35]` for the `z` coordinate.

    The joint values of the environment are deterministically initialized to a zero.

    For reproducibility, the starting state of the environment can also be set when calling `env.reset()` by passing the `options` dictionary argument (https://gymnasium.farama.org/api/env/#gymnasium.Env.reset)
    with the `initial_state_dict` key. The `initial_state_dict` key must be a dictionary with the following items:

    * `qpos`: np.ndarray with shape `(36,)`, MuJoCo simulation joint positions
    * `qvel`: np.ndarray with shape `(36,)`, MuJoCo simulation joint velocities
    * `obj_pos`: np.ndarray with shape `(3,)`, cartesian coordinates of the ball object
    * `target_pos`: np.ndarray with shape `(3,)`, cartesian coordinates of the goal ball location

    The state of the simulation can also be set at any step with the `env.set_env_state(initial_state_dict)` method.

    ## Episode End

    The episode will be `truncated` when the duration reaches a total of `max_episode_steps` which by default is set to 200 timesteps.
    The episode is never `terminated` since the task is continuing with infinite horizon.

    ## Arguments

    To increase/decrease the maximum number of timesteps before the episode is `truncated` the `max_episode_steps` argument can be set at initialization. The default value is 50. For example, to increase the total number of timesteps to 400 make the environment as follows:

    ```python
    import gymnasium as gym
    import gymnasium_robotics

    gym.register_envs(gymnasium_robotics)

    env = gym.make('AdroitHandRelocate-v1', max_episode_steps=400)
    ```

    ## Version History

    * v1: refactor version of the D4RL environment, also create dependency on newest [mujoco python bindings](https://mujoco.readthedocs.io/en/latest/python.html) maintained by the MuJoCo team in Deepmind.
    * v0: legacy versions in the [D4RL](https://github.com/Farama-Foundation/D4RL).
    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 100,
    }

    def __init__(self, reward_type: str = "dense", **kwargs):
        # Get the ant.xml path from the Gymnasium package
        xml_file_path = path.join(
            path.dirname(sys.modules[AdroitHandPenEnv.__module__].__file__), 
            "../assets/adroit_hand/adroit_relocate.xml"
        )
        observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(39,), dtype=np.float64
        )

        MujocoEnv.__init__(
            self,
            model_path=xml_file_path,
            frame_skip=5,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )
        self._model_names = MujocoModelNames(self.model)

        # whether to have sparse rewards
        if reward_type.lower() == "dense":
            self.sparse_reward = False
        elif reward_type.lower() == "sparse":
            self.sparse_reward = True
        else:
            raise ValueError(
                f"Unknown reward type, expected `dense` or `sparse` but got {reward_type}"
            )

        # Override action_space to -1, 1
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, dtype=np.float32, shape=self.action_space.shape
        )

        # change actuator sensitivity
        self.model.actuator_gainprm[
            self._model_names.actuator_name2id[
                "A_WRJ1"
            ] : self._model_names.actuator_name2id["A_WRJ0"]
            + 1,
            :3,
        ] = np.array([10, 0, 0])
        self.model.actuator_gainprm[
            self._model_names.actuator_name2id[
                "A_FFJ3"
            ] : self._model_names.actuator_name2id["A_THJ0"]
            + 1,
            :3,
        ] = np.array([1, 0, 0])
        self.model.actuator_biasprm[
            self._model_names.actuator_name2id[
                "A_WRJ1"
            ] : self._model_names.actuator_name2id["A_WRJ0"]
            + 1,
            :3,
        ] = np.array([0, -10, 0])
        self.model.actuator_biasprm[
            self._model_names.actuator_name2id[
                "A_FFJ3"
            ] : self._model_names.actuator_name2id["A_THJ0"]
            + 1,
            :3,
        ] = np.array([0, -1, 0])

        self.target_obj_site_id = self._model_names.site_name2id["target"]
        self.S_grasp_site_id = self._model_names.site_name2id["S_grasp"]
        self.obj_body_id = self._model_names.body_name2id["Object"]
        self.act_mean = np.mean(self.model.actuator_ctrlrange, axis=1)
        self.act_rng = 0.5 * (
            self.model.actuator_ctrlrange[:, 1] - self.model.actuator_ctrlrange[:, 0]
        )

        self._state_space = spaces.Dict(
            {
                "qpos": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(36,), dtype=np.float64
                ),
                "qvel": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(36,), dtype=np.float64
                ),
                "obj_pos": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(3,), dtype=np.float64
                ),
                "target_pos": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(3,), dtype=np.float64
                ),
            }
        )

        EzPickle.__init__(self, **kwargs)

    def step(self, a):
        a = np.clip(a, -1.0, 1.0)
        a = self.act_mean + a * self.act_rng  # mean center and scale
        self.do_simulation(a, self.frame_skip)
        obs = self._get_obs()
        obj_pos = self.data.xpos[self.obj_body_id].ravel()
        palm_pos = self.data.site_xpos[self.S_grasp_site_id].ravel()
        target_pos = self.data.site_xpos[self.target_obj_site_id].ravel()

        # compute the sparse reward variant first
        goal_distance = float(np.linalg.norm(obj_pos - target_pos))
        goal_achieved = goal_distance < 0.1
        reward_main = 10.0 if goal_achieved else -0.1

        # override reward if not sparse reward
        if not self.sparse_reward:
            reward_main = 0.1 * np.linalg.norm(palm_pos - obj_pos)  # take hand to object
            if obj_pos[2] > 0.04:  # if object off the table
                reward_main += 1.0  # bonus for lifting the object
                reward_main += -0.5 * np.linalg.norm(
                    palm_pos - target_pos
                )  # make hand go to target
                reward_main += -0.5 * np.linalg.norm(
                    obj_pos - target_pos
                )  # make object go to target

            # bonus for object close to target
            if goal_distance < 0.1:
                reward_main += 10.0

            # bonus for object "very" close to target
            if goal_distance < 0.05:
                reward_main += 20.0

        if self.render_mode == "human":
            self.render()

        reward, reward_dict = self.compute_reward_curriculum()

        reward_dict["main"] = reward_main
        reward_dict["task"] = reward

        info = {
            "success": goal_achieved,
            "reward_dict": reward_dict,
        }

        return obs, reward, False, False, info

    def _get_obs(self):
        # qpos for hand
        # xpos for obj
        # xpos for target
        qpos = self.data.qpos.ravel()
        obj_pos = self.data.xpos[self.obj_body_id].ravel()
        palm_pos = self.data.site_xpos[self.S_grasp_site_id].ravel()
        target_pos = self.data.site_xpos[self.target_obj_site_id].ravel()
        return np.concatenate(
            [qpos[:-6], palm_pos - obj_pos, palm_pos - target_pos, obj_pos - target_pos]
        )

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        obs, info = super().reset(seed=seed)
        if options is not None and "initial_state_dict" in options:
            self.set_env_state(options["initial_state_dict"])
            obs = self._get_obs()

        return obs, info

    def reset_model(self):
        self.model.body_pos[self.obj_body_id, 0] = self.np_random.uniform(
            low=-0.15, high=0.15
        )
        self.model.body_pos[self.obj_body_id, 1] = self.np_random.uniform(
            low=-0.15, high=0.3
        )
        self.model.site_pos[self.target_obj_site_id, 0] = self.np_random.uniform(
            low=-0.2, high=0.2
        )
        self.model.site_pos[self.target_obj_site_id, 1] = self.np_random.uniform(
            low=-0.2, high=0.2
        )
        self.model.site_pos[self.target_obj_site_id, 2] = self.np_random.uniform(
            low=0.15, high=0.35
        )

        self.set_state(self.init_qpos, self.init_qvel)

        return self._get_obs()

    def get_env_state(self):
        """
        Get state of hand as well as objects and targets in the scene
        """
        qpos = self.data.qpos.ravel().copy()
        qvel = self.data.qvel.ravel().copy()
        hand_qpos = qpos[:30].copy()
        obj_pos = self.data.xpos[self.obj_body_id].ravel().copy()
        palm_pos = self.data.site_xpos[self.S_grasp_site_id].ravel().copy()
        target_pos = self.data.site_xpos[self.target_obj_site_id].ravel().copy()
        return dict(
            hand_qpos=hand_qpos,
            obj_pos=obj_pos,
            target_pos=target_pos,
            palm_pos=palm_pos,
            qpos=qpos,
            qvel=qvel,
        )

    def set_env_state(self, state_dict):
        """
        Set the state which includes hand as well as objects and targets in the scene
        """
        assert self._state_space.contains(
            state_dict
        ), f"The state dictionary {state_dict} must be a member of {self._state_space}."
        qp = state_dict["qpos"]
        qv = state_dict["qvel"]

        self.model.body_pos[self.obj_body_id] = state_dict["obj_pos"]
        self.model.site_pos[self.target_obj_site_id] = state_dict["target_pos"]

        self.set_state(qp, qv)

    def arm_position(self):
        # Translation position of the arm in xyz direction
        obs = self._get_obs()
        arm_xyz_pos = obs[:3]

        return arm_xyz_pos

    def arm_angular_position(self):
        # Angular position of arm
        obs = self._get_obs()
        arm_angular = obs[3:6]

        return arm_angular

    def wrist_angular_position(self):
        # Angular position of writst
        obs = self._get_obs()
        wrist_angular = obs[6:8]

        return wrist_angular

    def mcp_angular_position_forefinger(self):
        # Angular position of MCP(metacarpophalangeal, knuckle) joint of the forefinger
        # Horizontal and Vertical
        obs = self._get_obs()
        mcp_angular_forefinger = obs[8:10]

        return mcp_angular_forefinger

    def pip_angular_position_forefinger(self):
        # Angular position of PIP(proximal interphalangeal, middle) joint of the forefinger
        obs = self._get_obs()
        pip_angular_forefinger = obs[10]

        return pip_angular_forefinger

    def dip_angular_position_forefinger(self):
        # Angular position of DIP(Distal Interphalangeal, tip) joint of the forefinger
        obs = self._get_obs()
        dip_angular_forefinger = obs[11]

        return dip_angular_forefinger

    def mcp_angular_position_middlefinger(self):
        # Angular position of MCP(metacarpophalangeal, knuckle) joint of the middlefinger
        # Horizontal and Vertical
        obs = self._get_obs()
        mcp_angular_middle = obs[12:14]

        return mcp_angular_middle

    def pip_angular_position_middlefingler(self):
        # Angular position of PIP(proximal interphalangeal, middle) joint of the middlefinger
        obs = self._get_obs()
        pip_angular_middlefinger = obs[14]

        return pip_angular_middlefinger

    def dip_angular_position_middlefinger(self):
        # Angular position of DIP(Distal Interphalangeal, tip) joint of the middlefinger
        obs = self._get_obs()
        dip_angular_middlefinger = obs[15]

        return dip_angular_middlefinger

    def mcp_angular_position_ringfinger(self):
        # Angular position of MCP(metacarpophalangeal, knuckle) joint of the ringfinger
        # Horizontal and Vertical
        obs = self._get_obs()
        mcp_angular_ringfinger = obs[16:18]

        return mcp_angular_ringfinger

    def pip_angular_position_ringfinger(self):
        # Angular position of PIP(proximal interphalangeal, middle) joint of the ringfinger
        obs = self._get_obs()
        pip_angular_ringfinger = obs[18]

        return pip_angular_ringfinger

    def dip_angular_position_ringfinger(self):
        # Angular position of DIP(Distal Interphalangeal, tip) joint of the ringfinger
        obs = self._get_obs()
        dip_angular_ringfinger = obs[19]

        return dip_angular_ringfinger

    def cmc_angular_position_littlefinger(self):
        # Angular Position of the CMC (carpometacarpal) joint of the little finger
        obs = self._get_obs()
        cmc_angular_littlefinger = obs[20]

        return cmc_angular_littlefinger

    def mcp_angular_position_littlefinger(self):
        # Angular position of MCP(metacarpophalangeal, knuckle) joint of the littlefinger
        # Horizontal and Vertical
        obs = self._get_obs()
        mcp_angular_littlefinger = obs[21:23]

        return mcp_angular_littlefinger

    def pip_angular_position_littlefinger(self):
        # Angular position of PIP(proximal interphalangeal, middle) joint of the littlefinger
        obs = self._get_obs()
        pip_angular_littlefinger = obs[23]

        return pip_angular_littlefinger

    def dip_angular_position_littlefinger(self):
        # Angular position of DIP(Distal Interphalangeal, tip) joint of the littlefinger
        obs = self._get_obs()
        dip_angular_littlefinger = obs[24]

        return dip_angular_littlefinger

    def cmc_angular_thumb(self):
        # Angular position of CMC (carpometacarpal) joint of the thumb
        # Horizontal and Vertical
        obs = self._get_obs()
        cmc_angular_thumb = obs[25:27]

        return cmc_angular_thumb

    def mcp_angular_position_thumb(self):
        # Angular position of MCP(metacarpophalangeal, knuckle) joint of the thumb
        # Horizontal and Vertical
        obs = self._get_obs()
        mcp_angular_thumb = obs[27:29]

        return mcp_angular_thumb

    def ip_angular_thumb(self):
        # Angular position of the IP (Interphalangeal) joint of the thumb
        obs = self._get_obs()
        ip_angular_thumb = obs[29]

        return ip_angular_thumb

    def positional_difference_ball(self):
        # Get xyz positional difference from the palm to the ball
        # ball_position - palm_position
        obs = self._get_obs()
        ball_positional_difference = obs[30:33]

        return ball_positional_difference

    def positional_difference_target(self):
        # Get xyz positional difference from the palm to the target
        # target_position - palm_position
        obs = self._get_obs()
        target_positional_difference = obs[33:36]

        return target_positional_difference

    def positional_difference_from_ball_to_target(self):
        # Get xyz positional difference from the ball to the target
        # target_position - ball_position
        obs = self._get_obs()
        ball_target_postional_difference = obs[36:]

        return ball_target_postional_difference

    def compute_reward_0(self):
        # We define our reward components here
        positional_difference_ball = self.positional_difference_ball()
        distance_to_ball = np.linalg.norm(positional_difference_ball)
        
        # Reward component to minimize the distance to the ball
        reward_distance_to_ball = -np.tanh(distance_to_ball)
        reward_weight_distance_to_ball = 1.0  # Weight for this component
        
        # Total reward
        reward = reward_weight_distance_to_ball * reward_distance_to_ball
        
        # Dictionary of reward components for potential debugging and analysis
        reward_dict = {
            'distance_to_ball': reward_distance_to_ball
        }
        
        return reward, reward_dict
    
    def compute_reward_1(self):
        # Getting positional difference between palm and ball
        positional_difference_ball = self.positional_difference_ball()
        # Calculating the norm of positional difference for magnitude
        ball_distance_penalty = np.linalg.norm(positional_difference_ball)
    
        # Penalty for being further from the ball encourages closer positioning
        positional_difference_penalty_weight = -1.0
        total_reward = positional_difference_penalty_weight * ball_distance_penalty
    
        # Dictionary for individual reward components
        reward_dict = {
            "positional_difference_ball_penalty": positional_difference_penalty_weight * ball_distance_penalty,
        }
    
        return total_reward, reward_dict
    
    def compute_reward_2(self):
        # Extract the positional difference of the palm to the target
        positional_difference_target = self.positional_difference_target()
        
        # Reward components
        target_approach_weight = -1.0  # Encourage decreasing the distance to the target
        target_approach_reward = np.linalg.norm(positional_difference_target)
        
        # Total reward calculation
        total_reward = target_approach_weight * target_approach_reward
        
        # Construct the reward dictionary
        reward_dict = {
            'target_approach_reward': target_approach_reward,
        }
        
        return total_reward, reward_dict
    
    def compute_reward_3(self):
        # Calculate the positional difference from ball to target
        ball_target_difference = self.positional_difference_from_ball_to_target()
        ball_to_target_distance = np.linalg.norm(ball_target_difference)
    
        # Components of the reward function
        distance_to_target_reward = -np.tanh(ball_to_target_distance)
        reward_weight = 1.0  # Weighting parameter for the distance reward component
    
        # Calculate total reward
        total_reward = reward_weight * distance_to_target_reward
    
        # Dictionary of reward components
        reward_components = {
            'distance_to_target_reward': distance_to_target_reward,
        }
    
        return total_reward, reward_components
    
    # Function to loop through compute_reward_X functions and sum their outputs
    def compute_reward_curriculum(self):
        total_reward = 0
        total_reward_dict = {}
        n = 3
        for i in range(n + 1):  # Including n, hence n + 1
            # Construct the function name based on i
            function_name = f'compute_reward_{i}'
            # Get the function by name and call it
            function = getattr(self, function_name, None)
            if function:
                # Call the function and add its return value to the total sum
                reward, reward_dict = function()
                total_reward += reward
                total_reward_dict.update(reward_dict)
            else:
                raise NameError(f"Function {function_name} not found.")
        return total_reward, total_reward_dict