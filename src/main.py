from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, as_completed
import dearpygui.dearpygui as dpg
from os.path import isfile, isdir, join
import pyperclip
from tempfile import gettempdir
from traceback import print_exc

import core
import extruct
import utilio

from pytube import YouTube, Playlist
import ffmpeg


dpg.create_context()

APPNAME = 'dataset-dl'
TEMPDIR = join(gettempdir(), APPNAME)
MAXWOREKR = 20

TAGS = []


def check_save_dir():
    dpg.set_value('save_dir_check', isdir(dpg.get_value('save_dir_path')))


def save_dir_dialog():
    save_dir = utilio.ask_directry()
    if save_dir != '':
        dpg.set_value('save_dir_path', save_dir)
    
    check_save_dir()


def check_csv_path():
    csv_path = dpg.get_value('csv_path')
    dpg.set_value('csv_path_check', isfile(csv_path) and csv_path.lower().endswith('.csv'))


def load_csv_dialog():
    load_csv = utilio.ask_open_file([('', '.csv')])
    if load_csv != '':
        dpg.set_value('csv_path', load_csv)
    
    check_csv_path()


def check_url():
    url_str = dpg.get_value('url')
    is_url = extruct.get_video_id(url_str) != '' or extruct.get_playlist_id(url_str) != ''
    dpg.set_value('url_check', is_url)


def paste_url():
    dpg.set_value('url', pyperclip.paste())
    check_url()


def lock_ui():
    for tag in TAGS:
        dpg.configure_item(tag, enabled=False)

def unlock_ui():
    for tag in TAGS:
        dpg.configure_item(tag, enabled=True)


def run_url():
    lock_ui()
    if not (dpg.get_value('save_dir_check') and dpg.get_value('url_check')):
        unlock_ui()
        return
    
    input_url = dpg.get_value('url')
    if extruct.get_playlist_id(input_url) != '':
        video_urls = Playlist(input_url).video_urls
    else:
        video_urls = ['https://www.youtube.com/watch?v=' + extruct.get_video_id(input_url)]
    
    with ThreadPoolExecutor(max_workers=MAXWOREKR) as executor:
        tasks = [executor.submit(download, video_url) for video_url in video_urls]
        for task in as_completed(tasks):
            pass
    unlock_ui()


def set_progress(stream, chunk, bytes_remaining):
    stream_id = extruct.file_hash(f'{stream.title}_{stream.filesize}')
    dpg.set_value(stream_id, 1 - bytes_remaining / stream.filesize)


def download(video_url):
    yt = YouTube(video_url, on_progress_callback=set_progress)
    quality_mode = core.get_qualitymode(dpg.get_value('quality_radio'))
    
    stream_video = core.get_video_stream(yt, quality_mode)
    stream_audio = core.get_audio_stream(yt, quality_mode)
    
    if not quality_mode.is_audio:
        return
    stream_audio_id = extruct.file_hash(f'{stream_audio.title}_{stream_audio.filesize}')
    
    if not quality_mode.is_video:
        with ThreadPoolExecutor(max_workers=MAXWOREKR*2) as executor:
            tasks = []
            tasks.append(executor.submit(
                    download_stream,
                    stream_audio,
                    dpg.get_value('save_dir_path'),
                    quality_mode.extension_audio,
                    filename = extruct.file_name(stream_audio.title)
                ))
            for task in as_completed(tasks):
                pass
            dpg.delete_item(f'{stream_audio_id}_group')
            return
    
    stream_video_id = extruct.file_hash(f'{stream_video.title}_{stream_video.filesize}')
    
    with ThreadPoolExecutor(max_workers=MAXWOREKR*2) as executor:
        tasks = []
        tasks.append(executor.submit(
                download_stream,
                stream_video,
                TEMPDIR,
                quality_mode.extension_video
            ))
        tasks.append(executor.submit(
                download_stream,
                stream_audio,
                TEMPDIR,
                quality_mode.extension_audio
            ))
        for task in as_completed(tasks):
            pass
    
    dpg.delete_item(f'{stream_video_id}_group')
    dpg.delete_item(f'{stream_audio_id}_group')
    
    video_temp_path = f'{join(TEMPDIR, stream_video_id)}.{quality_mode.extension_video}'
    audio_temp_path = f'{join(TEMPDIR, stream_audio_id)}.{quality_mode.extension_audio}'
    try:
        video = ffmpeg.input(video_temp_path)
        audio = ffmpeg.input(audio_temp_path)
        save_path = f"{join(dpg.get_value('save_dir_path'), extruct.file_name(stream_video.title))}.{quality_mode.extension_video}"
        marge_stream = ffmpeg.output(video, audio, save_path, vcodec='copy', acodec='copy').global_args('-loglevel', 'quiet')
        ffmpeg.run(marge_stream, overwrite_output=True)
        
        utilio.delete_file(video_temp_path)
        utilio.delete_file(audio_temp_path)
    except:
        print_exc()


def download_stream(stream, output_path, extension, filename=None):
    stream_id = extruct.file_hash(f'{stream.title}_{stream.filesize}')
    if filename == None:
        filename = f'{stream_id}.{extension}'
    else:
        filename = f'{filename}.{extension}'
    dpg.add_group(tag=f'{stream_id}_group', parent='url_tab', horizontal=True)
    dpg.add_progress_bar(tag=stream_id, parent=f'{stream_id}_group')
    dpg.add_text(stream.title, tag=f'{stream_id}_text', parent=f'{stream_id}_group')
    try:
        stream.download(output_path=output_path, filename=filename)
    except:
        print_exc()



with dpg.font_registry():
    with dpg.font(extruct.get_fullpath(join('resources', 'fonts', 'NotoSansJP-Regular.otf')), 22) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

with open(extruct.get_fullpath(join('resources', 'fonts', 'OFL.txt')), 'r', encoding='utf-8') as f:
    font_license = f.read()

with dpg.window(tag='Primary Window'):
    dpg.bind_font(default_font)
    with dpg.menu_bar():
        with dpg.menu(label='License'):
            dpg.add_text('NotoSansJP-Regular')
            dpg.add_input_text(default_value=font_license,
                               multiline=True,
                               readonly=True)
    
    dpg.add_text('Save Directory')
    with dpg.group(horizontal=True):
        dpg.add_checkbox(default_value=False, enabled=False, tag='save_dir_check')
        dpg.add_input_text(callback=check_save_dir, tag='save_dir_path')
        dpg.add_button(label='Select', tag='save_dir_button', callback=save_dir_dialog)
        TAGS.append('save_dir_path')
        TAGS.append('save_dir_button')
    dpg.add_spacer(height=10)
    
    dpg.add_text('Quality')
    dpg.add_radio_button(
        [quality_mode.text for quality_mode in core.QualityMode],
        tag = 'quality_radio',
        default_value = core.QualityMode.HIGH.text,
        horizontal = True
        )
    TAGS.append('quality_radio')
    dpg.add_spacer(height=10)
    
    dpg.add_text('Mode')
    with dpg.tab_bar():
        with dpg.tab(label='Video OR Playlist URL', tag='url_tab'):
            with dpg.group(horizontal=True):
                dpg.add_checkbox(default_value=False, enabled=False, tag='url_check')
                dpg.add_input_text(callback=check_url, tag='url')
                dpg.add_button(label='Paste', tag='url_paste_button', callback=paste_url)
                dpg.add_button(label='Run', tag='url_run_button', callback=run_url)
                TAGS.append('url')
                TAGS.append('url_paste_button')
                TAGS.append('url_run_button')
            
        with dpg.tab(label='CSV File'):
            with dpg.group(horizontal=True):
                dpg.add_checkbox(default_value=False, enabled=False, tag='csv_path_check')
                dpg.add_input_text(callback=check_csv_path, tag='csv_path')
                dpg.add_button(label='Select', tag='csv_path_button', callback=load_csv_dialog)
                TAGS.append('csv_path')
                TAGS.append('csv_path_button')



utilio.create_workdir(TEMPDIR)

dpg.create_viewport(title=APPNAME, width=800, height=500, large_icon=extruct.get_fullpath(join('resources', 'dataset-dl.ico')))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Primary Window', True)
dpg.start_dearpygui()
dpg.destroy_context()

utilio.delete_workdir(TEMPDIR)