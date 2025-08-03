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


from nexium_api import route

from .base import Router
from .. import GetAllStreamsRequestData, GetAllStreamsResponseData, CreateStreamRequestData, CreateStreamResponseData, \
    DeleteStreamRequestData, DeleteStreamResponseData, GetStreamRequestData, GetStreamResponseData, \
    UpdateStreamRequestData, UpdateStreamResponseData, UpdateStateStreamRequestData, UpdateStateStreamResponseData


class StreamRouter(Router):
    facade_service = 'StreamFacadeService'
    prefix = '/streams'

    @route(
        path='/get-all',
        request_data=GetAllStreamsRequestData,
        response_data=GetAllStreamsResponseData,
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetStreamRequestData,
        response_data=GetStreamResponseData,
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateStreamRequestData,
        response_data=CreateStreamResponseData,
    )
    async def create(self):
        pass

    @route(
        path='/update',
        request_data=UpdateStreamRequestData,
        response_data=UpdateStreamResponseData,
    )
    async def update(self):
        pass

    @route(
        path='/update_state',
        request_data=UpdateStateStreamRequestData,
        response_data=UpdateStateStreamResponseData,
    )
    async def update_state(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteStreamRequestData,
        response_data=DeleteStreamResponseData,
    )
    async def delete(self):
        pass
