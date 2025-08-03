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


from nexium_api import BaseRequestAuth


class RequestAuth(BaseRequestAuth):
    token: str

    async def check(self):
        pass
        # server_id, token_value = self.token.split(':')
        #
        # server = await server_repo.get_by_id(id_=server_id)
        #
        # if not await check_hash(
        #         hash_=b64decode(server.token_hash),
        #         salt=b64decode(server.token_salt),
        #         value=token_value,
        # ):
        #     raise TokenValidationError()
