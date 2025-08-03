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


from .banner import BannerRouter
from .base import Router
from .server import ServerRouter
from .proxy import ProxyRouter
from .site import SiteRouter
from .stream import StreamRouter
from .profile import ProfileRouter
from .selector import SelectorRouter
from .stream_banner import StreamBannerRouter
from .stream_server import StreamServerRouter
from ..models import RootAuth


class MainRouter(Router):
    auth = RootAuth

    server: ServerRouter
    proxy: ProxyRouter
    site: SiteRouter
    stream: StreamRouter
    profile: ProfileRouter
    banner: BannerRouter
    selector: SelectorRouter
    stream_banner: StreamBannerRouter
    stream_server: StreamServerRouter
