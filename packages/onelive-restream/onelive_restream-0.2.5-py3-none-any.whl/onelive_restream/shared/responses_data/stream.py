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

from nexium_api import BaseResponseData

from .site import SiteOut
from .server import ServerOut
from .. import StreamState
from ..models.stream import Stream


class StreamOut(BaseResponseData):
    id: int
    url: str
    state: StreamState
    site: SiteOut
    server: ServerOut
    start_at: datetime
    end_at: datetime


class GetStreamResponseData(BaseResponseData):
    stream: StreamOut


class GetAllStreamsResponseData(BaseResponseData):
    streams: list[StreamOut]


class CreateStreamResponseData(BaseResponseData):
    stream: Stream


class UpdateStreamResponseData(BaseResponseData):
    stream: Stream


class UpdateStateStreamResponseData(BaseResponseData):
    stream: Stream


class DeleteStreamResponseData(BaseResponseData):
    pass
