#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from requests import Session


class ClientNotAuthenticated(Exception):
    """클라이언트 로그인 필요 오류"""
    pass


class BaseSong:
    """
    음원사 관계없이 음원을 공통적으로 다루기 위한 추상 곡 모델

    Attributes:
        id (str): 음원사에서 자체적으로 부여하는 곡 구분번호
        title (str): 음원 제목
        artist (str): 음원 가수
    """

    id: str
    title: str
    artist: str

    def __init__(self, id: str, title: str, artist: str):
        self.id = id
        self.title = title
        self.artist = artist

    def __str__(self):
        return f"{self.artist} - {self.title}"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}', '{self.title}', '{self.artist}')"


class BaseClient:
    """
    음원사 관계없이 공통 처리를 위한 추상 클라이언트 모델

    Attributes:
        session: 클라이언트에서 네트워크 요청을 처리하고 세션을 유지하기 위한 requests.Session 객체
        is_signin (bool): 로그인 여부
        additional_data (dict): 추가 데이터
    """

    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        })
        self.is_signin = False
        self.additional_data = {}

    def signin(self, account_id: str, account_password: str):
        """
        음원사 로그인

        Args:
            account_id (str): 계정 ID (아이디 또는 이메일)
            account_password (str): 계정 비밀번호

        Returns:
            반환값은 없습니다. 로그인 실패 시 Exception을 발생시켜야합니다.
        """
        raise NotImplementedError('로그인 기능이 지원되지 않는 vendor입니다.')

    def get_keyword_from_song(self, song: BaseSong) -> str:
        """
        곡 검색을 위한 키워드 생성

        Args:
            song (:obj:`BaseSong`): 대상 곡 인스턴스

        Returns:
            (str) 검색 키워드를 반환합니다.
        """
        return str(song)

    def search_song(self, keyword: str) -> List[BaseSong]:
        """
        곡 키워드 검색

        Args:
            keyword (str): 검색 키워드

        Returns:
            (:obj:`list` of :obj:`BaseSong`) 검색 결과 곡을 담은 리스트를 반환합니다
        """
        raise NotImplementedError('곡 검색 기능이 지원되지 않는 vendor입니다.')

    def get_playlist(self, playlist_type: str, playlist_id: str) -> List[BaseSong]:
        """
        플레이리스트 포함 곡 추출

        Args:
            playlist_type (str): 플레이리스트 유형 (음원사에 여러 플레이리스트 유형이 있을 시 사용합니다)
            playlist_id (str): 플레이리스트 고유번호 (음원사에서 자체적으로 부여하는 플레이리스트 구분 번호)

        Returns:
            (:obj:`list` of :obj:`BaseSong`) 플레이리스트의 곡을 담은 리스트를 반환합니다
        """
        raise NotImplementedError('플레이리스트 파싱 기능이 지원되지 않는 vendor입니다.')

    def create_personal_playlist(self, playlist_name: str) -> str:
        """
        개인 플레이리스트 생성

        Args:
            playlist_name (str): 플레이리스트 이름

        Returns:
            (str) 플레이리스트 고유번호
        """
        raise NotImplementedError('개인 플레이리스트 생성 기능이 지원되지 않는 vendor 입니다.')

    def add_song_to_personal_playlist(self, playlist_id: str, song: BaseSong):
        """
        개인 플레이리스트에 곡 추가

        Args:
            playlist_id (str): 플레이리스트
            song (:obj:`BaseSong`): 추가할 곡

        Returns:
            반환값은 없습니다. 곡 추가 실패 시 Exception을 발생시켜야합니다.
        """
        raise NotImplementedError('개인 플레이리스트에 노래 추가 기능이 지원되지 않는 vendor 입니다.')
