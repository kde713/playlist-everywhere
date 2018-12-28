import os
import sys

from tqdm import tqdm
from PyInquirer import prompt

from playlist_everywhere.application.common import BaseApplication
from playlist_everywhere.vendor import MelonClient, GenieClient, BaseSong, ClientNotAuthenticated


class CliApplication(BaseApplication):
    VENDOR_DICT = {
        'melon': MelonClient,
        'genie': GenieClient,
    }

    def run(self):
        answers = prompt([
            {
                'type': 'list',
                'name': 'action',
                'message': '실행할 작업을 선택하세요.',
                'choices': ['download', 'upload', ]
            },
            {
                'type': 'list',
                'name': 'vendor',
                'message': '서비스 제공사를 선택하세요.',
                'choices': self.VENDOR_DICT.keys(),
            }
        ])
        getattr(self, answers['action'])(answers['vendor'])

    def download(self, vendor_name: str):
        vendor_client = self.VENDOR_DICT[vendor_name]()
        flag = False

        while not flag:
            try:
                answers = prompt([
                    {
                        'type': 'input',
                        'name': 'playlist',
                        'message': '다운로드할 플레이리스트를 입력해주세요. (유형:ID 형식)',
                        'validate': lambda val: len(val.split(":")) == 2 or '올바른 대상을 입력해주세요.',
                    },
                    {
                        'type': 'input',
                        'name': "file_name",
                        'message': '저장할 파일명을 입력해주세요.',
                        'validate': lambda val: len(val) > 0 or '파일명을 올바르게 입력해주세요.',
                    }
                ])
                playlist_type, playlist_id = answers['playlist'].split(":")
                with tqdm(total=100) as progress_bar:
                    progress_bar.set_description("플레이리스트 파싱중")
                    playlist = vendor_client.get_playlist(playlist_type, playlist_id)
                    progress_bar.update(60)
                    progress_bar.set_description("파일 변환중")
                    with open(answers['file_name'], "w", encoding='utf-8') as playlist_file:
                        playlist_file.write(f"{vendor_name}\n")
                        for song in playlist:
                            playlist_file.write(f"{song.id}\t{song.title}\t{song.artist}\n")
                    progress_bar.update(40)
                sys.stdout.write("===== 다운로드 결과 =====\n")
                sys.stdout.write(f"다운로드 곡 수: {len(playlist)}곡\n")
                sys.stdout.write(f"파일: {os.path.realpath(answers['file_name'])}\n")
                sys.stdout.write("====================")
                flag = True

            except ClientNotAuthenticated:
                sys.stderr.write("로그인이 필요합니다.\n")
                credentials = prompt([
                    {
                        'type': 'input',
                        'name': 'account_id',
                        'message': '계정 아이디/이메일을 입력해주세요.',
                        'validate': lambda val: len(val) > 0 or '아이디/이메일을 올바르게 입력해주세요.',
                    },
                    {
                        'type': 'password',
                        'name': 'account_password',
                        'message': '계정 비밀번호를 입력해주세요.',
                        'validate': lambda val: len(val) > 0 or '비밀번호를 올바르게 입력해주세요.',
                    }
                ])
                try:
                    vendor_client.signin(credentials['account_id'], credentials['account_password'])
                except Exception as e:
                    sys.stderr.write(f"오류가 발생했습니다: {e.message}\n")

            except NotImplementedError:
                sys.stderr.write(f"현재 선택하신 제공사에는 준비중인 기능입니다.\n")
                flag = True

            except Exception as e:
                sys.stderr.write(f"오류가 발생했습니다: {e.message}\n")

    def upload(self, vendor_name: str):
        vendor_client = self.VENDOR_DICT[vendor_name]()

        while not vendor_client.is_signin:
            try:
                sys.stderr.write("로그인이 필요합니다.\n")
                credentials = prompt([
                    {
                        'type': 'input',
                        'name': 'account_id',
                        'message': '계정 아이디/이메일을 입력해주세요.',
                        'validate': lambda val: len(val) > 0 or '아이디/이메일을 올바르게 입력해주세요.',
                    },
                    {
                        'type': 'password',
                        'name': 'account_password',
                        'message': '계정 비밀번호를 입력해주세요.',
                        'validate': lambda val: len(val) > 0 or '비밀번호를 올바르게 입력해주세요.',
                    }
                ])
                vendor_client.signin(credentials['account_id'], credentials['account_password'])
            except Exception as e:
                sys.stderr.write(f"오류가 발생했습니다: {e.message}\n")

        sys.stdout.write("로그인 되었습니다.\n")

        try:
            answers = prompt([
                {
                    'type': 'input',
                    'name': 'file_name',
                    'message': '업로드할 플레이리스트 파일명을 입력해주세요. (경로 포함)',
                    'validate': lambda val: os.path.isfile(val) or '올바른 파일을 입력해주세요.',
                },
                {
                    'type': 'input',
                    'name': 'playlist_name',
                    'message': '생성할 플레이리스트명을 입력해주세요.',
                    'validate': lambda val: len(val) > 1 or '올바른 이름을 입력해주세요.',
                }
            ])
            with tqdm(total=100) as progress_bar:
                progress_bar.set_description("파일 불러오는중")

                playlist_vendor = None
                song_list = []
                with open(answers['file_name'], "r", encoding='utf-8') as playlist_file:
                    for line in playlist_file.readlines():
                        if playlist_vendor is None:
                            playlist_vendor = line.strip()
                        else:
                            playlist_id, song_title, song_author = line.strip().split("\t")
                            song_list.append(BaseSong(playlist_id, song_title, song_author))

                progress_bar.update(10.0)
                progress_bar.set_description("음원 검색중")

                matched_song = []
                unmatched_song = []
                progress_per_match = 50 / len(song_list)

                if vendor_name == playlist_vendor:
                    matched_song = song_list
                else:
                    for saved_song in song_list:
                        search_result = vendor_client.search_song(vendor_client.get_keyword_from_song(saved_song))
                        if search_result:
                            matched_song.append(search_result[0])
                        else:
                            unmatched_song.append(str(saved_song))
                        progress_bar.update(progress_per_match)

                progress_bar.set_description("플레이리스트 생성중")

                new_playlist_id = vendor_client.create_personal_playlist(answers['playlist_name'])

                progress_bar.update(10.0)
                progress_bar.set_description("플레이리스트 구성중")

                progress_per_add = 30 / len(matched_song)
                unregistered_song = []
                for song in matched_song:
                    try:
                        vendor_client.add_song_to_personal_playlist(new_playlist_id, song)
                    except Exception as e:
                        unregistered_song.append(f"{str(song)} ({e.message})")
                    progress_bar.update(progress_per_add)

            sys.stdout.write("===== 업로드 결과 =====\n")
            sys.stdout.write(f"불러온 곡 수: {len(song_list)}곡\n")
            sys.stdout.write(f"매치된 곡 수: {len(matched_song)}\n")
            for unmatched in unmatched_song:
                sys.stdout.write(f">>> Not Found - {unmatched}\n")
            sys.stdout.write(f"등록된 곡 수: {len(matched_song) - len(unregistered_song)}곡\n")
            for unregistered in unregistered_song:
                sys.stdout.write(f">>> Add failed - {unregistered}\n")
            sys.stdout.write("====================")

        except NotImplementedError:
            sys.stderr.write(f"현재 선택하신 제공사에는 준비중인 기능입니다.")

        except Exception as e:
            sys.stderr.write(f"오류가 발생했습니다: {e.message}")
