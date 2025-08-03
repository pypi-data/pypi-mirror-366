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
from .. import GetAllBannersRequestData, GetAllBannersResponseData, GetBannerRequestData, GetBannerResponseData, \
    CreateBannerRequestData, CreateBannerResponseData, UpdateBannerRequestData, UpdateBannerResponseData, \
    DeleteBannerRequestData, DeleteBannerResponseData, GetBannersBySiteRequestData, GetBannersBySiteResponseData


class BannerRouter(Router):
    facade_service = 'BannerFacadeService'
    prefix = '/banners'

    @route(
        path='/get-all',
        request_data=GetAllBannersRequestData,
        response_data=GetAllBannersResponseData,
        response_field='banners',
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetBannerRequestData,
        response_data=GetBannerResponseData,
        response_field='banner',
    )
    async def get(self):
        pass

    @route(
        path='/get_by_site',
        request_data=GetBannersBySiteRequestData,
        response_data=GetBannersBySiteResponseData,
        response_field='banners',
    )
    async def get_by_site(self):
        pass

    @route(
        path='/create',
        request_data=CreateBannerRequestData,
        response_data=CreateBannerResponseData,
        response_field='banner',
    )
    async def create(self):
        pass

    @route(
        path='/update',
        request_data=UpdateBannerRequestData,
        response_data=UpdateBannerResponseData,
        response_field='banner',
    )
    async def update(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteBannerRequestData,
        response_data=DeleteBannerResponseData,
    )
    async def delete(self):
        pass
