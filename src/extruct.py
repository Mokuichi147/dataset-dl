from os.path import join
import re
import sys
from urllib.parse import parse_qs, urlparse


def get_video_id(url: str) -> str:
    """\
    https://www.youtube.com/watch?v={video_id}
    https://youtube.com/embed/{video_id}
    https://youtu.be/{video_id}
    https://youtube.com/watch?v={video_id}&list={playlist_id}
    """
    video_ids = re.findall(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if len(video_ids) == 0:
        return ''
    return video_ids[0]


def get_playlist_id(url: str) -> str:
    """\
    https://youtube.com/playlist?list={playlist_id}
    https://youtube.com/watch?v={video_id}&list={playlist_id}
    """
    url_query = parse_qs(urlparse(url).query)
    list_query = url_query.get('list')
    if list_query == None:
        return ''
    return list_query[0]


def file_hash(original_name: str) -> str:
    return str(hash(original_name)).replace('-', '#')


def file_name(original_name: str) -> str:
    symbols = [(':',';'),
               ('/','／'),
               ('\0','￥'),
               ('\\','￥'),
               ('*', '＊'),
               ('?','？'),
               ('"','”'),
               ('<','＜'),
               ('>','＞'),
               ('|','｜')]
    for ng, ok in symbols:
        original_name = original_name.replace(ng, ok)
    
    # Mac
    if original_name.startswith('.'):
        original_name = original_name[0] = '．'
    
    return original_name


def get_fullpath(file_name: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, file_name)
    return file_name