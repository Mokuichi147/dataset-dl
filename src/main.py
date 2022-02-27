from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, as_completed
import csv
import dearpygui.dearpygui as dpg
from os.path import isfile, isdir, join
import pyperclip
import sys
from tempfile import gettempdir
from traceback import print_exc

import core
import extruct
import utilio

from pytube import YouTube, Playlist
import ffmpeg

if sys.platform == 'darwin':
    from tkinter import Tk
    from tkinter.filedialog import askdirectory, askopenfilename
    
    save_dir_dialog_mac = False
    load_csv_dialog_mac = False
    tkinter_root = Tk()
    tkinter_root.withdraw()


dpg.create_context()

APPNAME = 'dataset-dl'
TEMPDIR = join(gettempdir(), APPNAME)
MAXWOREKR = 20

TAGS = []


def check_save_dir():
    dpg.set_value('save_dir_check', isdir(dpg.get_value('save_dir_path')))

if sys.platform == 'darwin':
    def save_dir_dialog():
        global save_dir_dialog_mac
        save_dir_dialog_mac = True
        
    def load_csv_dialog():
        global load_csv_dialog_mac
        load_csv_dialog_mac = True
else:
    def save_dir_dialog():
        save_dir = utilio.ask_directry()
        if save_dir != '':
            dpg.set_value('save_dir_path', save_dir)
        check_save_dir()
        
    def load_csv_dialog():
        load_csv = utilio.ask_open_file([('', '.csv')])
        if load_csv != '':
            dpg.set_value('csv_path', load_csv)
        check_csv_path()


def check_csv_path():
    csv_path = dpg.get_value('csv_path')
    dpg.set_value('csv_path_check', isfile(csv_path) and csv_path.lower().endswith('.csv'))


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
    parent_tag = 'url_tab'
    if not (dpg.get_value('save_dir_check') and dpg.get_value('url_check')):
        unlock_ui()
        return
    
    generate_entire_progress(parent_tag)
    input_url = dpg.get_value('url')
    if extruct.get_playlist_id(input_url) != '':
        video_urls = Playlist(input_url).video_urls
    else:
        video_urls = ['https://www.youtube.com/watch?v=' + extruct.get_video_id(input_url)]
    
    with ThreadPoolExecutor(max_workers=MAXWOREKR) as executor:
        tasks = [executor.submit(
                    download,
                    video_url,
                    core.NameMode.TITLE,
                    0,
                    0,
                    parent_tag
                ) for video_url in video_urls]
        complete_count = 0
        max_task_count = len(tasks)
        for task in as_completed(tasks):
            complete_count += 1
            dpg.set_value('entire_bar', complete_count / max_task_count)
            dpg.set_value('entire_text', f'Completed: {complete_count:>7} / {max_task_count}')
    dpg.delete_item('entire_group')
    unlock_ui()


def run_csv():
    lock_ui()
    parent_tag = 'csv_tab'
    if not (dpg.get_value('save_dir_check') and dpg.get_value('csv_path_check')):
        unlock_ui()
        return
    
    generate_entire_progress(parent_tag)
    with open(dpg.get_value('csv_path'), 'r', encoding='utf-8') as f,\
                 ThreadPoolExecutor(max_workers=MAXWOREKR) as executor:
        reader = csv.reader(f)
        tasks = []
        for row in reader:
            if row[0].startswith('#'):
                continue
            video_url = 'https://www.youtube.com/watch?v=' + row[0]
            tasks.append(executor.submit(
                    download,
                    video_url,
                    core.NameMode.ID,
                    int(float(row[1])),
                    int(float(row[2])),
                    parent_tag
                ))
        
        complete_count = 0
        max_task_count = len(tasks)
        for task in as_completed(tasks):
            complete_count += 1
            dpg.set_value('entire_bar', complete_count / max_task_count)
            dpg.set_value('entire_text', f'Completed: {complete_count:>7} / {max_task_count}')
    dpg.delete_item('entire_group')
    unlock_ui()


def generate_entire_progress(parent_tag: str):
    dpg.add_group(tag='entire_group', parent=parent_tag, horizontal=True)
    dpg.add_progress_bar(tag='entire_bar', parent='entire_group')
    dpg.add_text('Downloading...', tag=f'entire_text', parent=f'entire_group')


def set_progress(stream, chunk, bytes_remaining):
    stream_id = extruct.file_hash(f'{stream.title}_{stream.filesize}')
    dpg.set_value(stream_id, 1 - bytes_remaining / stream.filesize)


def download(video_url: str, naming: core.NameMode, start_time: int, end_time: int, parent_tag: str):
    yt = YouTube(video_url, on_progress_callback=set_progress)
    quality_mode = core.get_qualitymode(dpg.get_value('quality_radio'))
    
    stream_video = core.get_video_stream(yt, quality_mode)
    stream_audio = core.get_audio_stream(yt, quality_mode)
    
    if not quality_mode.is_audio:
        return
    stream_audio_id = extruct.file_hash(f'{stream_audio.title}_{stream_audio.filesize}')
    
    if not quality_mode.is_video:
        request_type = core.get_request_type(quality_mode.extension_audio)
        save_path = TEMPDIR if quality_mode == core.QualityMode.OPUS else dpg.get_value('save_dir_path')
        file_name = None    if quality_mode == core.QualityMode.OPUS else extruct.file_name(stream_audio.title)
        
        with ThreadPoolExecutor(max_workers=MAXWOREKR*2) as executor:
            tasks = []
            tasks.append(executor.submit(
                    download_stream,
                    stream_audio,
                    save_path,
                    request_type,
                    parent_tag,
                    filename = file_name
                ))
            for task in as_completed(tasks):
                pass
        dpg.delete_item(f'{stream_audio_id}_group')
        
        if quality_mode != core.QualityMode.OPUS:
            return
        
        if naming == core.NameMode.ID:
            audio_id = extruct.get_video_id(video_url)
            save_path = f"{join(dpg.get_value('save_dir_path'), extruct.file_name(audio_id))}.{quality_mode.extension_audio}"
        else:
            save_path = f"{join(dpg.get_value('save_dir_path'), extruct.file_name(stream_audio.title))}.{quality_mode.extension_audio}"
        
        audio_temp_path = f'{join(TEMPDIR, stream_audio_id)}'
        auodio_save(quality_mode, save_path, audio_temp_path, start_time, end_time)
    
    
    stream_video_id = extruct.file_hash(f'{stream_video.title}_{stream_video.filesize}')
    
    with ThreadPoolExecutor(max_workers=MAXWOREKR*2) as executor:
        tasks = []
        tasks.append(executor.submit(
                download_stream,
                stream_video,
                TEMPDIR,
                quality_mode.extension_video,
                parent_tag
            ))
        tasks.append(executor.submit(
                download_stream,
                stream_audio,
                TEMPDIR,
                quality_mode.extension_audio,
                parent_tag
            ))
        for task in as_completed(tasks):
            pass
    
    dpg.delete_item(f'{stream_video_id}_group')
    dpg.delete_item(f'{stream_audio_id}_group')
    
    if naming == core.NameMode.ID:
        stream_id = extruct.get_video_id(video_url)
        save_path = f"{join(dpg.get_value('save_dir_path'), extruct.file_name(stream_id))}.{quality_mode.extension_video}"
    else:
        save_path = f"{join(dpg.get_value('save_dir_path'), extruct.file_name(stream_video.title))}.{quality_mode.extension_video}"
    
    video_temp_path = f'{join(TEMPDIR, stream_video_id)}.{quality_mode.extension_video}'
    audio_temp_path = f'{join(TEMPDIR, stream_audio_id)}.{quality_mode.extension_audio}'
    marge_save(save_path, video_temp_path, audio_temp_path, start_time, end_time)


def auodio_save(quality_mode: core.QualityMode, save_path: str, audio_temp_path: str, start_time: int, end_time: int):
    try:
        if quality_mode == core.QualityMode.OPUS:
            opus_temp_path = f'{audio_temp_path}.{core.get_request_type(quality_mode.extension_audio)}'
            audio_temp_path = f'{audio_temp_path}.{quality_mode.extension_audio}'
            
            opus_audio = ffmpeg.input(opus_temp_path)
            opus_audio_stream = ffmpeg.output(opus_audio, audio_temp_path, acodec='copy').global_args('-loglevel', 'quiet')
            ffmpeg.run(opus_audio_stream, overwrite_output=True)
            utilio.delete_file(opus_temp_path)
        else:
            audio_temp_path = f'{audio_temp_path}.{quality_mode.extension_audio}'
        
        if start_time < end_time and not (start_time == 0 == end_time): 
            audio = ffmpeg.input(audio_temp_path, ss=start_time, to=end_time)
        else:
            audio = ffmpeg.input(audio_temp_path)
        
        audio_stream = ffmpeg.output(audio, save_path, acodec='copy').global_args('-loglevel', 'quiet')
        ffmpeg.run(audio_stream, overwrite_output=True)

        utilio.delete_file(audio_temp_path)
    except:
        print_exc()


def marge_save(save_path: str, video_temp_path: str, audio_temp_path: str,
               start_time: int, end_time: int):
    try:
        if start_time < end_time and not (start_time == 0 == end_time): 
            video = ffmpeg.input(video_temp_path, ss=start_time, to=end_time)
            audio = ffmpeg.input(audio_temp_path, ss=start_time, to=end_time)
        else:
            video = ffmpeg.input(video_temp_path)
            audio = ffmpeg.input(audio_temp_path)
        marge_stream = ffmpeg.output(video, audio, save_path, vcodec='copy', acodec='copy').global_args('-loglevel', 'quiet')
        ffmpeg.run(marge_stream, overwrite_output=True)
        
        utilio.delete_file(video_temp_path)
        utilio.delete_file(audio_temp_path)
    except:
        print_exc()


def download_stream(stream, output_path, extension, parent_tag, filename=None):
    stream_id = extruct.file_hash(f'{stream.title}_{stream.filesize}')
    if filename == None:
        filename = f'{stream_id}.{extension}'
    else:
        filename = f'{filename}.{extension}'
    dpg.add_group(tag=f'{stream_id}_group', parent=parent_tag, horizontal=True)
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
            dpg.add_input_text(default_value=font_license, multiline=True, readonly=True)
    
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
            
        with dpg.tab(label='CSV File', tag='csv_tab'):
            with dpg.group(horizontal=True):
                dpg.add_checkbox(default_value=False, enabled=False, tag='csv_path_check')
                dpg.add_input_text(callback=check_csv_path, tag='csv_path')
                dpg.add_button(label='Select', tag='csv_path_button', callback=load_csv_dialog)
                dpg.add_button(label='Run', tag='csv_run_button', callback=run_csv)
                TAGS.append('csv_path')
                TAGS.append('csv_path_button')
                TAGS.append('csv_run_button')



utilio.create_workdir(TEMPDIR)
icon = extruct.get_fullpath(join('resources', 'dataset-dl.ico')) if sys.platform == 'win32' else ''

dpg.create_viewport(title=APPNAME, width=1000, height=500, large_icon=icon)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Primary Window', True)

if not sys.platform == 'darwin':
    dpg.start_dearpygui()
else:
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        
        if save_dir_dialog_mac:
            save_dir = askdirectory()
            if save_dir != '':
                dpg.set_value('save_dir_path', save_dir)
            check_save_dir()
            save_dir_dialog_mac = False
            
        elif load_csv_dialog_mac:
            load_csv = askopenfilename(filetypes=[('', '.csv')])
            if load_csv != '':
                dpg.set_value('csv_path', load_csv)
            check_csv_path()
            load_csv_dialog_mac = False
    tkinter_root.destroy()

dpg.destroy_context()

utilio.delete_workdir(TEMPDIR)