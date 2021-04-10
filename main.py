from YouTubeStatistic import YouTubeStatistic


def test():
    API_KEY = 'AIzaSyD114JzSn1qQbI5R4vjzwBnO9I5PU5KvFs'
    channel_id_g1deon = 'UCNJ0iop1uEVhw-tOZUxKM5Q'
    channel_id_pewdiepie = 'UC-lHJZR3Gqxm24_Vd_AJ5Yw'
    channel_id_jove = 'UCDx2-SCLzDaC4vlh2PCGYQA'

    yts = YouTubeStatistic(API_KEY, channel_id_g1deon)

    # yts.load_instance()

    yts.update_channel_statistics()
    # print(yts.get_channel_statistics())

    # Соберем статистику по последним видео
    count_video = 20
    yts.update_video_data(count_video)
    # print(yts.get_video_data())

    # yts.dump_instance()

    yts.save_data_json()


if __name__ == '__main__':
    test()