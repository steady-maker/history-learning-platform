import os
from django.utils.functional import LazyObject
from utils.xdbSearcher import XdbSearcher

class IPRegion(LazyObject):
    def _setup(self):
        # 绝对路径
        db_path = os.path.join(os.path.dirname(__file__), "ip2region_v4.xdb")
        self._wrapped = XdbSearcher(dbfile=db_path)

ip_region_searcher = IPRegion()

def get_ip_region(ip: str) -> str:
    """
    将 IP 转换为 '省份 市' 格式，例如 '河北省 石家庄市'
    """
    try:
        region_str = ip_region_searcher.searchByIPStr(ip)
        return f"{region_str}".replace("|", " ").strip() or "未知地区"
    except Exception:
        return "未知地区"
