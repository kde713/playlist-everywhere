#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from typing import List

from bs4 import BeautifulSoup

from playlist_everywhere.vendor.common import BaseSong, BaseClient, ClientNotAuthenticated


class GenieClient(BaseClient):
    def signin(self, account_id: str, account_password: str):
        login_request = self.session.post("https://www.genie.co.kr/auth/signIn", data={
            'login_suxd': "",
            'login_suxn': "",
            'login_suxt': "",
            'chk': "",
            'login_http': "https",
            'uxd': account_id,
            'uxx': account_password,
            'ucc': "",
            'uxglk': 0,
            'f_JoinType': "",
            'mh': "",
            'lk_rfr': "",
        })
        user_no_match = re.findall(r'var iMemUno = \"(\d+)\";', login_request.text)
        if not login_request.cookies.get('GENIE%5FUXD') or not user_no_match:
            raise ClientNotAuthenticated('로그인 정보가 올바르지 않습니다')
        self.additional_data['user_no'] = user_no_match[0]
        self.is_signin = True

    def search_song(self, keyword: str) -> List[BaseSong]:
        search_request = self.session.get("https://www.genie.co.kr/search/searchSong", params={
            'query': keyword,
            'Coll': ''
        })
        parser = BeautifulSoup(search_request.text, 'html.parser')

        search_list_dom = parser.select('div.music-list-wrap tr.list')
        if len(search_list_dom) < 1:
            return []

        search_result = []
        for search_item_dom in search_list_dom:
            song_id = search_item_dom['songid']
            song_title_dom = search_item_dom.select("td.info > a.title")[0]
            for junk_icon in song_title_dom.find_all("span", "icon"):
                junk_icon.decompose()
            song_title = song_title_dom.get_text().strip()
            song_artist = search_item_dom.select("td.info > a.artist")[0].get_text().strip()
            search_result.append(BaseSong(song_id, song_title, song_artist))

        return search_result

    def get_playlist(self, playlist_type: str, playlist_id: str) -> List[BaseSong]:
        raise NotImplementedError("지니 플레이리스트 조회 기능은 준비중입니다.")

    def create_personal_playlist(self, playlist_name: str) -> str:
        if not self.is_signin:
            raise ClientNotAuthenticated('로그인이 필요합니다.')

        create_requset = self.session.post("https://www.genie.co.kr/myMusic/jSetNewAlbum", data={
            'unm': self.additional_data['user_no'],
            'albumName': playlist_name,
        })
        result = create_requset.json()
        if result['DATA0'] and result['DATA0'].get('newMyAlbumResult', None):
            return result['DATA0']['newMyAlbumResult']

        raise Exception(f'개인 플레이리스트 생성에 실패했습니다. ({result["Result"].get("RetMsg")})')

    def add_song_to_personal_playlist(self, playlist_id: str, song: BaseSong):
        if not self.is_signin:
            raise ClientNotAuthenticated('로그인이 필요합니다.')

        add_request = self.session.post("https://www.genie.co.kr/myMusic/jMyAlbumSongAdd", data={
            'mxnm': playlist_id,
            'xgnms': song.id,
            'mxlopths': 'W',
            'mxflgs': 1,
            'unm': self.additional_data['user_no'],
        })
        result = add_request.json()
        if str(result["Result"].get("RetCode")) != "0":
            raise Exception(f'곡 추가에 실패했습니다. ({result["Result"].get("RetMsg")})')
