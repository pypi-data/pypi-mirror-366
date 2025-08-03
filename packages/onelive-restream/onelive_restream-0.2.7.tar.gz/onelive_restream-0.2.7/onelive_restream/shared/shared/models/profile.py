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
from sqlmodel import Field, Relationship

from .base import BaseDbModel
from .proxy import Proxy
from .site import Site


class Profile(BaseDbModel, table=True):
    __tablename__ = 'profiles'

    site_id: int = Field(foreign_key='sites.id')
    site: Site = Relationship(sa_relationship_kwargs={'lazy': 'joined'})

    proxy_id: int = Field(foreign_key='proxies.id')
    proxy: Proxy = Relationship(sa_relationship_kwargs={'lazy': 'joined'})

    cookies: list = Field(default={}, sa_type=JSON)
