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


from sqlalchemy import JSON
from sqlmodel import SQLModel, Field

from .base import BaseDbModel
from ..enums import ProxyType


class Proxy(BaseDbModel, table=True):
    __tablename__ = 'proxies'

    type: ProxyType
    data: dict = Field(default={}, sa_type=JSON)

    def get(self):
        if self.type == ProxyType.HTTP:
            return HTTPProxy(**self.data)
        if self.type == ProxyType.SOCKS5:
            return SOCKS5Proxy(**self.data)


class HTTPProxy(SQLModel):
    username: str
    password: str
    host: str
    port: int

    def __str__(self):
        # noinspection HttpUrlsUsage
        return f'http://{self.username}:{self.password}@{self.host}:{self.port}'

    def __json__(self):
        return self.model_dump()


class SOCKS5Proxy(SQLModel):
    username: str
    password: str
    host: str
    port: int

    def __str__(self):
        # noinspection HttpUrlsUsage
        return f'socks5://{self.username}:{self.password}@{self.host}:{self.port}'

    def __json__(self):
        return self.model_dump()
