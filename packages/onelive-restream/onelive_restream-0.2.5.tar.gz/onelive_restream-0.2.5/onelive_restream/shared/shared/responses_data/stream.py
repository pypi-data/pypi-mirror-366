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


from nexium_api import BaseResponseData

from ..models.stream import Stream


class GetAllStreamsResponseData(BaseResponseData):
    streams: list[Stream]


class GetStreamResponseData(BaseResponseData):
    stream: Stream


class CreateStreamResponseData(BaseResponseData):
    stream: Stream


class UpdateStreamResponseData(BaseResponseData):
    stream: Stream


class UpdateStateStreamResponseData(BaseResponseData):
    stream: Stream


class DeleteStreamResponseData(BaseResponseData):
    pass
