# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
import warnings
from typing import Union, List, Dict

import pandas


class Position3(object):
    x: float = None
    y: float = None
    z: float = None

class GaitFV(object):
    initial_contact_acceleration_min: Position3 = None
    initial_contact_acceleration_max: Position3 = None
    initial_contact_angular_velocity_min: Position3 = None
    initial_contact_angular_velocity_max: Position3 = None
    toe_off_acceleration_min: Position3 = None
    toe_off_acceleration_max: Position3 = None
    toe_off_angular_velocity_min: Position3 = None
    toe_off_angular_velocity_max: Position3 = None
    swing_phase_stride_velocity_min: Position3 = None
    swing_phase_stride_velocity_max: Position3 = None
    
    def __init__(self) -> None:
        self.initial_contact_acceleration_min = Position3()
        self.initial_contact_acceleration_max = Position3()
        self.initial_contact_angular_velocity_min = Position3()
        self.initial_contact_angular_velocity_max = Position3()
        self.toe_off_acceleration_min = Position3()
        self.toe_off_acceleration_max = Position3()
        self.toe_off_angular_velocity_min = Position3()
        self.toe_off_angular_velocity_max = Position3()
        self.swing_phase_stride_velocity_min = Position3()
        self.swing_phase_stride_velocity_max = Position3()
        
    def _set(self, key: str, value: float):
        if key == "FV_INITIALCONTACTACCELERATIONMIN_X":
            self.initial_contact_acceleration_min.x = value
        elif key == "FV_INITIALCONTACTACCELERATIONMIN_Y":
            self.initial_contact_acceleration_min.y = value
        elif key == "FV_INITIALCONTACTACCELERATIONMIN_Z":
            self.initial_contact_acceleration_min.z = value
        elif key == "FV_INITIALCONTACTACCELERATIONMAX_X":
            self.initial_contact_acceleration_max.x = value
        elif key == "FV_INITIALCONTACTACCELERATIONMAX_Y":
            self.initial_contact_acceleration_max.y = value
        elif key == "FV_INITIALCONTACTACCELERATIONMAX_Z":
            self.initial_contact_acceleration_max.z = value            
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMIN_X":
            self.initial_contact_angular_velocity_min.x = value
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMIN_Y":
            self.initial_contact_angular_velocity_min.y = value
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMIN_Z":
            self.initial_contact_angular_velocity_min.z = value
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMAX_X":
            self.initial_contact_angular_velocity_max.x = value
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMAX_Y":
            self.initial_contact_angular_velocity_max.y = value
        elif key == "FV_INITIALCONTACTANGULARVELOCITYMAX_Z":
            self.initial_contact_angular_velocity_max.z = value            
        elif key == "FV_TOEOFFACCELERATIONMIN_X":
            self.toe_off_acceleration_min.x = value
        elif key == "FV_TOEOFFACCELERATIONMIN_Y":
            self.toe_off_acceleration_min.y = value
        elif key == "FV_TOEOFFACCELERATIONMIN_Z":
            self.toe_off_acceleration_min.z = value
        elif key == "FV_TOEOFFACCELERATIONMAX_X":
            self.toe_off_acceleration_max.x = value
        elif key == "FV_TOEOFFACCELERATIONMAX_Y":
            self.toe_off_acceleration_max.y = value
        elif key == "FV_TOEOFFACCELERATIONMAX_Z":
            self.toe_off_acceleration_max.z = value            
        elif key == "FV_TOEOFFANGULARVELOCITYMIN_X":
            self.toe_off_angular_velocity_min.x = value
        elif key == "FV_TOEOFFANGULARVELOCITYMIN_Y":
            self.toe_off_angular_velocity_min.y = value
        elif key == "FV_TOEOFFANGULARVELOCITYMIN_Z":
            self.toe_off_angular_velocity_min.z = value
        elif key == "FV_TOEOFFANGULARVELOCITYMAX_X":
            self.toe_off_angular_velocity_max.x = value
        elif key == "FV_TOEOFFANGULARVELOCITYMAX_Y":
            self.toe_off_angular_velocity_max.y = value
        elif key == "FV_TOEOFFANGULARVELOCITYMAX_Z":
            self.toe_off_angular_velocity_max.z = value            
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMIN_X":
            self.swing_phase_stride_velocity_min.x = value
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMIN_Y":
            self.swing_phase_stride_velocity_min.y = value
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMIN_Z":
            self.swing_phase_stride_velocity_min.z = value
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMAX_X":
            self.swing_phase_stride_velocity_max.x = value
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMAX_Y":
            self.swing_phase_stride_velocity_max.y = value
        elif key == "FV_SWINGPHASESTRIDEVELOCITYMAX_Z":
            self.swing_phase_stride_velocity_max.z = value

class GaitCTD(object):
    acceleration: Position3 = None
    angular_velocity: Position3 = None
    stride_global_acceleration: Position3 = None
    stride_velocity: Position3 = None
    stride_displacement: Position3 = None
    stance_phase_angle: Position3 = None
    initial_contact_flag: float = None
    foot_flat_flag: float = None
    toe_off_flag: float = None
    vertical_jump_flag: float = None
    
    def __init__(self) -> None:
        self.acceleration: Position3 = Position3()
        self.angular_velocity: Position3 = Position3()
        self.stride_global_acceleration: Position3 = Position3()
        self.stride_velocity: Position3 = Position3()
        self.stride_displacement: Position3 = Position3()
        self.stance_phase_angle: Position3 = Position3()
        
    def _set(self, key: str, value: float):
        if key == "CTD_ACCELERATION_X":
            self.acceleration.x = value
        elif key == "CTD_ACCELERATION_Y":
            self.acceleration.y = value
        elif key == "CTD_ACCELERATION_Z":
            self.acceleration.z = value
        elif key == "CTD_ANGULARVELOCITY_X":
            self.angular_velocity.x = value
        elif key == "CTD_ANGULARVELOCITY_Y":
            self.angular_velocity.y = value
        elif key == "CTD_ANGULARVELOCITY_Z":
            self.angular_velocity.z = value
        elif key == "CTD_STRIDEGLOBALACCELERATION_X":
            self.stride_global_acceleration.x = value
        elif key == "CTD_STRIDEGLOBALACCELERATION_Y":
            self.stride_global_acceleration.y = value
        elif key == "CTD_STRIDEGLOBALACCELERATION_Z":
            self.stride_global_acceleration.z = value
        elif key == "CTD_STRIDEVELOCITY_X":
            self.stride_velocity.x = value
        elif key == "CTD_STRIDEVELOCITY_Y":
            self.stride_velocity.y = value
        elif key == "CTD_STRIDEVELOCITY_Z":
            self.stride_velocity.z = value
        elif key == "CTD_STRIDEDISPLACEMENT_X":
            self.stride_displacement.x = value
        elif key == "CTD_STRIDEDISPLACEMENT_Y":
            self.stride_displacement.y = value
        elif key == "CTD_STRIDEDISPLACEMENT_Z":
            self.stride_displacement.z = value
        elif key == "CTD_STANCEPHASEANGLE_X":
            self.stance_phase_angle.x = value
        elif key == "CTD_STANCEPHASEANGLE_Y":
            self.stance_phase_angle.y = value
        elif key == "CTD_STANCEPHASEANGLE_Z":
            self.stance_phase_angle.z = value
        elif key == "CTD_INITIALCONTACTFLAG":
            self.initial_contact_flag = value
        elif key == "CTD_FOOTFLATFLAG":
            self.foot_flat_flag = value
        elif key == "CTD_TOEOFFFLAG":
            self.toe_off_flag = value
        elif key == "CTD_VERTICALJUMPFLAG":
            self.vertical_jump_flag = value

class Gait(object):
    time: pandas.Timedelta
    quaternion_w: float = None
    quaternion_x: float = None
    quaternion_y: float = None
    quaternion_z: float = None
    angular_velocity_x: float = None
    angular_velocity_y: float = None
    angular_velocity_z: float = None
    acc_x: float = None
    acc_y: float = None
    acc_z: float = None
    gravity_x: float = None
    gravity_y: float = None
    gravity_z: float = None
    euler_x: float = None
    euler_y: float = None
    euler_z: float = None

    analyzed: bool = False

    stride: float = None
    cadence: float = None
    speed: float = None
    pronation: float = None
    landing_force: float = None

    duration: float = None
    swing_phase_duration: float = None
    stance_phase_duration: float = None
    continuous_stance_phase_duration: float = None

    strike_angle: float = None
    toe_off_angle: float = None

    foot_strike: float = None
    pronation_euler_angles: Position3 = None
    propulsion_pronation_euler_angles: Position3 = None
    coninuous_pronation_euler_angles: Position3 = None
    foot_angle: float = None
    lateral_maximum_displacement: float = None
    lateral_minimum_displacement: float = None
    previous_loading_rate: float = None
    previous_kicking_force: float = None
    max_knee_flexion_angle: float = None
    delta_displacement: Position3 = None

    stride_maximum_vertical_height: float = None

    fv: GaitFV = None
    ctd: GaitCTD = None

    def __init__(self, time: pandas.Timedelta) -> None:
        self.time = time
        self.fv = GaitFV()
        self.ctd = GaitCTD()
        self.pronation_euler_angles = Position3()
        self.propulsion_pronation_euler_angles = Position3()
        self.coninuous_pronation_euler_angles = Position3()
        self.delta_displacement = Position3()

    def _set(self, key: str, value: float):
        if key == "SHOES_QUATERNION_W":
            self.quaternion_w: float = value
        elif key == "SHOES_QUATERNION_X":
            self.quaternion_x: float = value
        elif key == "SHOES_QUATERNION_Y":
            self.quaternion_y: float = value
        elif key == "SHOES_QUATERNION_Z":
            self.quaternion_z: float = value
        elif key == "SHOES_ANGULAR_VELOCITY_X":
            self.angular_velocity_x: float = value
        elif key == "SHOES_ANGULAR_VELOCITY_Y":
            self.angular_velocity_y: float = value
        elif key == "SHOES_ANGULAR_VELOCITY_Z":
            self.angular_velocity_z: float = value
        elif key == "SHOES_ACC_X":
            self.acc_x: float = value
        elif key == "SHOES_ACC_Y":
            self.acc_y: float = value
        elif key == "SHOES_ACC_Z":
            self.acc_z: float = value
        elif key == "SHOES_ACC_OF_GRAVITY_X":
            self.gravity_x: float = value
        elif key == "SHOES_ACC_OF_GRAVITY_Y":
            self.gravity_y: float = value
        elif key == "SHOES_ACC_OF_GRAVITY_Z":
            self.gravity_z: float = value
        elif key == "SHOES_EULER_ANGLE_X":
            self.euler_x: float = value
        elif key == "SHOES_EULER_ANGLE_Y":
            self.euler_y: float = value
        elif key == "SHOES_EULER_ANGLE_Z":
            self.euler_z: float = value
        elif key == "STRIDE":
            self.analyzed = True
            self.stride: float = value
        elif key == "CADENCE":
            self.analyzed = True
            self.cadence: float = value
        elif key == "SPEED":
            self.analyzed = True
            self.speed: float = value
        elif key == "PRONATION":
            self.analyzed = True
            self.pronation: float = value
        elif key == "LANDINGFORCE":
            self.analyzed = True
            self.landing_force: float = value
        elif key == "DURATION":
            self.analyzed = True
            self.duration: float = value
        elif key == "SWINGPHASEDURATION":
            self.analyzed = True
            self.swing_phase_duration: float = value
        elif key == "STANCEPHASEDURATIONE":
            self.analyzed = True
            self.stance_phase_duration: float = value
        elif key == "CONTINUOUSSTANSPHASEDURATION":
            self.analyzed = True
            self.continuous_stance_phase_duration: float = value
        elif key == "STRIKEANGLE":
            self.analyzed = True
            self.strike_angle: float = value
        elif key == "TOEOFFANGLE":
            self.analyzed = True
            self.toe_off_angle: float = value
        elif key == "STRIDEMAXIMUMVERTICALHEIGHT":
            self.analyzed = True
            self.stride_maximum_vertical_height: float = value
        elif key == "FOOTSTRIKE":
            self.analyzed = True
            self.foot_strike: float = value
        elif key == "PRONATIONEULERANGLES_X":
            self.analyzed = True
            self.pronation_euler_angles.x = value
        elif key == "PRONATIONEULERANGLES_Y":
            self.analyzed = True
            self.pronation_euler_angles.y = value
        elif key == "PRONATIONEULERANGLES_Z":
            self.analyzed = True
            self.pronation_euler_angles.z = value
        elif key == "PROPULSIONPRONATIONEULERANGLES_X":
            self.analyzed = True
            self.propulsion_pronation_euler_angles.x = value
        elif key == "PROPULSIONPRONATIONEULERANGLES_Y":
            self.analyzed = True
            self.propulsion_pronation_euler_angles.y = value
        elif key == "PROPULSIONPRONATIONEULERANGLES_Z":
            self.analyzed = True
            self.propulsion_pronation_euler_angles.z = value
        elif key == "CONTINUOUSPRONATIONEULERANGLES_X":
            self.analyzed = True
            self.coninuous_pronation_euler_angles.x = value
        elif key == "CONTINUOUSPRONATIONEULERANGLES_Y":
            self.analyzed = True
            self.coninuous_pronation_euler_angles.y = value
        elif key == "CONTINUOUSPRONATIONEULERANGLES_Z":
            self.analyzed = True
            self.coninuous_pronation_euler_angles.z = value
        elif key == "FOOTANGLE":
            self.analyzed = True
            self.foot_angle: float = value
        elif key == "LATERALMAXIMUMDISPLACEMENT":
            self.analyzed = True
            self.lateral_maximum_displacement: float = value
        elif key == "LATERALMINIMUMDISPLACEMENT":
            self.analyzed = True
            self.lateral_minimum_displacement: float = value
        elif key == "PREVIOUSLOADINGRATE":
            self.analyzed = True
            self.previous_loading_rate: float = value
        elif key == "PREVIOUSKICKINGFORCE":
            self.analyzed = True
            self.previous_kicking_force: float = value
        elif key == "MAXKNEEFLEXIONANGLE":
            self.analyzed = True
            self.max_knee_flexion_angle: float = value
        elif key == "DELTADISPLACEMENT_X":
            self.analyzed = True
            self.delta_displacement.x = value
        elif key == "DELTADISPLACEMENT_Y":
            self.analyzed = True
            self.delta_displacement.y = value
        elif key == "DELTADISPLACEMENT_Z":
            self.analyzed = True
            self.delta_displacement.z = value
        else:
            self.fv._set(key, value)
            self.ctd._set(key, value)

        # if self.analyzed:
        #     print(f"gait. analyzed key: {key}")

class GaitAnalysis(object):
    _left: Union[List[Gait], Gait] = []
    _right: Union[List[Gait], Gait] = []
    _stored: Dict[int, List[Gait]] = {}
    _realtime: Dict[int, Gait] = {}

    @property
    def left(self) -> Union[List[Gait], Gait]:
        warnings.warn("'left' Property is deprecated.")
        return self._left

    @left.setter
    def left(self, value: Union[List[Gait], Gait]):
        self._left = value

    @property
    def right(self) -> Union[List[Gait], Gait]:
        warnings.warn("'right' Property is deprecated.")
        return self._right

    @right.setter
    def right(self, value: Union[List[Gait], Gait]):
        self._right = value

    @property
    def stored(self) -> Dict[int, List[Gait]]:
        return self._stored

    @stored.setter
    def stored(self, value: Dict[int, List[Gait]]):
        self._stored = value

    @property
    def realtime(self) -> Dict[int, Gait]:
        return self._realtime

    @realtime.setter
    def realtime(self, value: Dict[int, Gait]):
        self._realtime = value
