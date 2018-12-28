#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from typing import List

from bs4 import BeautifulSoup

from playlist_everywhere.vendor.common import BaseSong, BaseClient


class MelonClient(BaseClient):
    def get_playlist(self, playlist_type: str, playlist_id: str) -> List[BaseSong]:
        if playlist_type == "dj":
            return self.get_djplaylist(playlist_id)

        else:
            raise ValueError('올바르지 않은 플레이리스트 유형입니다.')

    def get_djplaylist(self, playlist_id: str) -> List[BaseSong]:
        navigation_pattern = re.compile(r'\$\(\'#pageObjNavgation\'\)\.html\(\"(.*?)\"\)', re.DOTALL)
        result_songs = []
        start_index = 1
        is_end_of_playlist = False
        while not is_end_of_playlist:
            list_request = self.session.get("https://www.melon.com/dj/playlist/djplaylist_listsong.htm", params={
                'startIndex': start_index,
                'pageSize': 50,
                'plylstSeq': playlist_id,
            })
            parser = BeautifulSoup(list_request.text, 'html.parser')
            for song_item_dom in parser.select("table tbody tr"):
                song_item_attr_dom = song_item_dom.select("td")
                song_id = song_item_attr_dom[0].select("input")[0]['value']
                song_title = song_item_attr_dom[4].select('div.ellipsis.rank01 a')[0].get_text().strip()
                song_artist = song_item_attr_dom[4].select('div.ellipsis.rank02 a')[0].get_text().strip()
                result_songs.append(BaseSong(song_id, song_title, song_artist))

            navigation_text = navigation_pattern.findall(list_request.text)[0]
            next_navigation_text = navigation_text.split("현재페이지")[1]
            is_end_of_playlist = "sendPage" not in next_navigation_text
            start_index += 50
        return result_songs
