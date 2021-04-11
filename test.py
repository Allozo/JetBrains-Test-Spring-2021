from YouTubeStatistic import YouTubeStatistic


def test():
    API_KEY = 'AIzaSyD114JzSn1qQbI5R4vjzwBnO9I5PU5KvFs'
    channel_id_ExtremeCode = 'UCBNlINWfd08qgDkUTaUY4_w'

    yts = YouTubeStatistic(API_KEY, channel_id_ExtremeCode)

    yts.load_instance()

    # yts.update_channel_statistics()
    # print(yts.get_channel_statistics())

    # Соберем статистику по последним видео
    # count_video = 20
    # yts.update_video_data(count_video)
    # print(yts.get_video_data())

    # Получим все видео
    # yts.update_video_data()

    # yts.dump_instance()

    yts.save_data_json()


if __name__ == '__main__':
    test()