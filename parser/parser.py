import requests
import time
import datetime
from selenium import webdriver
from selenium.common.exceptions import *
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import pytube
import subprocess
import iso8601

import os
import asyncio
import aiohttp
import aiofiles
import pandas as pd
import json

urls = []

config = ""
config_filename = "config.json"

request_semaphone = asyncio.Semaphore(20)

main_url = "https://www.youtube.com"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

video_previews = []

upload_image_count = 0
videos_upload = []
upload_video_count = 0
result_items = []

youtube_api_keys = []
index_api = 0

def load_config(filename):
    print("Загрузка config")
    with open(filename, 'r', encoding='utf-8') as file:
        global config
        config = json.loads(file.read())

def load_api():
    print("Загрузка Api")
    filename = "api.txt"
    with open(filename, 'r', encoding='utf-8') as file:
        items = file.read().split("\n")
        for item in items:
            if (item.strip() != ""):
                print(item)
                youtube_api_keys.append(item)

def load_urls():
    print("Загрузка URL")
    filename = "urls.txt"
    with open(filename, 'r', encoding='utf-8') as file:
        items = file.read().split("\n")
        for item in items:
            if (item.strip() != ""):
                print(item)
                urls.append(item)

def get_api():
    try:
        return youtube_api_keys[index_api]
    except Exception as e:
        print("Не осталось доступных api", e)
        exit(-10)

def set_api():
    global index_api
    index_api+= 1

def init_driver():
    ff = "chromedriver"
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument("headless")
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_option.add_experimental_option("prefs", prefs)


    try:
        # driver = webdriver.Firefox(executable_path=ff)
        driver = webdriver.Chrome(executable_path=ff, options=chrome_option)
        return driver
        # driver = webdriver.Chrome(executable_path=ff, chrome_options=chrome_option, service_args=service_args)
    except SessionNotCreatedException as e:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера", e)



def parse(driver):
    print("Парсинг")
    href_list = []
    driver.get("https://blog.feedspot.com/sports_youtube_channels/")
    scroll(driver)
    while True:
        items = driver.find_elements_by_css_selector("#fsb > p")
        try:
            div_block = driver.find_element_by_css_selector("#fsb > div")
            new_items = div_block.find_elements_by_css_selector("#fsb > div > div")
            all_items = items + new_items
            for item in all_items:
                a = item.find_element_by_css_selector("a.ext")
                href = a.get_attribute("href")
                if(href.find("/videos") == -1):
                    href = href + "/videos"
                print(href)
                href_list.append(href)
            break
        except:
            continue
    driver.close()
    driver.quit()
    return href_list

def request(url, params):
    while True:
        try:
            params["key"] = get_api()
            r = requests.get(url, params=params, headers=headers)
            if(r.status_code == 200):
                return r
            elif(r.status_code == 403):
                print(r.status_code)
                print(r.request)
                print("Ожидание 1 секунда")
                time.sleep(1)
                print("Смена API")
                set_api()
            else:
                print(r.status_code)
                print(r.request)
                print("Ожидание 1 секунда")
                time.sleep(1)
        except Exception as e:
            print("Ожидание 1 секунда", e)
            time.sleep(1)

def search_channel():
    main_url = "https://www.googleapis.com/youtube/v3/search"

def get_channel_name(url):
    items = url.split("/")
    return items[-2]

def get_channel(name_channel):
    main_url = "https://www.googleapis.com/youtube/v3/channels"
    data = {
        "part": "id,snippet,contentDetails,statistics",
        "forUsername": name_channel,
        "maxResults": "1"
    }

    r = request(main_url, data).json()
    try:
        items = r["items"]
        if(len(items) > 0):
            id = items[0]["id"]
            published_at = items[0]["snippet"]["publishedAt"]
            subcriber_count = items[0]["statistics"]["subscriberCount"]
            uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
            data = {
                "id" : id,
                "published_at" : published_at,
                "subcriber_count": subcriber_count,
                "uploads": uploads
            }
            return data

        else:
            #Если не нашло, то возможно название это и есть Id
            return get_channel_by_id(name_channel)
    except:
        return get_channel_by_id(name_channel)

def create_path(path):
    if (os.path.exists(path) == False):

        try:
            os.mkdir(path)
            print("Создание папки для сохранения ", path)
        except OSError as e:
            print("Папка для сохранения не создана", e, path)
            exit(-10)


def get_channel_by_id(id):
    main_url = "https://www.googleapis.com/youtube/v3/channels"
    print("Запрос повтор", id)
    data = {
        "id": id,
        "part": "id, snippet, contentDetails, statistics",
        "maxResults": "1"
    }
    r = request(main_url, data)
    print("Retry", r.text)
    new_data = r.json()
    try:
        items = new_data["items"]
    except:
        items = []
    if (len(items) > 0):
        id = items[0]["id"]
        published_at = items[0]["snippet"]["publishedAt"]
        subcriber_count = items[0]["statistics"]["subscriberCount"]
        uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        data = {
            "id": id,
            "published_at": published_at,
            "subcriber_count": subcriber_count,
            "uploads": uploads
        }
        return data
    else:
        return None


def get_duration(text):
    # text = text.replace("H", "")
    # index_p = text.find("PT")
    # index_m = text.find("M")
    # hours = text[0: index_p]
    # if hours == "":
    #     hours = "00"
    # minutes = text[index_p + 2: index_m]
    # if(len(minutes) == 1):
    #     minutes = "0" + minutes
    # seconds = text[index_m + 1: -1]
    # if (len(seconds) == 1):
    #     seconds = "0" + seconds
    #
    # result = hours + ":" + minutes + ":" + seconds
    return text


def get_channel_founded(published_at):
    date = iso8601.parse_date(published_at)
    return date.strftime("%d-%m-%y %H:%M:%S")


def parse_youtube(url):
    last_items = []
    name_channel = get_channel_name(url)
    channel = get_channel(name_channel)
    if(channel is None):
        return
    id_channel = channel["id"]
    published_at = channel["published_at"]
    subcriber_count = channel["subcriber_count"]
    uploads = channel["uploads"]
    # print(name_channel)
    # print(id_channel)
    # print(published_at)
    # print(subcriber_count)
    # print(uploads)

    items = get_playlist_items_by_playlist_id(uploads)
    # print("VIDEOS", items)
    for index, item in enumerate(items):
        item_id = item["id"]
        # video_more = get_video(video_id)
        # print("More", video_more)
        # video_title = video["snippet"]["title"]
        # video_desription = video_more["snippet"]["description"]
        # video_published_at = video_more["snippet"]["publishedAt"]
        # try:
        #     video_preview = video_more["snippet"]["thumbnails"]["maxres"]["url"]
        # except:
        #     video_preview = video_more["snippet"]["thumbnails"]["standard"]["url"]

        video_id = item["contentDetails"]["videoId"]
        video = get_video(video_id)
        video_title = video["snippet"]["title"]
        video_desription = video["snippet"]["description"]
        video_published_at = video["snippet"]["publishedAt"]
        blocks = ["maxres", "standard", "high", "medium", "default"]
        for block in blocks:
            try:
                video_preview = video["snippet"]["thumbnails"][block]["url"]
                break
            except:
                continue

        try:
            video_tag = video["snippet"]["tags"]
            tag = ",".join(video_tag)
        except:
            tag = None
        video_duration = get_duration(video["contentDetails"]["duration"])
        try:
            video_view_count = video["statistics"]["viewCount"]
        except:
            video_view_count = None
        try:
            video_like_count = video["statistics"]["likeCount"]
        except:
            video_like_count = None
        try:
            video_dislike_count = video["statistics"]["dislikeCount"]
        except:
            video_dislike_count = None
        try:
            video_favorite_count = video["statistics"]["favoriteCount"]
        except:
            video_favorite_count = None
        try:
            video_comment_count = video["statistics"]["commentCount"]
        except:
            video_comment_count = None

        video_preview_name = video_preview.split("/")[-2]
        # # # print(video_title)
        # # # print(video_desription)
        # # print(video_published_at)
        # # print("isToday:", isToday(video_published_at))
        # # # print(video_preview)


        all = {
            "video_id" : video_id,
            "video_duration" : video_duration,
            "video_title" : video_title,
            "review": video_preview_name + ".jpg",
            "video": video_id + ".mp4",
            "description" : video_desription,
            "channel_founded": get_channel_founded(published_at),
            "published_at" : get_channel_founded(video_published_at),
            "subcriber_count" : subcriber_count,
            "tags" : tag
        }
        if(index > 0):
            last_item = last_items[-1]
            last_item["view_count"] = video_view_count
            last_item["like_count"] = video_like_count
            last_item["dislike_count"] = video_dislike_count
            last_item["favorite_count"] = video_favorite_count
            last_item["comment_count"] = video_comment_count
            last_item["data_published_at_last_video"] = get_channel_founded(published_at)
            last_item["title_last_video"] = video_title
        if(isToday(video_published_at)):
            last_items.append(all)
            video_previews.append([video_preview, video_preview_name])
            videos_upload.append(video_id)
        else:
            break
    global result_items
    result_items = result_items + last_items



def get_video(video_id):
    main_url = "https://www.googleapis.com/youtube/v3/videos"
    data = {
        'id': video_id,
        'part': 'id, contentDetails, snippet, statistics',
    }
    r = request(main_url, data).json()
    return r["items"][0]

def get_playlist_items_by_playlist_id(playlist_id, max_results=50):
    main_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    data = {
        'playlistId': playlist_id,
        'part': 'id, contentDetails, snippet',
        'maxResults': max_results
    }
    r = request(main_url, data).json()
    return r["items"]

def scroll(driver, count = 600000000):
    text = "window.scrollTo(0," + str(count) +");"
    driver.execute_script(text)

async def save_image(r, name):
    start_time = time.time()
    path_image = "images/" + name + ".jpg"
    if (os.path.exists(path_image) == False):
        f = await aiofiles.open(path_image, mode='wb')
        await f.write(await r.read())
        await f.close()
        global upload_image_count
        upload_image_count = upload_image_count + 1
        print("Скачивание изображения:", path_image, '[{0:0.2f} c]'.format(time.time() - start_time), '[{0:0.2f} %]'.format(upload_image_count * 100 / len(video_previews)))



async def async_request(item):
    url = item[0]
    base_host = item[1]
    global request_semaphone
    async with request_semaphone:
        try:
            async with aiohttp.ClientSession() as client:
                async with client.get(url) as r:
                    print("Статус:", r.status , "url:", url)
                    if(r.status == 200):
                        await save_image(r, base_host)
                        return ["is_saved_image"]

                    elif(r.status == 404):
                        return ["not found"]

                    else:
                        return [None, url, base_host]

        except Exception as e:
            print("Блокировка. Ожидание 1 секунд", e, url)
            await asyncio.sleep(1)
            return [None, url, base_host]


async def crawl(future):
    futures = []
    # Получаем из футуры ссылки
    items = await future
    # new_items = chunks(items, limit_packet)

    # for new_item in new_items:
    for item in items:
        await async_request(item)



async def start_main(root_urls):
    loop = asyncio.get_event_loop()
    initial_future = loop.create_future()
    initial_future.set_result(root_urls)
    await crawl(initial_future)


def save_video(video_id):
    global upload_video_count
    url = None
    items =["144p", "240p", "360p", "480p", "720p", "1080p"]
    url_video = "https://www.youtube.com/watch?v=" + video_id
    print("Скачивание видео", url_video)
    for item in items:
        try:
            url = pytube.YouTube(url_video).streams.filter(res=item)[0].url
            print("Разрешение", item, url)
            break
        except Exception as e:
            url = None
            continue


    if(url != None):
        if (os.path.exists("videos/" + video_id + ".mp4") == False):
            for i in range(5):
                try:
                    process_call_str = 'ffmpeg -loglevel quiet -ss {1} -to {2} -i "{0}" -vcodec copy -acodec copy "{3}"'.format(
                        str(url), str("00:00:00"), str("00:06:00"), "videos/" + video_id + ".mp4")
                    status = subprocess.check_call(process_call_str, shell=True)
                    upload_video_count = upload_video_count + 1
                    print("Видео", url_video, "загружено",  '[{0:0.2f} %]'.format(upload_video_count * 100 / len(videos_upload)))
                    break
                except:
                    continue

        else:
            upload_video_count = upload_video_count + 1
            print("Видео уже имеется", url_video, '[{0:0.2f} %]'.format(upload_video_count * 100 / len(videos_upload)))
    else:
        upload_video_count = upload_video_count + 1
        print("Видео", url_video, "загрузить не удалось", '[{0:0.2f} %]'.format(upload_video_count * 100 / len(videos_upload)))

def isToday(text):
    current = iso8601.parse_date(text)
    curr = datetime.datetime.utcnow().replace(tzinfo=iso8601.UTC)
    period = curr - current
    # print(current)
    # print(curr)
    if((period.total_seconds() <= 12960000) or (period.total_seconds() >= 31104000)):
        return False
    return True


def save_result(items):
    print("Сохранение результатов")
    df = pd.DataFrame(items)
    df.to_excel("results/result.xlsx", index=False)
    df.to_csv("results/result.csv", index=False, encoding='utf-8-sig')

if __name__ == '__main__':

    starr_time = time.time()
    load_config(config_filename)
    create_path("images/")
    create_path("videos/")
    create_path("results/")
    load_api()
    if(config["is_parsed_site"] == "true"):
        driver = init_driver()
        urls = parse(driver)
        urls = list(set(urls))
        print("Количество элементов:", len(urls))
    if (config["is_parsed_custom"] == "true"):
        load_urls()
    for url in urls[0:1]:
        parse_youtube(url)
    save_result(result_items)

    # print("Скачивание Preview")
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(start_main(video_previews))
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
    #Скачивание видео
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        for _ in executor.map(save_video, videos_upload):
            pass

    print("Время выполнения скрипта", time.time() - starr_time)

    # parse_youtube("https://www.youtube.com/user/corycotton/videos")






