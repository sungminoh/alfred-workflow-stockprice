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
from multiprocessing import Process, Queue
from itertools import chain
import cPickle as pickle
from collections import defaultdict
from os.path import exists
from os import remove
import re
import sys
from workflow import Workflow
reload(sys)
sys.setdefaultencoding("utf-8")


class Stock(Workflow):
    LIST_URL = u'http://ac.finance.naver.com:11002/ac?q=%s&q_enc=euc-kr&st=111&frm=stock&r_format=json&r_enc=euc-kr&r_unicode=0&t_koreng=1&r_lt=111'
    SEARCH_URL = u'https://finance.naver.com/item/main.nhn?code=%s'
    POLLING_URL = u'http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:%s'
    FAVORITE_FILE = './favorite.pickle'

    def __init__(self, *args):
        super(Stock, self).__init__()
        self.arguments = args

    def add(self, title, subtitle='', url=None, icon=None):
        self.add_item(title, subtitle, valid=True, modifier_subtitles={'ctrl': '즐겨찾기에 추가합니다.', 'alt': '즐겨찾기에서 삭제합니다.'}, arg=url, icon=icon)

    def build_alfred_items(self, items):
        for item in items:
            values = defaultdict(str)
            # URL, Polling URL, Detail object
            with ignored(Exception):
                values['url'] = Stock.SEARCH_URL % encode(item['label'])
            with ignored(Exception):
                values['polling_url'] = Stock.POLLING_URL % item['code']
            with ignored(Exception):
                values['detail'] = get_json(values['polling_url'])['result']['areas'][0]['datas'][0]
            detail = values['detail']
            try:
                # process detail data
                with ignored(Exception):
                    values['nm'] = detail['nm']
                with ignored(Exception):
                    values['nv'] = '￦ ' + format_num(detail['nv'])
                with ignored(Exception):
                    if detail['nv'] > detail['pcv']:
                        values['sign'] = '+'
                        icon = './icons/red-arrow-up.png'
                    elif detail['nv'] < detail['pcv']:
                        values['sign'] = '-'
                        icon = './icons/blue-arrow-down.png'
                    else:
                        values['sign'] = ' '
                        icon = ''
                with ignored(Exception):
                    values['cr'] = format_num(detail['cr'], 2)
                with ignored(Exception):
                    values['cv'] = format_num(detail['cv'])
                with ignored(Exception):
                    values['space'] = 40 - len(detail['nm'].encode('euc-kr'))
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
                title = (u'{nm:<%s}\t{nv:<15}\t( {sign} {cr} %%, {cv})' % space).format(nm=nm, nv=nv, sign=sign, cr=cr, cv=cv)
                subtitle = u'{market} 거래량: {aq}  고가: {hv}  저가: {lv}  PER: {eps}  PBR: {bps}'.format(market=item['market'], aq=aq, hv=hv, lv=lv, eps=eps, bps=bps)
                self.add(title, subtitle, url, icon)
            except:
                self.add(item['name'], item['market'], url, icon)

    @staticmethod
    def load_favorites():
        if exists(Stock.FAVORITE_FILE):
            with open(Stock.FAVORITE_FILE, 'rb') as f:
                queue = Queue()
                procs = []
                for label in pickle.load(f):
                    proc = Process(target=Stock.get_items, args=(label, queue))
                    procs.append(proc)
                    proc.start()
                for proc in procs:
                    proc.join()
                return sorted(chain(*[queue.get() for _ in procs]), key=lambda x: x['name'])
        else:
            return []

    @staticmethod
    def get_items(query, store=None):
        url = Stock.LIST_URL % query
        data = get_json(url)[u'items']
        items = data_to_dic(data)
        if store:
            store.put(items)
        return items

    def search(self):
        query = get_query(self.arguments)
        if query:
            items = Stock.get_items(query)
        else:
            items = Stock.load_favorites()
        self.build_alfred_items(items)

    def search_for_delete(self):
        self.add('삭제하고 싶은 종목을 선택하세요.')
        items = Stock.load_favorites()
        self.build_alfred_items(items)

    def set_favorite(self):
        url = self.arguments[0]
        label = re.search(r'code=([^&]*)', url).groups()[0]
        if exists(Stock.FAVORITE_FILE):
            with open(Stock.FAVORITE_FILE, 'rb') as f:
                favorites = pickle.load(f)
                favorites.append(label)
        else:
            favorites = [label]
        with open(Stock.FAVORITE_FILE, 'wb') as f:
            pickle.dump(favorites, f)

    def del_favorite(self):
        url = self.arguments[0]
        label = re.search(r'code=([^&]*)', url).groups()[0]
        if exists(Stock.FAVORITE_FILE):
            with open(Stock.FAVORITE_FILE, 'rb') as f:
                favorites = pickle.load(f)
            try:
                favorites.remove(label)
            except:
                pass
        else:
            favorites = []
        with open(Stock.FAVORITE_FILE, 'wb') as f:
            pickle.dump(favorites, f)

    def reset_favorite(self):
        if exists(Stock.FAVORITE_FILE):
            remove(Stock.FAVORITE_FILE)

    def run(self, func):
        getattr(self, func)()


def main():
    command = sys.argv[1]
    stock = Stock(*sys.argv[2:])
    stock.run(command)
    stock.send_feedback()


if __name__ == '__main__':
    main()
