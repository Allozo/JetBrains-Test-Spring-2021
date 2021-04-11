import requests
import json
from tqdm import tqdm
import pickle
import datetime
from pathlib import Path


class YouTubeStatistic:
    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_statistics = None
        self.video_data = None

    def get_channel_statistics(self):
        return self.channel_statistics

    def get_video_data(self):
        return self.video_data

    def update_channel_statistics(self):
        """
        Получает данные о канале. В случае успеха записывает их в поле
        channel_statistics. В случае не успеха выводит сообщение об ошибке
        и записывает пустой словарь в то же самое поле.
        :return:
        """
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'  # noqa
        json_url = requests.get(url)
        data = json.loads(json_url.text)

        print("Получаем данные о канале.")

        try:
            data = data['items'][0]['statistics']
        except KeyError:
            print('Не удалось получить данные о канале.')
            print('Проверьте правильность указанного channel_id.')
            data = None

        self.channel_statistics = data

    def _get_video_from_json_page(self, url):
        """
        Получает на вход url, из него достает список видео и ссылку
        на следующую страницу (если она есть)
        :param url:
        :return:
        """
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = []

        if 'items' not in data:
            return channel_videos, None

        item_data = data['items']
        next_page_token = data.get('nextPageToken', None)

        for item in item_data:
            try:
                kind = item['id']['kind']
                if kind == 'youtube#video':
                    video_id = item['id']['videoId']
                    channel_videos.append(video_id)
            except KeyError:
                print('Ошибка при попытке получить видео из json')

        return channel_videos, next_page_token

    def _get_channel_videos(self, count_video):
        """
        Получим список длиной count_video, где будут id видео
        :param count_video:
        :return:
        """
        # Получим json с 50 видео в одном запросе
        limit = 50
        url = f'https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=id&order=date'  # noqa
        url += f'&maxResults={str(limit)}'

        list_video = []
        next_page_token = 1
        while (count_video is None or len(list_video) < count_video) and next_page_token is not None:
            # Если впервый раз зашли в цикл, то получаем видео с url.
            # Если уже были итерации, внутри цикла, то дописываем url.
            if next_page_token == 1:
                next_url = url
            else:
                next_url = url + "&pageToken=" + next_page_token

            now_list_video, next_page_token = self._get_video_from_json_page(next_url)

            # Если получаем все видео канала
            if count_video is None:
                list_video += now_list_video
                continue

            # Если получаем только часть видео
            for video_id in now_list_video:
                if len(list_video) < count_video:
                    list_video.append(video_id)

        return list_video

    def _get_single_video_data(self, video_id, type):
        url = f'https://www.googleapis.com/youtube/v3/videos?part={type}&id={video_id}&key={self.api_key}'
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0][type]
        except KeyError:
            print(f"Не удалось получить данные для видео с id={video_id}")
            print(f"Ссылка {url} оказалась недействительной")
            data = dict()
        return data

    def update_video_data(self, count_video=None):
        """
        Получим статистикку по последним count_video. Если count_video
        не указано, то хотим получить все видео
        :param count_video:
        :return:
        """
        #  Получим последние count_video видео канала
        print(f"Получаем видео канала.")
        list_videos = self._get_channel_videos(count_video)

        # Получим статистику по полученным видео
        print(f"Получаем статистику по {len(list_videos)} видео.")
        videos_with_statistic = dict()
        parts = ['snippet', 'statistics']
        for video_id in tqdm(list_videos):
            videos_with_statistic[video_id] = {}
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                videos_with_statistic[video_id].update(data)

        self.video_data = videos_with_statistic

    def dump_instance(self):
        with open('backup_instance', 'wb') as file:
            pickle.dump(self, file)

    def load_instance(self):
        with open('backup_instance', 'rb') as file:
            t = pickle.load(file)
            self.video_data = t.video_data
            self.channel_statistics = t.channel_statistics

    def save_data_json(self):
        if self.video_data is None or self.channel_statistics is None:
            print('Нет данных для сохранения')
            return

        # Получим имя канала
        name_channel = self.video_data.popitem()[1]['channelTitle']

        # Получим сегодняшнюю дату
        date = datetime.date.today().strftime('%d-%m-%Y')

        # Запишем в словарь статистику которую получили - её будем
        # будем дописывать в существующий файл
        statistic_now = {
            date: {
                'channel_statistic': self.channel_statistics,
                'videos_statistic': self.video_data
            }
        }

        file_name = f'statistic_channels.json'
        try:
            # Добавим в уже существующий файл данные
            path_file = Path(file_name)

            data = json.loads(path_file.read_text(encoding='utf-8'))

            # Если такого канала еще нет в файле со статистикой, то
            # создадим его там
            if name_channel not in data:
                data[name_channel] = {}
            data[name_channel].update(statistic_now)
            path_file.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
            print("Данные дописаны в существующий файл.")
        except FileNotFoundError:
            # Если не получилось открыть файл, то создадим его
            # и запишем данные с нуля
            json_res = {
                name_channel: statistic_now
            }

            with open(file_name, 'w', encoding="utf-8") as file:
                json.dump(json_res, file, indent=4, ensure_ascii=False, default=str)
            print(f"Данные сохранены в новый файл с именем {file_name}.")
