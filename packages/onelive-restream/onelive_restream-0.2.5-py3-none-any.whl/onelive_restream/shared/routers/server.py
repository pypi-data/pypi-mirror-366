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

from .. import GetAllServersRequestData, GetAllServersResponseData, CreateServerRequestData, CreateServerResponseData, \
    DeleteServerRequestData, DeleteServerResponseData
from .base import Router


class ServerRouter(Router):
    facade_service = 'ServerFacadeService'
    prefix = '/servers'

    @route(
        path='/get-all',
        request_data=GetAllServersRequestData,
        response_data=GetAllServersResponseData,
        response_field='servers'
    )
    async def get_all(self):
        pass

    @route(
        path='/create',
        request_data=CreateServerRequestData,
        response_data=CreateServerResponseData,
        response_field='server'
    )
    async def create(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteServerRequestData,
        response_data=DeleteServerResponseData,
    )
    async def delete(self):
        pass
