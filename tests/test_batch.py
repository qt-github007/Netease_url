import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
from music_downloader import MusicDownloader, MusicInfo
from openpyxl import Workbook
from werkzeug.datastructures import FileStorage


class SongIdExtractionTests(unittest.TestCase):
    def test_extracts_ids_and_song_links_in_order_without_duplicates(self):
        content = """
        185668
        https://music.163.com/song?id=123456&userid=1
        "https://music.163.com/#/song?id=789012",备注
        185668, 345678
        https://example.com/song?id=999999
        """

        self.assertEqual(
            main.api_service.extract_music_ids_from_text(content),
            ['185668', '123456', '789012', '345678'],
        )

    def test_rejects_non_netease_url(self):
        with self.assertRaisesRegex(ValueError, '只支持'):
            main.api_service._extract_music_id('https://example.com/song?id=185668')

    def test_supports_fragment_song_url(self):
        music_id = main.api_service._extract_music_id(
            'https://music.163.com/#/song?id=185668'
        )
        self.assertEqual(music_id, '185668')

    def test_batch_is_split_at_200(self):
        values = [str(100000 + index) for index in range(298)]
        music_ids = main.api_service.validate_batch_ids(values)
        batches = main.api_service.split_batch_ids(music_ids)

        self.assertEqual([len(batch) for batch in batches], [200, 98])

    def test_file_limit_is_enforced(self):
        values = [str(100000 + index) for index in range(2001)]
        with self.assertRaisesRegex(ValueError, '最多识别 2000 首'):
            main.api_service.validate_batch_ids(values)

    def test_extracts_ids_from_excel_headers_and_hyperlinks(self):
        workbook = Workbook()
        summary = workbook.active
        summary.title = '说明与汇总'
        summary['A1'] = '这些数字不是歌曲列表：20260829、302'
        result = workbook.create_sheet('匹配结果')
        result.append(['标题'])
        result.append([])
        result.append([])
        result.append(['序号', '歌曲 ID', '网易云链接'])
        result.append([1, 27927803, 'https://music.163.com/song?id=27927803'])
        result.append([2, 2018734484, '点此打开'])
        result['C6'].hyperlink = 'https://music.163.com/song?id=2018734484'
        result.append([3, 27927803, 'https://music.163.com/song?id=27927803'])

        stream = io.BytesIO()
        workbook.save(stream)
        workbook.close()
        stream.seek(0)

        uploaded = FileStorage(stream=stream, filename='songs.xlsx')
        self.assertEqual(
            main.api_service.read_song_ids_from_upload(uploaded),
            ['27927803', '2018734484'],
        )

    def test_song_name_queries_keep_order_and_remove_duplicates(self):
        queries = main.api_service.validate_song_queries([
            ' 晴天 周杰伦\n海阔天空 Beyond\n晴天 周杰伦 ',
            'HERO\nhero',
        ])

        self.assertEqual(queries, ['晴天 周杰伦', '海阔天空 Beyond', 'HERO'])

    def test_song_name_txt_only_accepts_txt(self):
        uploaded = FileStorage(stream=io.BytesIO('晴天'.encode()), filename='songs.csv')
        with self.assertRaisesRegex(ValueError, '仅支持 .txt'):
            main.api_service.read_song_names_from_upload(uploaded)

    def test_song_name_match_prefers_matching_artist_over_first_result(self):
        first_result = {
            'name': '晴天（翻唱版）',
            'artists': '其他歌手',
            'album': '翻唱合集',
        }
        matching_artist = {
            'name': '晴天',
            'artists': '周杰伦',
            'album': '叶惠美',
        }

        self.assertGreater(
            main.api_service._score_song_match('晴天 | 周杰伦', matching_artist),
            main.api_service._score_song_match('晴天 | 周杰伦', first_result),
        )

    @patch('main.search_music')
    def test_explicit_artist_mismatch_requires_manual_confirmation(self, mocked_search):
        mocked_search.return_value = [{
            'id': 2064191772,
            'name': '晴天周杰伦',
            'artists': '其他歌手',
            'album': '测试专辑',
            'picUrl': '',
        }]

        result = main.api_service.resolve_song_name('晴天 | 周杰伦', {})

        self.assertTrue(result['success'])
        self.assertFalse(result['artist_matched'])
        self.assertFalse(result['auto_selected'])


class BatchApiTests(unittest.TestCase):
    def setUp(self):
        main.app.config.update(TESTING=True)
        self.client = main.app.test_client()

    @staticmethod
    def fake_song_detail(music_id):
        return {
            'songs': [{
                'id': music_id,
                'name': f'歌曲{music_id}',
                'ar': [{'name': '测试歌手'}],
                'al': {'name': '测试专辑', 'picUrl': 'https://example.com/cover.jpg'},
            }]
        }

    @staticmethod
    def fake_song_url(music_id, level, cookies):
        if int(music_id) == 222222:
            raise main.APIException('测试解析失败')
        return {
            'data': [{
                'id': music_id,
                'url': f'https://example.com/{music_id}.flac',
                'level': level,
                'size': 1024,
                'type': 'flac',
            }]
        }

    @patch('main.url_v1', return_value={'data': [{'url': None}]})
    @patch('main.name_v1')
    def test_batch_summary_marks_missing_download_url_as_failure(
        self, mocked_detail, mocked_url
    ):
        mocked_detail.return_value = self.fake_song_detail(111111)

        result = main.api_service.parse_song_summary('111111', 'standard', {})

        self.assertFalse(result['success'])
        self.assertIn('未获取到下载链接', result['error'])

    @patch('main.load_cookies', return_value={})
    @patch('main.url_v1', side_effect=fake_song_url.__func__)
    @patch('main.name_v1', side_effect=fake_song_detail.__func__)
    def test_batch_parse_uploaded_txt_keeps_partial_failures(
        self, mocked_detail, mocked_url, mocked_cookies
    ):
        upload = (
            io.BytesIO(
                b'111111\nhttps://music.163.com/song?id=222222\n111111\n333333\n'
            ),
            'songs.txt',
        )
        response = self.client.post(
            '/batch/parse',
            data={'file': upload, 'level': 'lossless'},
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()['data']
        self.assertEqual(payload['ids'], ['111111', '222222', '333333'])
        self.assertEqual(payload['total'], 3)
        self.assertEqual(payload['succeeded'], 2)
        self.assertEqual(payload['failed'], 1)
        self.assertFalse(payload['results'][1]['success'])

    def test_batch_parse_rejects_unsupported_file(self):
        response = self.client.post(
            '/batch/parse',
            data={'file': (io.BytesIO(b'185668'), 'songs.json')},
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('TXT', response.get_json()['message'].upper())

    @patch.object(main.api_service, '_get_cookies', return_value={})
    @patch('main.search_music')
    def test_batch_resolve_names_returns_ids_links_and_partial_failures(
        self, mocked_search, mocked_cookies
    ):
        songs = {
            '晴天 周杰伦': [{
                'id': 186016,
                'name': '晴天',
                'artists': '周杰伦',
                'album': '叶惠美',
                'picUrl': 'https://example.com/1.jpg',
            }],
            '海阔天空 Beyond': [{
                'id': 347230,
                'name': '海阔天空',
                'artists': 'Beyond',
                'album': '乐与怒',
                'picUrl': 'https://example.com/2.jpg',
            }],
            '不存在的测试歌曲': [],
        }
        mocked_search.side_effect = lambda query, cookies, limit: songs[query]

        response = self.client.post(
            '/batch/resolve-names',
            data={
                'content': '晴天 周杰伦',
                'file': (
                    io.BytesIO('海阔天空 Beyond\n不存在的测试歌曲'.encode()),
                    'names.txt',
                ),
            },
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()['data']
        self.assertEqual(payload['total'], 3)
        self.assertEqual(payload['succeeded'], 2)
        self.assertEqual(payload['failed'], 1)
        self.assertEqual(payload['ids'], ['347230', '186016'])
        self.assertEqual(
            payload['results'][0]['link'],
            'https://music.163.com/song?id=347230',
        )
        self.assertFalse(payload['results'][1]['success'])

    @patch.object(main.api_service, '_get_cookies', return_value={})
    @patch.object(main.api_service, 'parse_song_summary')
    def test_batch_parse_automatically_splits_more_than_200_ids(
        self, mocked_parse, mocked_cookies
    ):
        mocked_parse.side_effect = lambda music_id, level, cookies: {
            'id': music_id,
            'success': True,
        }
        ids = [str(100000 + index) for index in range(298)]

        response = self.client.post(
            '/batch/parse',
            json={'ids': ids, 'level': 'standard'},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()['data']
        self.assertEqual(payload['total'], 298)
        self.assertEqual(payload['batch_size'], 200)
        self.assertEqual(payload['batch_count'], 2)
        self.assertEqual(mocked_parse.call_count, 298)

    def test_batch_download_returns_zip_and_failure_summary(self):
        class FakeDownloader:
            def __init__(self, download_dir, **kwargs):
                self.download_dir = Path(download_dir)
                self.download_dir.mkdir(parents=True, exist_ok=True)

            def download_music_file(self, music_id, quality):
                if music_id == 222222:
                    return SimpleNamespace(
                        success=False,
                        file_path=None,
                        error_message='测试下载失败',
                    )
                file_path = self.download_dir / f'歌曲{music_id} [{quality}].flac'
                file_path.write_bytes(f'audio-{music_id}'.encode())
                return SimpleNamespace(
                    success=True,
                    file_path=str(file_path),
                    error_message='',
                )

        with patch('main.MusicDownloader', FakeDownloader):
            response = self.client.post(
                '/batch/download',
                json={
                    'ids': ['111111', '222222', '333333'],
                    'quality': 'lossless',
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')
        self.assertEqual(response.headers['X-Batch-Succeeded'], '2')
        self.assertEqual(response.headers['X-Batch-Failed'], '1')

        with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
            names = archive.namelist()
            self.assertIn('歌曲111111 [lossless].flac', names)
            self.assertIn('歌曲333333 [lossless].flac', names)
            self.assertIn('批量下载结果.txt', names)
            summary = archive.read('批量下载结果.txt').decode('utf-8-sig')
            self.assertIn('成功：2 首', summary)
            self.assertIn('222222: 测试下载失败', summary)
        response.close()


class DownloadFilenameTests(unittest.TestCase):
    def test_download_path_contains_id_and_quality(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = MusicDownloader(download_dir=temp_dir, ffmpeg_path='/tmp/ffmpeg')
            info = MusicInfo(
                id=185668,
                name='稻香',
                artists='周杰伦',
                album='魔杰座',
                pic_url='',
                duration=0,
                track_number=0,
                download_url='https://example.com/test.flac',
                file_type='flac',
                file_size=1024,
                quality='lossless',
            )

            file_path = downloader._build_file_path(info)
            self.assertEqual(file_path.name, '周杰伦 - 稻香 [lossless] (185668).flac')


if __name__ == '__main__':
    unittest.main()
