# -*- coding: utf-8 -*-

"""
    nv: 현재가
    cd: 종목코드
    eps: nv/eps PER(배)
    bps: nv/bps PBR(배)
    ov: 시가
    sv: 전일?
    pcv: 전일
    cv: 전일 대비
    cr: 전일 대비 증감 %
    aq: 거래량
    aa: 거래대금
    ms: 장상태 ('OPEN', 'CLOSE')
    hv: 고가
    lv: 저가
    ul: 상한가
    ll: 하한가
    nm: 이름
    keps:
    dv:
    cnsEps:
    nav:
    rf:
    mt:
    tyn:
"""

import urllib2
import json
import unicodedata
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

LIST_URL = u'http://ac.finance.naver.com:11002/ac?q=%s&q_enc=euc-kr&st=111&frm=stock&r_format=json&r_enc=euc-kr&r_unicode=0&t_koreng=1&r_lt=111'
POLLING_URL = u'http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:%s&q_enc=utf-8'

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
    ret = []
    for v in l:
        url = 'finance.naver.com%s' % v[3]
        if v[3].startswith('/market') or v[3].startswith('/fund'):
            url = 'info.' + url
        dic = dict(label=v[0],
                   name=v[1],
                   market=v[2],
                   url=url,
                   code=v[4])
        ret.append(dic)
    return ret


def get_json(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    try:
        data = json.loads(content.decode('utf-8'))
    except:
        data = json.loads(content.decode('euc-kr'))
    return data


def format_num(num, decimal=None):
    if not decimal:
        decimal = 0
    return ('{:,.%sf}' % decimal).format(float(num))


def get_query():
    try:
        query = u'%s' % ' '.join(sys.argv[1:])
        query = unicodedata.normalize('NFC', query)
        return urllib2.quote(query.encode('utf-8'))
    except:
        return ''


def print_alfred_format(items):
    print '<items>'
    for item in items:
        try:
            polling_url = POLLING_URL % item['code']
            detail = get_json(polling_url)['result']['areas'][0]['datas'][0]
            # 종목 현재가 (+ 비율% 변동)
            title = u'{nm}    {nv} ( {sign} {cr}%, {cv})'.format(
                nm=detail['nm'],
                nv='￦' + format_num(detail['nv']),
                sign='+' if detail['nv'] >= detail['pcv'] else '-',
                cr=format_num(detail['cr'], 2),
                cv=format_num(detail['cv']))
            subtitle = u'거래량: {aq}  고가: {hv}  저가: {lv}  PER: {eps}  PBR: {bps}'.format(
                aq=format_num(detail['aq']),
                hv=format_num(detail['hv']),
                lv=format_num(detail['lv']),
                eps=format_num(float(detail['nv'])/float(detail['eps']), 2) + '배',
                bps=format_num(float(detail['nv'])/float(detail['bps']), 2) + '배')
            item_text = '<item arg="%s"><title>%s</title><subtitle>%s</subtitle></item>' % (item['url'], title, subtitle)
        except Exception as e:
            print e
            item_text = '<item arg="%s"><title>%s</title><subtitle>%s</subtitle></item>' % (item['url'], item['name'], item['market'])
        print item_text.encode('utf-8')
    print '</items>'


def main():
    query = get_query()
    url = LIST_URL % query
    data = get_json(url)[u'items']
    items = build_dic(make_depth_two(platten_nested_list(data)))
    print_alfred_format(items)


if __name__ == '__main__':
    main()
