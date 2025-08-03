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
from .. import GetAllVncsRequestData, GetVncRequestData, CreateVncRequestData, DeleteVncRequestData, \
    GetAllVncsResponseData, GetVncResponseData, CreateVncResponseData, DeleteVncResponseData


class VncRouter(Router):
    facade_service = 'VncFacadeService'
    prefix = '/vncs'

    @route(
        path='/get-all',
        request_data=GetAllVncsRequestData,
        response_data=GetAllVncsResponseData,
        response_field='vncs'
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetVncRequestData,
        response_data=GetVncResponseData,
        response_field='vnc'
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateVncRequestData,
        response_data=CreateVncResponseData,
        response_field='vnc'
    )
    async def create(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteVncRequestData,
        response_data=DeleteVncResponseData,
    )
    async def delete(self):
        pass
