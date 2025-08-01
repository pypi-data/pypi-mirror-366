# # Copyright 2020 Aptpod, Inc.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
import intdash
import pandas


class Unit(object):
    id: str
    side: str
    time: pandas.Timedelta
    value: float
    channel: int

    def __init__(self, time: pandas.Timedelta, id: str, value: float, channel: int, side: str = None) -> None:
        if side is None:
            side = ""
        else:
            side = side.upper() + "_"
        self.side: str = self
        self.id: str = id
        self.value: float = value
        self.channel = channel
        self.time: pandas.Timedelta = time
        self._raw_data = intdash.Unit(
            elapsed_time=time,
            channel=channel,
            data=intdash.data.Float(data_id=side + id, value=value),
        )

    def copy(self, id: str, value: float, channel: int, side: str = None) -> "Unit":
        if side is None:
            side = ""
        else:
            side = side + "_"
        return Unit(
            time=self.time,
            id=id,
            value=value,
            side=side,
        )

    def to_datapoint(self) -> intdash.DataPoint:
        datapoint = intdash.DataPoint(
            elapsed_time=self.time,
            channel=self.channel,
            data_type=intdash.DataType.float,
            data_payload=intdash.data.Float(
                data_id=self.id, value=self.value).to_payload()
        )
        return datapoint
