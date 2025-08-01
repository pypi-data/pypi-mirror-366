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
from json.decoder import JSONDecodeError
import intdash
import numpy as np
import json
import asyncio
import pandas
import time
import queue
from typing import Callable, Union, List, Dict
from xmlrpc.client import Boolean

from ._filter import get_intdash_data_filter
from ._gait import Gait, GaitAnalysis
from ._unit import Unit
from ._pose import Pose, PoseAnalysis

class AnalyticsValue(object):
    """ORPHE ANALYTICSから取得されたデータです。
    """
    basetime: pandas.Timestamp
    gait: GaitAnalysis
    pose: PoseAnalysis
    ref_times: List[pandas.Timedelta]

    def __init__(self, basetime: float, gait_analysis: GaitAnalysis, pose_analysis: PoseAnalysis, ref_times: List[pandas.Timedelta] = []) -> None:
        self.basetime = basetime
        self.gait = gait_analysis
        self.pose = pose_analysis
        self.ref_times = ref_times

class Analytics(object):
    """intdash REST サーバーに対するアクセスクライアントです。

    Args:
        url (str): ORPHE ANALYTICS REST API サーバーの URL
        token (str): エッジトークン

    .. note::
        認証情報として、 **トークン** が必要です。
    """

    _down_queue: queue.Queue = queue.Queue(maxsize=0)
    _up_queue: queue.Queue = queue.Queue(maxsize=0)
    _is_connected = False
    _current_value: AnalyticsValue = None
    _current_time: int = None

    def __init__(self, url: str, token: str = None) -> None:
        self.url: str = url
        self.token: str = token

        self._client: intdash.Client = intdash.Client(
            url=url,
            edge_token=token,
        )

    # 辞書データ変換
    _json_dict = {
        "quatW": "SHOES_QUATERNION_W",
        "quatX": "SHOES_QUATERNION_X",
        "quatY": "SHOES_QUATERNION_Y",
        "quatZ": "SHOES_QUATERNION_Z",
        "gyroX": "SHOES_ANGULAR_VELOCITY_X",
        "gyroY": "SHOES_ANGULAR_VELOCITY_Y",
        "gyroZ": "SHOES_ANGULAR_VELOCITY_Z",
        "accX": "SHOES_ACC_X",
        "accY": "SHOES_ACC_Y",
        "accZ": "SHOES_ACC_Z",
        "gravityX": "SHOES_ACC_OF_GRAVITY_X",
        "gravityY": "SHOES_ACC_OF_GRAVITY_Y",
        "gravityZ": "SHOES_ACC_OF_GRAVITY_Z",
        "eulerX": "SHOES_EULER_ANGLE_X",
        "eulerY": "SHOES_EULER_ANGLE_Y",
        "eulerZ": "SHOES_EULER_ANGLE_Z"
    }

    def analyze_channel_data(self, channel_data, is_before_multi_tenant=False) -> Union[List[Gait], Gait]:
        tmp: Dict[pandas.Timedelta, Gait] = {}
        for unit in channel_data:
            # Skip basetime.
            if unit.data.data_type.value == intdash.DataType.basetime.value:
                continue

            # 計測時間取得
            # total_time_seconds = unit.elapsed_time.total_seconds()
            elapsed_time = unit.elapsed_time
            if elapsed_time not in tmp and (unit.data.data_type.value == intdash.DataType.float.value or unit.data.data_type.value == intdash.DataType.string.value):
                gait = Gait(time=elapsed_time)
                tmp[elapsed_time] = gait

            # センサーデータを取得
            sensor_data = unit.data

            # Skip other data.
            if unit.data.data_type.value == intdash.DataType.float.value:
                if is_before_multi_tenant:
                    key = sensor_data.data_id[2:]
                else:
                    key = sensor_data.data_id

                gait = tmp[elapsed_time]
                gait._set(key, sensor_data.value)

            elif unit.data.data_type.value == intdash.DataType.string.value:
                try:
                    sensor_data_json = json.loads(sensor_data.value)
                    for key in self._json_dict:
                        gait = tmp[elapsed_time]
                        gait._set(self._json_dict[key], sensor_data_json[key])

                except json.JSONDecodeError:
                    continue

        return sorted(tmp.values(), key=lambda gait: gait.time)

    def analyze_pose_data(self, channel_data) -> Union[List[Pose], Pose]:
        tmp: Dict[pandas.Timedelta, Pose] = {}
        for unit in channel_data:
            # Skip basetime.
            if unit.data.data_type.value == intdash.DataType.basetime.value:
                continue

            # センサーデータを取得
            sensor_data = unit.data

            if (sensor_data.data_id[:8] != 'TF_POSE_'):
                continue

            # 計測時間取得
            elapsed_time = unit.elapsed_time
            if elapsed_time not in tmp and unit.data.data_type.value == intdash.DataType.float.value:
                pose = Pose(time=elapsed_time)
                tmp[elapsed_time] = pose

            # Skip other data.
            if unit.data.data_type.value == intdash.DataType.float.value:
                key = sensor_data.data_id
                pose = tmp[elapsed_time]
                pose._set(key, sensor_data.value)            

        return sorted(tmp.values(), key=lambda pose: pose.time)

    def analyze_reference_time(self, channel_data) -> List[pandas.Timedelta]:        

        tmp = [u for u in channel_data if u.channel == 1 and (
                u.data.data_type.value == intdash.DataType.float.value) and 
                u.data.data_id == 'Reference_Time']        

        times = [u.elapsed_time for u in tmp if u.data.value in [-9999, -9999.9]]
        # end = [{'value': u.data.value, 'elapsed_time': u.elapsed_time} for u in tmp if u.data.value in [9999]]

        if len(times) < 1:
            return []
        
        return times
        
        # if end[-1]['elapsed_time'] > start[-1]['elapsed_time']:
        #     duration = end[-1]['elapsed_time'] - start[-1]['elapsed_time']
        #     return duration
        
        # if len(end) > 1:
        #     duration = end[-1]['elapsed_time'] - start[-2]['elapsed_time']
        #     return duration

        # return 0

    def is_before_multi_tenant(self, unit_data: List[Unit]) -> bool:
        for u in unit_data:
            if u.channel == 1 and (u.data.data_id[:12] in ["L_SHOES_JSON", "R_SHOES_JSON"]):
                return True
        return False

    def load(self, measurement_uuid: str, debug: bool = False) -> AnalyticsValue:
        # 計測の取得
        print(f'Search measurement uuid: {measurement_uuid}', flush=True)
        m = self._client.measurements.get(
            uuid=measurement_uuid
        )

        # 計測がない場合終了
        if debug:
            print(m)
        if m == np.nan:
            print("No measurements were found.", flush=True)
            return

        # ユニットの取得（小数点のみ）
        print(f'Load measurement: {measurement_uuid}', flush=True)
        res = self._client.units.list(
            start=m.basetime,
            end=m.basetime + m.duration * 2, # endの時刻時点の計測は検索対象に含まれないので、余分に2倍しておく
            measurement_uuid=m.uuid,
            limit=1000000,
            iterator=True,
            # id_queries=[
            #     intdash.IdQuery(data_type=intdash.DataType.float),
            #     intdash.IdQuery(data_type=intdash.DataType.string)
            # ],
            exit_on_error=True
        )
        us = []
        for r in res:
            for ru in r:
                us.append(ru)
        
        is_before_multi_tenant = self.is_before_multi_tenant(us)

        channels: List[int] = []
        received_data: Dict[int, List[Unit]] = {}
        analyzed_data: Dict[int, List[Gait]] = {}

        for u in us:
            if u.channel != 0 and (u.data.data_type.value == intdash.DataType.float.value or u.data.data_type.value == intdash.DataType.string.value):
                if u.channel not in channels:
                    channels.append(u.channel)
                if u.channel not in received_data.keys():
                    received_data[u.channel] = []
                received_data[u.channel].append(u)

        # for channel in list_channel:
        left_us = [u for u in us if u.channel != 0 and (
                u.data.data_type.value == intdash.DataType.float.value or u.data.data_type.value == intdash.DataType.string.value) and
                   u.data.data_id[0] == 'L']
        right_us = [u for u in us if u.channel != 0 and (
                u.data.data_type.value == intdash.DataType.float.value or u.data.data_type.value == intdash.DataType.string.value) and
                    u.data.data_id[0] == 'R']
        pose_us = [u for u in us if u.channel != 0 and (
                u.data.data_type.value == intdash.DataType.float.value or u.data.data_type.value == intdash.DataType.string.value) and
                    u.data.data_id[:3] == 'TF_']
        
        ref_times = self.analyze_reference_time(us)

        start = time.time()
        print(f"Measurement name: {m.name}", flush=True)
        print(f"Start: {start}", flush=True)
        print(f"Length: {len(us)}", flush=True)

        gait_analysis = GaitAnalysis()        

        gait_analysis._left = []
        gait_analysis._left = []
        for channel in [1, 2, 3, 4]:
            analyzed_data[channel] = []

        if is_before_multi_tenant:
            gait_analysis._left = self.analyze_channel_data(left_us, is_before_multi_tenant)
            gait_analysis._right = self.analyze_channel_data(right_us, is_before_multi_tenant)
        else:
            for channel in channels:
                analyzed_data[channel] = self.analyze_channel_data(received_data[channel], is_before_multi_tenant)
        gait_analysis._stored = analyzed_data

        pose_analysis = PoseAnalysis()
        pose_analysis._stored = self.analyze_pose_data(pose_us)
        finish = time.time()
        print(f'Finished: {finish}, {finish - start}', flush=True)

        return AnalyticsValue(
            basetime=m.basetime,
            gait_analysis=gait_analysis,
            pose_analysis=pose_analysis,
            ref_times = ref_times
        )

    def save(self, measurement_uuid: str, units: List[Unit]):
        analysis_result = []
        for unit in units:
            if not isinstance(unit, Unit):
                print(f"It's not a store unit.")
                continue
            analysis_result.append(unit._raw_data)

        print(f"Storing reponse data: Length({len(analysis_result)})", flush=True)
        self._client.units.store(
            measurement_uuid=measurement_uuid,
            units=analysis_result,
        )

    # エッジの検索
    def _search_edge(self, edge_uuid):
        i = 1
        found = None
        while True:
            edges = self._client.edges.list(type="device", page=i)
            for edge in edges:
                if edge.uuid == edge_uuid:
                    found = edge
                if found != None:
                    break

            i = i + 1
            if found != None or i > 100:
                break

        if found == None:
            print("Edge not found:" + edge_uuid)
            return None
        else:
            print("Edge found: " + found.name + " " + found.uuid)
            return found

    # 端末エッジから解析エッジを取得
    def _find_analyzer(self, uuid):
        found = self._search_edge(uuid)
        if found == None:
            return None
        return self._client.edges.list(name=found.name.replace("_device", "_analyzer"))[0]

    def realtime(self, callback: Callable[[AnalyticsValue], List[Unit]], measurement_uuid: str = None,
                 downstream_edge_uuid: str = None, upstream_edge_uuid: str = None):
        # 端末エッジとアナライザーエッジの取得
        if measurement_uuid is not None:
            measurement = self._client.measurements.get(uuid=measurement_uuid)
            if measurement is None:
                print(
                    f"Couldn't find the edge: measurement: {measurement_uuid}")
                return
            downstream_edge_uuid = measurement.edge_uuid
        elif downstream_edge_uuid is not None:
            edge = self._search_edge(downstream_edge_uuid)
            if edge is None:
                print(f"Couldn't find the edge: {downstream_edge_uuid}")
                return
        else:
            print(
                f"Specify [measurement_uuid] or both [measurement_uuid] and [downstream_edge_uuid].")
            return
        if downstream_edge_uuid == upstream_edge_uuid:
            print(
                f"dst_edge_uuid must differ src_edge_uuid. Please specify another dst_edge_uuid.")
            return
        loop = asyncio.get_event_loop()
        try:
            print(f"...Waiting for measurement...")
            loop.run_until_complete(self._realtime_coroutine(callback, downstream_edge_uuid=downstream_edge_uuid,
                                                             upstream_edge_uuid=upstream_edge_uuid))
        finally:
            print(f"...Measurement is closed")
            loop.close()

    async def on_close(self):
        print("connection closed!")

    async def _realtime_coroutine(self, callback: Callable[[AnalyticsValue], None], downstream_edge_uuid: str = None,
                                  upstream_edge_uuid: str = None):
        conn: intdash.ISCPConn = None
        down_spec = self._init_downstream_spec(downstream_edge_uuid)
        up_meas = self._create_upstream_measurement(upstream_edge_uuid)
        up_spec = self._init_upstream_spec(upstream_edge_uuid, up_meas)

        while not self._is_connected:
            conn = await self._client.connect_iscp(on_close=self.on_close)
            await self.exec_downstream(conn=conn, spec=down_spec)

        up_stream = await conn.open_upstream(spec=up_spec, on_ack=self.on_ack)

        while True:
            try:
                await asyncio.ensure_future(self._callback_process(callback))
                if self._up_queue.qsize() == 0:
                    continue
                up_data: List[Unit] = self._up_queue.get_nowait()
                await self._exec_upstream(up_stream, units=up_data, measurement_uuid=up_spec.measurement_uuid)
            except Exception as e:
                print(f"error: {e}")

    def _init_downstream_spec(self, downstream_edge_uuid: str = None) -> intdash.DownstreamSpec:
        spec = None
        if downstream_edge_uuid is not None:
            spec = intdash.DownstreamSpec(
                src_edge_uuid=downstream_edge_uuid,
                filters=get_intdash_data_filter()
            )
        return spec

    def _create_upstream_measurement(self, upstream_edge_uuid: str = None) -> intdash.Measurement:
        meas = None
        if upstream_edge_uuid is not None:
            meas = self._client.measurements.create(
                edge_uuid=upstream_edge_uuid,
                basetime=pandas.Timestamp.utcnow(),
                basetime_type="ntp",
            )
        return meas

    def _init_upstream_spec(self, upstream_edge_uuid: str = None, measurement: intdash.Measurement = None):
        spec = None
        if upstream_edge_uuid is not None and measurement is not None:
            spec = intdash.UpstreamSpec(
                src_edge_uuid=upstream_edge_uuid,
                dst_edge_uuids=None,
                resend=False,
                store=False,
                measurement_uuid=measurement.uuid,
            )
        return spec

    async def exec_downstream(self, conn: intdash.ISCPConn, spec: intdash.DownstreamSpec):
        await conn.open_downstream(spec=spec, on_msg=self.on_msg)

    async def on_msg(self, datapoint) -> None:
        if not self._is_connected:
            self._is_connected = True
        # print(f"down stream callback. datapoint: {datapoint}")
        try:
            self._down_queue.put_nowait(datapoint)
        except queue.Full:
            pass

    def is_before_multi_tenant(self, unit_data: List[Unit]) -> bool:
        for u in unit_data:
            if u.channel == 1 and (u.data.data_id[:12] in ["L_SHOES_JSON", "R_SHOES_JSON"]):
                return True
        return False

    def _callback_process(self, callback: Callable[[AnalyticsValue], None]):
        try:
            if self._down_queue.qsize() == 0:
                return

            datapoint: intdash.DataPoint = self._down_queue.get_nowait()
            if datapoint is None or datapoint.data_type is None:
                return
            if datapoint.data_type.value == intdash.DataType.basetime.value:
                return
            # Skip other data.
            if datapoint.data_type.value not in (intdash.DataType.float.value, intdash.DataType.string.value):
                return
            if datapoint.channel == 0:
                return

            payload_data = None
            if datapoint.data_type.value == intdash.DataType.string.value:
                payload_data = intdash.data.String.from_payload(
                    datapoint.data_payload)
            elif datapoint.data_type.value == intdash.DataType.float.value:
                payload_data = intdash.data.Float.from_payload(
                    datapoint.data_payload)

            channel_id = datapoint.channel
            elapsed_time: pandas.Timedelta = datapoint.elapsed_time
            total_time: int = elapsed_time.total_seconds()
            if total_time != self._current_time:
                self._current_time = total_time
                self._reset_current_value(elapsed_time)

            self._set_current_value(channel_id, payload_data)

            if self._current_value is not None:
                result: List[Unit] = callback(self._current_value)
                self._up_queue.put_nowait(result)

        except queue.Empty:
            # print(f"Empty Queue")
            yield
        except UnicodeDecodeError as e:
            print(e)
            yield

    def _reset_current_value(self, elapsed_time: pandas.Timedelta):
        self._current_value = AnalyticsValue(
            gait_analysis=GaitAnalysis(),
            pose_analysis=PoseAnalysis(),
        )
        self._current_value.gait.left = Gait(elapsed_time)
        self._current_value.gait.right = Gait(elapsed_time)
        for channel_id in self._current_value.gait.realtime:
            self._current_value.gait.realtime[channel_id] = Gait(elapsed_time)
        self._current_value.pose.realtime = Pose(elapsed_time)

    def get_elapsed_time(self) -> pandas.Timedelta:
        return self._current_value.pose.realtime.time

    def _is_old_spec(self, channel_id: int, data_id: str) -> Boolean:
        if channel_id == 1 and len(data_id) >= 12 and data_id[:12] in ["L_SHOES_JSON", "R_SHOES_JSON"]:
            return True
        return False

    def _is_pose_data(self, data_id: str) -> Boolean:
        if len(data_id) >= 8 and data_id[:8] == 'TF_POSE_':
            return True
        return False

    def _set_current_value(self, channel_id: int, payload_data: Union[intdash.data.String, intdash.data.Float]):
        data_id: str = payload_data.data_id
        if self._is_pose_data(data_id):
            if payload_data.data_type.value == intdash.DataType.float.value:
                tmp_key = payload_data.data_id
                tmp_value = payload_data.value
                self._current_value.pose.realtime._set(tmp_key, tmp_value)
            return

        elapsed_time = self.get_elapsed_time()
        tmp_gait = Gait(elapsed_time)

        if payload_data.data_type.value == intdash.DataType.float.value:
            if len(data_id) >= 2 and data_id[:2] in ['L_', 'R_']:
                tmp_key = data_id[2:]
            else:
                tmp_key = data_id
            tmp_value: float = payload_data.value
            tmp_gait._set(tmp_key, tmp_value)
        elif payload_data.data_type.value == intdash.DataType.string.value:
            try:
                sensor_data_json = json.loads(payload_data.value)
                # print(f"callback. string value: {sensor_data_json}")
                for key in self._json_dict:
                    tmp_key = self._json_dict[key]
                    tmp_value: float = sensor_data_json[key]
                    tmp_gait._set(tmp_key, tmp_value)
            except json.JSONDecodeError:
                print("json decode error")
                return

        if self._is_old_spec(channel_id, data_id):
            side: str = "l" if data_id[0] == "L" else "r"
            if side == "l":
                self._current_value.gait.left = tmp_gait
            else:
                self._current_value.gait.right = tmp_gait

        # new spec, access data by channel id
        if channel_id not in self._current_value.gait.realtime:
            self._current_value.gait.realtime[channel_id] = tmp_gait
            return

        self._current_value.gait.realtime[channel_id] = tmp_gait
        return

    async def deadline(self, upstream):
        await asyncio.sleep(10)
        await upstream.close()

    async def on_ack(self, serial, result):
        # print(f"up stream callback")
        # print(f"ACK's serial number is {serial}. Result code is {result}.")
        pass

    async def _exec_upstream(self, upstream: intdash.Upstream, units: List[Unit] = None,
                             measurement_uuid: str = None) -> None:
        try:
            if len(units) > 0:
                for u in units:
                    tmp_dp = u.to_datapoint()
                    await upstream.write(tmp_dp)
                # print(f"wrote data to measurement_id: {measurement_uuid}")
        except Exception as e:
            print(e)
