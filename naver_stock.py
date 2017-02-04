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

from helper import data_to_dic, get_json, format_num, get_query, encode, ignored
import cPickle as pickle
from collections import defaultdict
from os.path import exists
from os import remove
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

LIST_URL = u'http://ac.finance.naver.com:11002/ac?q=%s&q_enc=euc-kr&st=111&frm=stock&r_format=json&r_enc=euc-kr&r_unicode=0&t_koreng=1&r_lt=111'
SEARCH_URL = u'http://finance.naver.com/search/search.nhn?query=%s'
POLLING_URL = u'http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:%s'
FAVORITE_FILE = 'favorite.pickle'
ITEM_TEXT = '<item arg="{url}"><title>{title}</title><subtitle>{subtitle}</subtitle></item>'


def build_alfred_items(items):
    alfred_items = []
    for item in items:
        values = defaultdict(str)
        # URL, Polling URL, Detail object
        with ignored(Exception):
            values['url'] = SEARCH_URL % encode(item['label'] + ' ' + item['name'])
        with ignored(Exception):
            values['polling_url'] = POLLING_URL % item['code']
        with ignored(Exception):
            values['detail'] = get_json(values['polling_url'])['result']['areas'][0]['datas'][0]
        detail = values['detail']
        try:
            # process detail data
            with ignored(Exception):
                values['nm'] = detail['nm']
            with ignored(Exception):
                values['nv'] = '￦' + format_num(detail['nv'])
            with ignored(Exception):
                values['sign'] = '+' if detail['nv'] >= detail['pcv'] else '-'
            with ignored(Exception):
                values['cr'] = format_num(detail['cr'], 2)
            with ignored(Exception):
                values['cv'] = format_num(detail['cv'])
            with ignored(Exception):
                values['space'] = 45 - len(detail['nm'].encode('euc-kr'))
            with ignored(Exception):
                values['aq'] = format_num(detail['aq'])
            with ignored(Exception):
                values['hv'] = format_num(detail['hv'])
            with ignored(Exception):
                values['lv'] = format_num(detail['lv'])
            with ignored(Exception):
                values['eps'] = format_num(float(detail['nv'])/float(detail['eps']), 2) + '배'
            with ignored(Exception):
                values['bps'] = format_num(float(detail['nv'])/float(detail['bps']), 2) + '배'
            # unpack dictionary
            url, polling_url, nm, nv, sign, cr, cv, space, aq, hv, lv, eps, bps = \
                map(values.get, ('url', 'polling_url', 'nm', 'nv', 'sign', 'cr', 'cv', 'space', 'aq', 'hv', 'lv', 'eps', 'bps'))
            # 종목 현재가 (+ 비율% 변동)
            title = (u'{nm}{nv:>%s} ( {sign} {cr} %%, {cv})' % space).format(nm=nm, nv=nv, sign=sign, cr=cr, cv=cv)
            subtitle = u'{market} 거래량: {aq}  고가: {hv}  저가: {lv}  PER: {eps}  PBR: {bps}'.format(market=item['market'], aq=aq, hv=hv, lv=lv, eps=eps, bps=bps)
            item_text = ITEM_TEXT.format(url=url, title=title, subtitle=subtitle)
        except:
            item_text = ITEM_TEXT.format(url=url, title=item['name'], subtitle=item['market'])
        alfred_items.append(item_text.encode('utf-8'))
    return alfred_items


def print_alfred_items(alfred_items):
    print '<items>'
    for item in alfred_items:
        print item
    print '</items>'


def get_items(query):
    url = LIST_URL % query
    data = get_json(url)[u'items']
    items = data_to_dic(data)
    return items


def search():
    if sys.argv[2:]:
        print_alfred_items(build_alfred_items(get_items(get_query(sys.argv[2:]))))
    else:
        items = []
        for label in load_favorites():
            items.extend(get_items(label))
        print_alfred_items(build_alfred_items(items))


def search_for_delete():
    items = []
    for label in load_favorites():
        items.extend(get_items(label))
    alfred_items = build_alfred_items(items)
    alfred_items.insert(0, u'<item><title>삭제하고 싶은 종목을 선택하세요.</title></item>')
    print_alfred_items(alfred_items)


def load_favorites():
    if exists(FAVORITE_FILE):
        with open(FAVORITE_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        return []


def set_favorite():
    url = sys.argv[2]
    label = url[re.search('query=', url).end():re.search('%20', url).start()]
    if exists(FAVORITE_FILE):
        with open(FAVORITE_FILE, 'rb') as f:
            favorites = pickle.load(f)
            favorites.append(label)
    else:
        favorites = [label]
    with open(FAVORITE_FILE, 'wb') as f:
        pickle.dump(favorites, f)


def del_favorite():
    url = sys.argv[2]
    label = url[re.search('query=', url).end():re.search('%20', url).start()]
    if exists(FAVORITE_FILE):
        with open(FAVORITE_FILE, 'rb') as f:
            favorites = pickle.load(f)
        try:
            favorites.remove(label)
        except:
            pass
    else:
        favorites = []
    with open(FAVORITE_FILE, 'wb') as f:
        pickle.dump(favorites, f)


def reset_favorite():
    if exists(FAVORITE_FILE):
        remove(FAVORITE_FILE)


router = dict(set_favorite=set_favorite,
              del_favorite=del_favorite,
              reset_favorite=reset_favorite,
              search=search,
              search_for_delete=search_for_delete)


def main():
    command = sys.argv[1]
    router[command]()


if __name__ == '__main__':
    main()
