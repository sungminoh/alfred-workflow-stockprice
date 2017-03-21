import json
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
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    try:
        data = json.loads(content.decode('utf-8'))
    except:
        data = json.loads(content.decode('euc-kr'))
    return data


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

