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
from .. import GetAllStreamsBannersRequestData, GetAllStreamsBannersResponseData, GetStreamBannerRequestData, \
    GetStreamBannerResponseData, CreateStreamBannerRequestData, CreateStreamBannerResponseData, \
    UpdateStreamBannerRequestData, UpdateStreamBannerResponseData, DeleteStreamBannerRequestData, \
    DeleteStreamBannerResponseData


class StreamBannerRouter(Router):
    facade_service = 'StreamBannerFacadeService'
    prefix = '/streams_banners'

    @route(
        path='/get-all',
        request_data=GetAllStreamsBannersRequestData,
        response_data=GetAllStreamsBannersResponseData,
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetStreamBannerRequestData,
        response_data=GetStreamBannerResponseData,
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateStreamBannerRequestData,
        response_data=CreateStreamBannerResponseData,
    )
    async def create(self):
        pass

    @route(
        path='/update',
        request_data=UpdateStreamBannerRequestData,
        response_data=UpdateStreamBannerResponseData,
    )
    async def update(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteStreamBannerRequestData,
        response_data=DeleteStreamBannerResponseData,
    )
    async def delete(self):
        pass
