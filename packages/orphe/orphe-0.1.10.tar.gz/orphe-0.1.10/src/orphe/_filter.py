from intdash import DataFilter
from intdash import DataType


def get_intdash_data_filter():
    filters = []

    # L_SHOES_JSON
    # R_SHOES_JSON
    for i in ['L', 'R']:
        data_id = i + '_SHOES_JSON'
        filters.append(DataFilter(
            data_type=DataType.string.value, data_id=data_id, channel=1))

    for i in ['L', 'R']:
        for j in ['SHOES_QUATERNION', 'SHOES_ACC', 'SHOES_ACC_OF_GRAVITY', 'SHOES_EULER_ANGLE', 'SHOES_ANGULAR_VELOCITY', ]:
            for k in ['W', 'X', 'Y', 'Z']:
                data_id = i + '_' + j + '_' + k
                filters.append(DataFilter(
                    data_type=DataType.float.value, data_id=data_id, channel=1))

    # L_CADENCE, L_SPEED, L_STRIDE, L_CONTINUOUSSTANSPHASEDURATION, L_DURATION, L_LANDINGFORCE, L_PRONATION, L_STANCEPHASEDURATIONE, L_STRIDEMAXIMUMVERTICALHEIGHT, L_STRIKEANGLE, L_SWINGPHASEDURATION, L_TOEOFFANGLE
    # R_CADENCE, R_SPEED, R_STRIDE, R_CONTINUOUSSTANSPHASEDURATION, R_DURATION, R_LANDINGFORCE, R_PRONATION, R_STANCEPHASEDURATIONE, R_STRIDEMAXIMUMVERTICALHEIGHT, R_STRIKEANGLE, R_SWINGPHASEDURATION, R_TOEOFFANGLE
    for i in ['L', 'R']:
        for j in ['STRIDE', 'CADENCE', 'SPEED', 'PRONATION', 'LANDINGFORCE', 'DURATION', 'SWINGPHASEDURATION', 'CONTINUOUSSTANSPHASEDURATION', 'STANCEPHASEDURATIONE', 'STRIKEANGLE', 'TOEOFFANGLE', 'STRIDEMAXIMUMVERTICALHEIGHT']:
            data_id = i + '_' + j
            for k in [2, 3]:
                filters.append(DataFilter(
                    data_type=DataType.float.value, data_id=data_id, channel=k))

    # STRIDE, CADENCE, SPEED
    for j in ['STRIDE', 'CADENCE', 'SPEED', 'PRONATION', 'LANDINGFORCE', 'DURATION', 'SWINGPHASEDURATION', 'STANCEPHASEDURATIONE', 'STRIKEANGLE', 'TOEOFFANGLE', 'STRIDEMAXIMUMVERTICALHEIGHT']:
        data_id = j
        for k in [1, 2, 3, 4]:
            filters.append(DataFilter(
                data_type=DataType.float.value, data_id=data_id, channel=k))
    
    # 説明変数
    for i in ['L', 'R']:
        for j in ['LV_INITIALCONTACTACCELERATION', 'LV_INITIALCONTACTANGULARVELOCITY', 'LV_TOEOFFACCELERATION', 'LV_TOEOFFANGULARVELOCITY', 'LV_SWINGPHASESTRIDEVELOCITY']:
            for m in ['MIN', 'MAX']:
                for p in ['X', 'Y', 'Z']:
                    data_id = i + '_' + j + m + '_' + p
                    for k in [1, 2, 3, 4]:
                        filters.append(DataFilter(
                            data_type=DataType.float.value, data_id=data_id, channel=k))
                            
    for j in ['LV_INITIALCONTACTACCELERATION', 'LV_INITIALCONTACTANGULARVELOCITY', 'LV_TOEOFFACCELERATION', 'LV_TOEOFFANGULARVELOCITY', 'LV_SWINGPHASESTRIDEVELOCITY']:
        for m in ['MIN', 'MAX']:
            for p in ['X', 'Y', 'Z']:
                data_id = i + '_' + j + m + '_' + p
                for k in [1, 2, 3, 4]:
                    filters.append(DataFilter(
                        data_type=DataType.float.value, data_id=data_id, channel=k))
    
    # 3次元パラメータ
    for i in ['L', 'R']:
        for j in ['CTD_ACCELERATION', 'CTD_ANGULARVELOCITY', 'CTD_STRIDEGLOBALACCELERATION', 'CTD_STRIDEVELOCITY', 'CTD_STRIDEDISPLACEMENT', 'CTD_STANCEPHASEANGLE']:
            for p in ['X', 'Y', 'Z']:
                data_id = i + '_' + j + '_' + p
                for k in [1, 2, 3, 4]:
                    filters.append(DataFilter(
                        data_type=DataType.float.value, data_id=data_id, channel=k))
        for j in ['CTD_INITIALCONTACTFLAG', 'CTD_FOOTFLATFLAG', 'CTD_TOEOFFFLAG', 'CTD_VERTICALJUMPFLAG']:
            data_id = i + '_' + j
            for k in [1, 2, 3, 4]:
                filters.append(DataFilter(
                    data_type=DataType.float.value, data_id=data_id, channel=k))
    
    for j in ['CTD_ACCELERATION', 'CTD_ANGULARVELOCITY', 'CTD_STRIDEGLOBALACCELERATION', 'CTD_STRIDEVELOCITY', 'CTD_STRIDEDISPLACEMENT', 'CTD_STANCEPHASEANGLE']:
        for p in ['X', 'Y', 'Z']:
            data_id = i + '_' + j + '_' + p
            for k in [1, 2, 3, 4]:
                filters.append(DataFilter(
                    data_type=DataType.float.value, data_id=data_id, channel=k))
    for j in ['CTD_INITIALCONTACTFLAG', 'CTD_FOOTFLATFLAG', 'CTD_TOEOFFFLAG', 'CTD_VERTICALJUMPFLAG']:
        data_id = i + '_' + j
        for k in [1, 2, 3, 4]:
            filters.append(DataFilter(
                data_type=DataType.float.value, data_id=data_id, channel=k))


    # TF_POSE_ARM_L, TF_POSE_HIP_L, TF_POSE_KNEE_L
    # TF_POSE_ARM_R, TF_POSE_HIP_R, TF_POSE_KNEE_R
    for i in ['ARM', 'HIP', 'KNEE']:
        for j in ['L', 'R']:
            data_id = 'TF_POSE_' + i + '_' + j
            filters.append(DataFilter(
                data_type=DataType.float.value, data_id=data_id, channel=2))

    # TF_POSE_L_ANKLE_X, TF_POSE_L_ANKLE_Y, TF_POSE_L_ELBOW_X, TF_POSE_L_ELBOW_Y, TF_POSE_L_EYE_X, TF_POSE_L_EYE_Y, TF_POSE_L_HIP_X, TF_POSE_L_HIP_Y, TF_POSE_L_KNEE_X, TF_POSE_L_KNEE_Y, TF_POSE_L_SHOULDER_X, TF_POSE_L_SHOULDER_Y, TF_POSE_L_WRIST_X, TF_POSE_L_WRIST_Y, TF_POSE_L_EAR_X, TF_POSE_L_EAR_Y
    # TF_POSE_R_ANKLE_X, TF_POSE_R_ANKLE_Y, TF_POSE_R_ELBOW_X, TF_POSE_R_ELBOW_Y, TF_POSE_R_EYE_X, TF_POSE_R_EYE_Y, TF_POSE_R_HIP_X, TF_POSE_R_HIP_Y, TF_POSE_R_KNEE_X, TF_POSE_R_KNEE_Y, TF_POSE_R_SHOULDER_X, TF_POSE_R_SHOULDER_Y, TF_POSE_R_WRIST_X, TF_POSE_R_WRIST_Y, TF_POSE_R_EAR_X, TF_POSE_R_EAR_Y
    for i in ['L', 'R']:
        for j in ['ANKLE', 'ELBOW', 'EYE', 'HIP', 'KNEE', 'SHOULDER', 'WRIST', 'EAR']:
            for k in ['X', 'Y']:
                data_id = 'TF_POSE_' + i + '_' + j + '_' + k
                filters.append(DataFilter(
                    data_type=DataType.float.value, data_id=data_id, channel=2))

    # TF_POSE_NECK, TF_POSE_PELVIS, TF_POSE_SHOULDER_LINE, TF_POSE_TRUNK
    for i in ['NECK', 'PELVIS', 'SHOULDER_LINE', 'TRUNK']:
        data_id = 'TF_POSE_' + i
        filters.append(DataFilter(
            data_type=DataType.float.value, data_id=data_id, channel=2))

    # TF_POSE_NECK_X, TF_POSE_NOSE_X
    # TF_POSE_NECK_Y, TF_POSE_NOSE_Y
    for i in ['NECK', 'NOSE']:
        for j in ['X', 'Y']:
            data_id = 'TF_POSE_' + i + '_' + j
            filters.append(DataFilter(
                data_type=DataType.float.value, data_id=data_id, channel=2))

    # ORPHE_CORE
    for i in [1, 2, 3, 4]:
        filters.append(DataFilter(data_type=DataType.string.value,
                       data_id="ORPHE_CORE", channel=i))

    # jpeg	JPEG	2
    # StrideTimeCV	Float	2
    # cutoff_StrideTimeCV	Float	2

    # for u in filters:
    #     print(
    #         f"data_id: {u.data_id}, data_type: {u.data_type}, channel: {u.channel}")

    filters.append(
        DataFilter(data_type=DataType.float.value, data_id="Reference_Time", channel=1))

    return filters


# if __name__ == '__main__':
#     filters = get_intdash_data_filter()
