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

from .. import CreateSiteRequestData, CreateSiteResponseData, GetAllSitesRequestData, GetAllSitesResponseData, \
    DeleteSiteRequestData, DeleteSiteResponseData, GetSiteRequestData, GetSiteResponseData
from .base import Router


class SiteRouter(Router):
    facade_service = 'SiteFacadeService'
    prefix = '/sites'

    @route(
        path='/get-all',
        request_data=GetAllSitesRequestData,
        response_data=GetAllSitesResponseData,
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetSiteRequestData,
        response_data=GetSiteResponseData,
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateSiteRequestData,
        response_data=CreateSiteResponseData,
    )
    async def create(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteSiteRequestData,
        response_data=DeleteSiteResponseData,
    )
    async def delete(self):
        pass
