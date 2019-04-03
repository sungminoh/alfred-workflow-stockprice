import json
import re
import urllib2
import unicodedata
from contextlib import contextmanager


def platten_nested_list(l):
    ret = []
    for v in l:
        if isinstance(v, list):
            if len(v) == 1:
                if isinstance(v[0], list):
                    ret.append(platten_nested_list(v[0]))
                else:
                    ret.append(v[0])
            elif len(v) > 1:
                ret.append(platten_nested_list(v))
        else:
            ret.append(v)
    return ret


def make_depth_two(l):
    ret = []
    for v in l:
        if isinstance(v, list):
            if len(v) > 0:
                if not isinstance(v[0], list):
                    ret.append(v)
                else:
                    ret.extend(make_depth_two(v))
        else:
            ret.append([v])
    return ret


def build_dic(l):
    appeared = set()
    ret = []
    for v in l:
        if v[0] in appeared:
            continue
        appeared.add(v[0])
        dic = dict(label=v[0],
                   name=v[1],
                   market=v[2],
                   code=v[4])
        ret.append(dic)
    return ret


def data_to_dic(data):
    return build_dic(make_depth_two(platten_nested_list(data)))


def get_json(url):
    headers = {
        'authority': 'ac.finance.naver.com',
        'cache-control': 'max-age=0',
        'save-data': 'on',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
        'cookie': 'NNB=CGZMQERKMOMVY; npic=kwUMpAjWeZW05ke3zXghQaDMHe2qBml8aNjihV38fBbO7Mu+2Z2oDQPMO13W6kfpCA==; nx_ssl=2; naver_stock_codeList=041190%7C',
    }
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    content = response.read()
    try:
        data = json.loads(content.decode('utf-8'))
    except Exception:
        data = json.loads(content.decode('euc-kr'))
    return data


def parse_url(url):
    # p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*)(?P<uri>.*)'
    p = '((?P<schema>https?)://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*)(?P<uri>[^\?]*)\??(?P<params>.*)'
    m = re.search(p, str(url))
    schema, host, port, uri, params = m.group('schema'), m.group('host'), m.group('port'), m.group('uri'), m.group('params')
    return schema, host, port, uri, params


def format_num(num, decimal=0):
    return ('{:,.%sf}' % decimal).format(float(num))


def encode(query):
    return urllib2.quote(unicodedata.normalize('NFC', query).encode('euc-kr'))


def get_query(argv):
    try:
        query = u'%s' % ' '.join(argv)
        return encode(query)
    except Exception:
        return ''


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

