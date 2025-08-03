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


from typing import Dict, Any, List, Optional

from nexium_api import BaseResponseData

from .proxy import ProxyOut
from .selector import SelectorOut
from .banner import BannerOut
from ..models.site import Site


class SiteOut(BaseResponseData):
    id: int
    name: str
    url: str
    proxy: Optional[ProxyOut]
    cookies: Dict[str, Any]
    selectors: List[SelectorOut]
    banners: List[BannerOut]


class GetAllSitesResponseData(BaseResponseData):
    sites: list[SiteOut]


class GetSiteResponseData(BaseResponseData):
    site: SiteOut


class CreateSiteResponseData(BaseResponseData):
    site: Site


class UpdateSiteResponseData(BaseResponseData):
    site: Site


class DeleteSiteResponseData(BaseResponseData):
    pass
