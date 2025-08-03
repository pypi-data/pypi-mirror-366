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


from typing import Optional, Any, Dict, List

from sqlalchemy import JSON, and_
from sqlalchemy.orm import foreign, relationship, remote
from sqlmodel import Field, Relationship

from .base import BaseDbModel
from .proxy import Proxy
from .selector import Selector
from .banner import Banner


class Site(BaseDbModel, table=True):
    __tablename__ = 'sites'

    name: str
    url: str

    proxy_id: Optional[int] = Field(default=None, foreign_key='proxies.id')
    proxy: Optional[Proxy] = Relationship(
        sa_relationship_kwargs={
            'lazy': 'joined',
            'primaryjoin': lambda: and_(
                foreign(Site.proxy_id) == remote(Proxy.id),
                Proxy.is_deleted == False,
            )
        }
    )

    cookies: Dict[str, Any] = Field(default=dict, sa_type=JSON)

    selectors: List[Selector] = Relationship(
        sa_relationship_kwargs={
            'lazy': 'selectin',
            'primaryjoin': lambda: and_(
                foreign(Selector.site_id) == Site.__table__.c.id,
                Selector.is_deleted == False,
            )
        }
    )

    banners: List[Banner] = Relationship(
        sa_relationship_kwargs={
            'lazy': 'selectin',
            'primaryjoin': lambda: and_(
                foreign(Banner.site_id) == Site.__table__.c.id,
                Banner.is_deleted == False,
            )
        }
    )