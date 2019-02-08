import json
import re
import urllib2
from httplib import HTTPSConnection
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
        if v[0] in appeared: continue
        appeared.add(v[0])
        # url = 'finance.naver.com%s' % v[3]
        # if v[3].startswith('/market') or v[3].startswith('/fund'):
            # url = 'info.' + url
        dic = dict(label=v[0],
                   name=v[1],
                   market=v[2],
                   # url=url,
                   code=v[4])
        ret.append(dic)
    return ret


def data_to_dic(data):
    return build_dic(make_depth_two(platten_nested_list(data)))


def get_json(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "npic=s3bX+Og5mdOluWR1wbMyv6Skb/K5KL+6lFal+ZyzyjG1ye0a4tSqbvfMmTWMx+2mCA==; NNB=2Y3RIKP7P5MVU; ASID=0cc907c9000001613b11f9140001fa12; __gads=ID=a31df8aefa0f52f9:T=1517347381:S=ALNI_MYX4E_j_F9q0HbHLuMlOICW4Ijc1w; _ga=GA1.2.1988629889.1545098371; nx_ssl=2; BMR=s=1548222526858&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.nhn%3FblogId%3Dkjh3pp%26logNo%3D220759726221%26proxyReferer%3Dhttps%253A%252F%252Fwww.google.com%252F&r2=https%3A%2F%2Fwww.google.com%2F; NID_AUT=VQLANkaTHY0tB1DaoaQkO61F6LuA/MDDohN2AvhZleoB1mHvjvC4a3qgufgGnqFu; page_uid=UZlhQlpl6Ilss5iehvZssssssvG-307940; NID_SES=AAABelVlfnEi6GJGdTIi1CPsZ4QnXEgtwBpChMNHXdzIux1GS5WqkzKO681CncL4J1vL+7ghwRT43kIn6ZPYykfaVU3EKLlIxNLUkZ5J2vXfQdwM00i+yoG7EXeJnEwL5sWhn2qkcMNifgmU/y74nkWE4p/Lem0q3FCHskwbwmakfVw0T79UWVDdh0vSMjUQZ1gRySyejiFk020aRKxBXNS/M15ZGL5dz2bH0NCn1Nr/LkXuI67TyaI8yKMERe5oh+1upI6wy6YgpL8QTknysBS6RRTwsfLM6d3zZe/i74rkSGOplDfxQ6z+EtMHn8s6nL8iPqLjAZ+erpqfkCFEnN4DNZRNSm1G90L8HSLNPKNByZ8VGLa1HhKgfCCKWO3H2HYog5PUY1hS2kj22N8InKg7n8cumzmAf/F60371UJ2eC67g+apiFO1mHpTUkksuTDfzC6PuY62ILLz0lecwftqpY9H0SjFpfOxDf4QJigCX8bvlb+SxkcKXoECH2qtRNEOVNA==; naver_stock_codeList=041140%7C",
        "Host": "ac.finance.naver.com:11002",
        "Pragma": "no-cache",
        "Save-Data": "on",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "X-Compress": "null"
    }
    if(url.startswith('https')):
        host, port, uri = parse_url(url)
        conn = HTTPSConnection(host, port)
        conn.request('get', uri)
        response = conn.getresponse()
    else:
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
    content = response.read()
    try:
        data = json.loads(content.decode('utf-8'))
    except:
        data = json.loads(content.decode('euc-kr'))
    return data


def parse_url(url):
    p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*)(?P<uri>.*)'
    m = re.search(p, str(url))
    host, port, uri = m.group('host'), m.group('port'), m.group('uri')
    return host, port, uri


def format_num(num, decimal=0):
    return ('{:,.%sf}' % decimal).format(float(num))


def encode(query):
    return urllib2.quote(unicodedata.normalize('NFC', query).encode('euc-kr'))


def get_query(argv):
    try:
        query = u'%s' % ' '.join(argv)
        return encode(query)
    except:
        return ''

@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

