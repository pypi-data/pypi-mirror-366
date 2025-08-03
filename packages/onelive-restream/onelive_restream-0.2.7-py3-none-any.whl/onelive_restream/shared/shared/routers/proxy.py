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

from .. import GetAllProxiesRequestData, GetAllProxiesResponseData, CreateProxyRequestData, CreateProxyResponseData, \
    DeleteProxyResponseData, DeleteProxyRequestData, GetProxyRequestData, GetProxyResponseData
from .base import Router


class ProxyRouter(Router):
    facade_service = 'ProxyFacadeService'
    prefix = '/proxies'

    @route(
        path='/get-all',
        request_data=GetAllProxiesRequestData,
        response_data=GetAllProxiesResponseData,
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetProxyRequestData,
        response_data=GetProxyResponseData,
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateProxyRequestData,
        response_data=CreateProxyResponseData,
    )
    async def create(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteProxyRequestData,
        response_data=DeleteProxyResponseData,
    )
    async def delete(self):
        pass
