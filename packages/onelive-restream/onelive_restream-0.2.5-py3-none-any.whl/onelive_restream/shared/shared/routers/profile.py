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

from .. import GetAllProfilesRequestData, GetAllProfilesResponseData, GetProfileRequestData, GetProfileResponseData, \
    UpdateProfileRequestData, UpdateProfileResponseData, CreateProfileRequestData, CreateProfileResponseData, \
    DeleteProfileRequestData, DeleteProfileResponseData
from .base import Router


class ProfileRouter(Router):
    facade_service = 'ProfileFacadeService'
    prefix = '/profiles'

    @route(
        path='/get-all',
        request_data=GetAllProfilesRequestData,
        response_data=GetAllProfilesResponseData,
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetProfileRequestData,
        response_data=GetProfileResponseData,
    )
    async def get(self):
        pass

    @route(
        path='/update',
        request_data=UpdateProfileRequestData,
        response_data=UpdateProfileResponseData,
    )
    async def update(self):
        pass

    @route(
        path='/create',
        request_data=CreateProfileRequestData,
        response_data=CreateProfileResponseData,
    )
    async def create(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteProfileRequestData,
        response_data=DeleteProfileResponseData,
    )
    async def delete(self):
        pass
