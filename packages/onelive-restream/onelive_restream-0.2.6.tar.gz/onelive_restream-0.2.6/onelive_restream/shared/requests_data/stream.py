#
# (c) 2025, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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
# limitations under the License.
#


from datetime import datetime

from nexium_api import BaseRequestData

from ..enums import StreamState


class GetAllStreamsRequestData(BaseRequestData):
    pass


class GetStreamRequestData(BaseRequestData):
    id_: int


class CreateStreamRequestData(BaseRequestData):
    url: str
    state: StreamState
    server_id: int
    site_id: int
    start_at: datetime
    end_at: datetime


class UpdateStreamRequestData(BaseRequestData):
    id_: int
    url: str
    state: StreamState
    server_id: int
    site_id: int
    start_at: datetime
    end_at: datetime


class UpdateStateStreamRequestData(BaseRequestData):
    id_: int
    state: StreamState


class DeleteStreamRequestData(BaseRequestData):
    id_: int
