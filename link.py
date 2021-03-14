import requests
from urllib.parse import urlparse
from lxml import etree


def parse_link_data(_url):
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                      AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    _purl = urlparse(_url)
    link_data = dict()
    if not _purl:
        return _purl
    try:
        resp = requests.get(_url, headers=_headers)
        _sel = etree.HTML(resp.text)
    except:
        return {}

    # 读取favicon
    def fav(_sel, _purl):
        _xp = "//link[contains(@rel, '%s')]/@href"
        res = _sel.xpath(_xp % 'icon')
        res = res if res else _sel.xpath(_xp % 'ICON')
        if not res:
            return '{}://{}/{}'.format(_purl.scheme, _purl.netloc, 'favicon.ico')
        _ut = urlparse(res[0])
        if _ut.scheme == '' and _ut.netloc:
            return '{}://{}/{}'.format(_purl.scheme, _purl.netloc, res[0])
        return res[0]

    # 获得结果
    link_data['describe'] = ''.join(_sel.xpath(
        '//meta[@name="description"]/@content'))[:200]
    link_data['title'] = ''.join(_sel.xpath(
        '//title/text()'))[:50]  # [:50] 限制长度
    link_data['favicon'] = fav(_sel, _purl)
    link_data['link'] = _url
    return link_data
