import pandas
from typing import List


class Position2(object):
    x: float = None
    y: float = None

class PoseAngle(object):
    neck : float = None    
    shoulder_line : float = None
    trunk : float = None
    pelvis : float = None
    arm_left : float = None
    arm_right : float = None
    hip_left : float = None
    hip_right : float = None
    knee_left : float = None
    knee_right : float = None            
    
class PosePosition(object):
    nose : Position2 = None
    neck : Position2 = None
    shoulder_right : Position2 = None
    shoulder_left : Position2 = None
    elbow_left : Position2 = None
    elbow_right : Position2 = None
    wrist_right : Position2 = None
    wrist_left : Position2 = None
    hip_right : Position2 = None
    hip_left : Position2 = None
    ankle_right : Position2 = None
    ankle_left : Position2 = None
    knee_left : Position2 = None
    knee_right : Position2 = None
    eye_left : Position2 = None 
    eye_right : Position2 = None 
    ear_left : Position2 = None 
    ear_right : Position2 = None

    def __init__(self) -> None:
        self.nose = Position2()
        self.neck = Position2()
        self.shoulder_right = Position2()
        self.shoulder_left = Position2()
        self.elbow_left = Position2()
        self.elbow_right = Position2()
        self.wrist_right = Position2()
        self.wrist_left = Position2()
        self.hip_right = Position2()
        self.hip_left = Position2()
        self.ankle_right = Position2()
        self.ankle_left = Position2()
        self.knee_left = Position2()
        self.knee_right = Position2()
        self.eye_left = Position2()
        self.eye_right = Position2()
        self.ear_left = Position2()
        self.ear_right = Position2()

class Pose(object):
    time : pandas.Timedelta
    angle: PoseAngle = None         # 膝の角度、首の角度、腰の角度
    position: PosePosition = None   # 目のXY座標、鼻のXY座標

    def __init__(self, time : pandas.Timedelta) -> None:
        self.time = time
        self.angle = PoseAngle()
        self.position = PosePosition()
    
    def _set(self, key : str, value : float):
        if key == 'TF_POSE_HIP_R':
            self.angle.hip_right = value
        elif key == 'TF_POSE_HIP_L':
            self.angle.hip_left = value
        elif key == 'TF_POSE_KNEE_R':
            self.angle.knee_right = value
        elif key == 'TF_POSE_KNEE_L':
            self.angle.knee_left = value
        elif key == 'TF_POSE_ARM_R':
            self.angle.arm_right = value
        elif key == 'TF_POSE_ARM_L':
            self.angle.arm_left = value
        elif key == 'TF_POSE_TRUNK':
            self.angle.trunk = value
        elif key == 'TF_POSE_NECK':
            self.angle.neck = value
        elif key == 'TF_POSE_PELVIS':
            self.angle.pelvis = value
        elif key == 'TF_POSE_SHOULDER_LINE':
            self.angle.shoulder_line = value
        elif key == 'TF_POSE_NOSE_X':
            self.position.nose.x = value
        elif key == 'TF_POSE_NOSE_Y':
            self.position.nose.y = value
        elif key == 'TF_POSE_NECK_X':
            self.position.neck.x = value
        elif key == 'TF_POSE_NECK_Y':
            self.position.neck.y = value
        elif key == 'TF_POSE_R_SHOULDER_X':
            self.position.shoulder_right.x = value
        elif key == 'TF_POSE_R_SHOULDER_Y':
            self.position.shoulder_right.y = value
        elif key == 'TF_POSE_R_ELBOW_X':
            self.position.elbow_right.x = value
        elif key == 'TF_POSE_R_ELBOW_Y':
            self.position.elbow_right.y = value
        elif key == 'TF_POSE_R_WRIST_X':
            self.position.wrist_right.x = value
        elif key == 'TF_POSE_R_WRIST_Y':
            self.position.wrist_right.y = value
        elif key == 'TF_POSE_L_SHOULDER_X':
            self.position.shoulder_left.x = value
        elif key == 'TF_POSE_L_SHOULDER_Y':
            self.position.shoulder_left.y = value
        elif key == 'TF_POSE_L_ELBOW_Y':
            self.position.elbow_left.y = value
        elif key == 'TF_POSE_L_WRIST_X':
            self.position.wrist_left.x = value
        elif key == 'TF_POSE_L_WRIST_Y':
            self.position.wrist_left.y = value
        elif key == 'TF_POSE_R_HIP_X':
            self.position.hip_right.x = value
        elif key == 'TF_POSE_R_HIP_Y':
            self.position.hip_right.y = value
        elif key == 'TF_POSE_R_KNEE_X':
            self.position.knee_right.x = value
        elif key == 'TF_POSE_R_KNEE_Y':
            self.position.knee_right.y = value
        elif key == 'TF_POSE_R_ANKLE_X':
            self.position.ankle_right.x = value
        elif key == 'TF_POSE_R_ANKLE_Y':
            self.position.ankle_right.y = value
        elif key == 'TF_POSE_L_HIP_X':
            self.position.hip_left.x = value
        elif key == 'TF_POSE_L_HIP_Y':
            self.position.hip_left.y = value
        elif key == 'TF_POSE_L_KNEE_X':
            self.position.knee_left.x = value
        elif key == 'TF_POSE_L_KNEE_Y':
            self.position.knee_left.y = value
        elif key == 'TF_POSE_L_ANKLE_X':
            self.position.ankle_left.x = value
        elif key == 'TF_POSE_L_ANKLE_Y':
            self.position.ankle_left.y = value
        elif key == 'TF_POSE_R_EYE_X':
            self.position.eye_right.x = value
        elif key == 'TF_POSE_R_EYE_Y':
            self.position.eye_right.y = value
        elif key == 'TF_POSE_L_EYE_X':
            self.position.eye_left.x = value
        elif key == 'TF_POSE_L_EYE_Y':
            self.position.eye_left.y = value
        elif key == 'TF_POSE_R_EAR_X':
            self.position.ear_right.x = value
        elif key == 'TF_POSE_R_EAR_Y':
            self.position.ear_right.y = value
        elif key == 'TF_POSE_L_EAR_X':
            self.position.ear_left.x = value
        elif key == 'TF_POSE_L_EAR_Y':
            self.position.ear_left.y = value

        # print(f"pose. key: {key}")


class PoseAnalysis(object):
    _stored: List[Pose] = []
    _realtime: Pose = None

    @property
    def stored(self) -> List[Pose]:
        return self._stored

    @stored.setter
    def stored(self, value: List[Pose]):
        self._stored = value

    @property
    def realtime(self) -> Pose:
        return self._realtime

    @realtime.setter
    def realtime(self, value):
        self._realtime = value
