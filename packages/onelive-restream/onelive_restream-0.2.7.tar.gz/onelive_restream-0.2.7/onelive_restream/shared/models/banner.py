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


from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlmodel import Field

from .base import BaseDbModel


class Banner(BaseDbModel, table=True):
    __tablename__ = 'banners'

    name: str
    site_id: int = Field(foreign_key='sites.id')
    photo: str = Field(sa_column=Column(LONGTEXT, nullable=False))
    x: str
    y: str
