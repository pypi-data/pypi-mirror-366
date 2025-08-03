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

from .. import GetAllSelectorsRequestData, GetAllSelectorsResponseData, GetSelectorRequestData, GetSelectorResponseData, \
    CreateSelectorRequestData, CreateSelectorResponseData, UpdateSelectorRequestData, UpdateSelectorResponseData, \
    DeleteSelectorRequestData, DeleteSelectorResponseData, GetSelectorsBySiteRequestData, \
    GetSelectorsBySiteResponseData
from .base import Router


class SelectorRouter(Router):
    facade_service = 'SelectorFacadeService'
    prefix = '/selectors'

    @route(
        path='/get-all',
        request_data=GetAllSelectorsRequestData,
        response_data=GetAllSelectorsResponseData,
        response_field='selectors',
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetSelectorRequestData,
        response_data=GetSelectorResponseData,
        response_field='selector',
    )
    async def get(self):
        pass

    @route(
        path='/get_by_site',
        request_data=GetSelectorsBySiteRequestData,
        response_data=GetSelectorsBySiteResponseData,
        response_field='selectors',
    )
    async def get_by_site(self):
        pass

    @route(
        path='/create',
        request_data=CreateSelectorRequestData,
        response_data=CreateSelectorResponseData,
        response_field='selector',
    )
    async def create(self):
        pass

    @route(
        path='/update',
        request_data=UpdateSelectorRequestData,
        response_data=UpdateSelectorResponseData,
        response_field='selector',
    )
    async def update(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteSelectorRequestData,
        response_data=DeleteSelectorResponseData,
    )
    async def delete(self):
        pass
