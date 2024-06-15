import omni.isaac.lab.sim as sim_utils
from omni.isaac.lab.actuators import IdealPDActuatorCfg
from omni.isaac.lab.assets.articulation import ArticulationCfg

from orbit.berkeley_humanoid.assets import ORBIT_ASSET_DIR

BERKELEY_HUMANOID_HXX_ACTUATOR_CFG = IdealPDActuatorCfg(
    joint_names_expr=[".*HR", ".*HAA"],
    effort_limit=20.0,
    velocity_limit=23,
    stiffness={".*": 10.0},
    damping={".*": 1.5},
)

BERKELEY_HUMANOID_HFE_ACTUATOR_CFG = IdealPDActuatorCfg(
    joint_names_expr=[".*HFE"],
    effort_limit=30.0,
    velocity_limit=20,
    stiffness={".*": 15.0},
    damping={".*": 1.5},
)

BERKELEY_HUMANOID_KFE_ACTUATOR_CFG = IdealPDActuatorCfg(
    joint_names_expr=[".*KFE"],
    effort_limit=30.0,
    velocity_limit=14,
    stiffness={".*": 15.0},
    damping={".*": 1.5},
)

BERKELEY_HUMANOID_FFE_ACTUATOR_CFG = IdealPDActuatorCfg(
    joint_names_expr=[".*FFE"],
    effort_limit=20.0,
    velocity_limit=23,
    stiffness={".*": 1.0},
    damping={".*": 0.1},
)

BERKELEY_HUMANOID_FAA_ACTUATOR_CFG = IdealPDActuatorCfg(
    joint_names_expr=[".*FAA"],
    effort_limit=5.0,
    velocity_limit=42,
    stiffness={".*": 1.0},
    damping={".*": 0.1},
)

BERKELEY_HUMANOID_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=f"{ORBIT_ASSET_DIR}/Robots/berkeley_humanoid.usd",
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True, solver_position_iteration_count=4, solver_velocity_iteration_count=0
        ),
        # collision_props=sim_utils.CollisionPropertiesCfg(contact_offset=0.02, rest_offset=0.0),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.515),
        joint_pos={
            'LL_HR': -0.071,
            'LR_HR': 0.071,
            'LL_HAA': 0.103,
            'LR_HAA': -0.103,
            'LL_HFE': -0.463,
            'LR_HFE': -0.463,
            'LL_KFE': 0.983,
            'LR_KFE': 0.983,
            'LL_FFE': -0.350,
            'LR_FFE': -0.350,
            'LL_FAA': 0.126,
            'LR_FAA': -0.126
        },
    ),
    actuators={"hxx": BERKELEY_HUMANOID_HXX_ACTUATOR_CFG, "hfe": BERKELEY_HUMANOID_HFE_ACTUATOR_CFG,
               "kfe": BERKELEY_HUMANOID_KFE_ACTUATOR_CFG, "ffe": BERKELEY_HUMANOID_FFE_ACTUATOR_CFG,
               "faa": BERKELEY_HUMANOID_FAA_ACTUATOR_CFG},
    soft_joint_pos_limit_factor=0.95,
)
