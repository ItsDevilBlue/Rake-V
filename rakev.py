from tkinter import *
import os
from tkinter import filedialog
import pygame
from pygame import mixer
import customtkinter as ctk
from CTkListbox import *
import copy
import eyed3
import io
import json
import random
from PIL import Image, ImageTk, ImageDraw, ImageOps
from youtubesearchpython import VideosSearch
from threading import Thread
import yt_dlp
from playsound3 import playsound
import PIL
import pystray
import ctypes
from pathlib import Path
from CTkMessagebox import CTkMessagebox

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)
pygame.mixer.music.set_volume(0.5)

songs_playlist = None
current_song = None
seek_click = False
new_pos = 0
shuffled = False
selected_playlist = None
repeat = False
search_delay = None
playlists_main_path = None
original_playlists_order = None
current_song_index = None
sound_thread = None
playlists_order = None
last_volume = None
no_results = False
first_search = False
loading = False
playlists_order  = {}
artist = 'By JK'
title = 'Rake V'

rotation_speed = 0
target_speed = 6
max_speed = 6
deceleration_rate = 0.2
acceleration_rate = 0.5

def load_state():
    global playlists_main_path, shuffled, seek_click, songs_playlist, artist, title, current_song_index, current_song, playlists_order, original_playlists_order, shuffled, new_pos, repeat 
    try:
        def open_help_window(event):
            help_window = ctk.CTkToplevel(root)
            help_window.lift()
            help_window.title("How to use - Rake V")
            help_window.geometry("600x800")
            help_window.resizable(False, False)

            how_to_use = (
                    "🎵 Welcome to Rake V — Your Modern MP3 Player 🎧\n"
                    "──────────────────────────────────────────────\n\n"
                    "Built using Python, Tkinter, CustomTkinter,\n"
                    "and Pygame, Rake V delivers fast, clean, and\n"
                    "customizable music playback. Here’s how to begin:\n\n"
                        
                    "🗂 Importing Your Playlists\n"
                    "──────────────────────────────────────────────\n"
                    "1. Click the “Import Folder” button on the top bar.\n"
                    "2. Select your main music folder.\n"
                    "   - Each subfolder becomes a playlist.\n"
                    "   - Example: Music/Rap, Music/Chill, Music/Mixes\n"
                    "3. Your playlists appear on the left panel.\n"
                    "   - Click one to load its songs instantly.\n\n"
                            
                    "🎶 Playing Music\n"
                    "──────────────────────────────────────────────\n"
                    "1. Click a playlist to view its songs.\n"
                    "2. Click any song to start playing it immediately.\n"
                    "3. Album artwork and vinyl rotation appear in the center.\n"
                    "4. Vinyl animation slows or stops when paused.\n\n"
                            
                    "▶️ Playback Controls\n"
                    "──────────────────────────────────────────────\n"
                    "- Play/Pause: Click ▶/II or press Space\n"
                    "- Next Song: ▶|\n"
                    "- Previous Song: |◀\n"
                    "- Repeat Song: 🔁 toggles repeat mode\n"
                    "- Shuffle: 🔀 shuffles the current playlist\n"
                    "- Seek: Drag the progress bar under the album art\n\n"
                            
                    "🔊 Volume Controls\n"
                    "──────────────────────────────────────────────\n"
                    "- Use the volume slider (bottom right corner)\n"
                    "- Click 🔈/🔇 to mute or unmute instantly\n\n"
                            
                    "🔍 Global Search\n"
                    "──────────────────────────────────────────────\n"
                    "- Type in the search bar to search ALL playlists at once\n"
                    "- Search updates instantly as you type\n"
                    "- Press Enter to play the top result\n"
                    "- Click ❌ to clear search results\n\n"
                            
                    "⬇ YouTube Audio Download\n"
                    "──────────────────────────────────────────────\n"
                    "- Type a song name in the search bar\n"
                    "- Click “Download”\n"
                    "- Rake finds the best YouTube audio and saves it\n"
                    "- Downloaded songs are added directly to the selected playlist\n\n"
                        
                    "📂 Playlist Management\n"
                    "──────────────────────────────────────────────\n"
                    "✔ Playlists sync with your folder structure\n"
                    "✔ Right-click a playlist to rename or delete it\n"
                    "✔ New songs added to your folders appear automatically\n"
                    "✔ Reorder playlists by dragging\n\n"
                        
                    "💾 Auto-Saving / Resume\n"
                    "──────────────────────────────────────────────\n"
                    "- Rake automatically remembers:\n"
                    "  • Last played song\n"
                    "  • Playlist selection\n"
                    "  • Volume level\n"
                    "  • Repeat/Shuffle state\n"
                    "  • Queue order\n"
                        
                    "🎛 Additional Features\n"
                    "──────────────────────────────────────────────\n"
                    "✔ Smooth vinyl rotation effects\n"
                    "✔ Custom draggable top bar (no default Windows title bar)\n"
                    "✔ Fast load times even with large playlists\n"
                    "✔ Instant UI updates when files change\n\n"
                        
                    "💡 Tips\n"
                    "──────────────────────────────────────────────\n"
                    "- Playlist folders MUST contain .mp3 files\n"
                    "- Hover-based tooltips may be added soon\n"
                    "- Keep your folder names simple for best results\n\n"
                        
                    "──────────────────────────────────────────────\n"
                    "\"The moment I stop having fun with it,\n"
                    "I’ll be done with it.\" — Drake"
                )

            textbox = ctk.CTkTextbox(help_window, wrap="word", font=("Segoe UI", 12), corner_radius=10)
            textbox.pack(padx=10, pady=10, fill="both", expand=True)

            textbox.insert("0.0", how_to_use)
            textbox.configure(state='disabled')
            
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                state = json.load(f)
                playlists_main_path = state.get("playlists_main_path", None)
                playlists_order = state.get("playlists_order", None)
                original_playlists_order = state.get("original_playlists_order", None)
                current_song = state.get("current_song", None)
                current_song_index = state.get("current_song_index", None)
                songs_playlist = state.get("songs_playlist", None)
                selected_playlist = state.get("selected_playlist", None)
                volume = int(state.get("volume", None))
                shuffled = state.get("shuffled", None)
                    
                sync_playlists()
                if os.path.exists(playlists_main_path):
                    for playlist in os.listdir(playlists_main_path):
                        playlist_list.insert(END, playlist)
                    if songs_playlist:
                        playlist_list.activate(list(playlists_order.keys()).index(songs_playlist))
                    elif selected_playlist:
                        playlist_list.activate(list(playlists_order.keys()).index(selected_playlist))
                    load_playlist_songs(None)
                    if current_song:
                        current_song = None
                        pygame.mixer.music.set_volume(0)
                        play_song(None)
                        new_pos = int(state.get("new_pos", None))
                        pause_unpause(None)
                        seek_click = True
                        pygame.mixer.music.set_pos(new_pos)
                        seek_click = False
                volume_slider.set(volume)
                change_volume(None)

                if shuffled:
                    shuffle_btn.configure(text_color="#b70007")
        else:
            open_help_window(None)
                    
        help_btn.bind("<Button-1>", open_help_window)
            
    except Exception as e:
        msg = CTkMessagebox(title="Loading Error", message=e, icon="cancel")

def import_playlists(Event):
    global playlists_order, loading, angle, rotation_speed, playlists_main_path, original_playlists_order, seek_click, current_song, current_song_index, songs_playlist, selected_playlist
    try:
        if loading:
            return
        loading = True
        temp = filedialog.askdirectory(initialdir="", title="Select Playlists Folder") + '/' 
        if not temp.strip('/'):
            loading = False
            return
        playlists_main_path = temp
        search_bar.configure(state="normal")
        playlist_songs_list.delete("all")
        playlist_list.delete("all")
        playlists_order = {}
        songs_playlist = None
        current_song_index = None
        current_song = None
        selected_playlist = None
        song_title.configure(text='Rake V')
        artist_label.configure(text='By JK')
        song_length.configure(text='--:--')
        pygame.mixer.music.unload()
        seek_click = True
        rotation_speed = 0
        angle = 0
        new_pos = 0
        seek_slider.set(0)
        song_pos.configure(text='--:--')
        seek_click = False
        search_box.place_forget()
        play_btn.configure(text='II')
        update_cover_art("assets\\rakebanner.png")
        
        if search_bar.get():
            search_bar.delete(0, END)

        try:
            for playlist in os.listdir(playlists_main_path):
                songs = []
                path = Path(playlists_main_path + playlist)
                if path.is_dir():
                    songs =  [f for f in os.listdir(path) if f.lower().endswith('.mp3')]
                    playlist_list.insert(END, playlist)
                    playlists_order[playlist] = [songname[:-4] for songname in songs]

            original_playlists_order = copy.deepcopy(playlists_order)
        except:
            pass
        loading = False
    except Exception as e:
        msg = CTkMessagebox(title="Importing Error", message=e, icon="cancel")

def load_playlist_songs(Event):
    global selected_playlist, loading
    try:
        if loading:
            playlist_list.activate(list(playlists_order.keys()).index(selected_playlist))
            return
        if playlist_list.get() != selected_playlist and loading != True:
            loading = True
            selected_playlist = playlist_list.get()
            playlist_songs_list.delete(0, 'end')
            if selected_playlist:
                for i, song in  enumerate(playlists_order[selected_playlist]):
                    playlist_songs_list.insert(END, song)
                    if songs_playlist == selected_playlist and song == current_song:
                        playlist_songs_list.activate(i)
                        playlist_songs_list.see(i)
            loading = False
    except Exception as e:
        msg = CTkMessagebox(title="Loading Songs Error", message=e, icon="cancel")

def update_songs_playlist(Event):
    global songs_playlist
    try:
        if playlist_songs_list.size() > 0:
            songs_playlist = selected_playlist
            play_song(None)
    except Exception as e:
        msg = CTkMessagebox(title="Updating Songs Playlist Error", message=e, icon="cancel")

def play_song(Event):
    global current_song_index, current_song, songfile, new_pos, artist, title, loading
    try:
        if loading:
            playlist_songs_list.deactivate(playlist_songs_list.curselection())
            if songs_playlist == playlist_list.get():
                try:
                    playlist_songs_list.activate(current_song_index)
                except:
                    pass
            return
        if current_song == playlist_songs_list.get():
            return

        loading = True
        if songs_playlist == selected_playlist:
            current_song_index = playlist_songs_list.curselection()
            current_song = playlist_songs_list.get()
        else:
            print('g')
            current_song = playlists_order[songs_playlist][current_song_index]
        pygame.mixer.music.load(playlists_main_path + songs_playlist + '/' + current_song + '.mp3')
        pygame.mixer.music.play()
        search_bar.configure(state='normal')
        play_btn.configure(text='II')
        seek_slider.configure(state='normal')
        new_pos = 0
        songfile = eyed3.load(playlists_main_path + songs_playlist + '/' + current_song + '.mp3')
        seek_slider.configure(to=int(songfile.info.time_secs), number_of_steps=int(songfile.info.time_secs))
        m, s = divmod(int(songfile.info.time_secs), 60)
        song_length.configure(text=f'{m:02d}:{s:02d}')

        artist = songfile.tag.artist or 'Unknown'
        title = songfile.tag.title or current_song
        song_title.configure(text=title[:42] + ('...' if len(title) > 40 else ''))
        artist_label.configure(text=artist[:42] + ('...' if len(title) > 40 else ''))
        
        check_events(None)

        if songfile.tag.album != None:
            root.title(f'{artist} - {title} ({songfile.tag.album})')
        else:
            root.title(f'{artist} - {title}')
        if songfile and songfile.tag and songfile.tag.images:
            update_cover_art(songfile.tag.images[0].image_data)
        else:
            update_cover_art("assets\\rakebanner.png")
            
        loading = False
    except Exception as e:
        msg = CTkMessagebox(title="Playing Song Error", message=e, icon="cancel")

def rotate_vinyl():
    global rotation_speed, angle, original_image, rotated, vinyl_tk, vinyl_canvas
    try:
        if not pygame.mixer.music.get_busy():
            if rotation_speed > 0:
                rotation_speed = max(0, rotation_speed - deceleration_rate)
        else:
            if rotation_speed < target_speed:
                rotation_speed = min(target_speed, rotation_speed + acceleration_rate)
        if rotation_speed > 0:
            angle = (angle - rotation_speed) % 360
            rotated = original_img.rotate(angle, resample=Image.BICUBIC, expand=False)
            vinyl_tk = ImageTk.PhotoImage(rotated)
            vinyl_canvas.itemconfig(image_on_canvas, image=vinyl_tk)
            vinyl_canvas.image = vinyl_tk

    except Exception as e:
        msg = CTkMessagebox(title="Rotating Vinyl Error", message=e, icon="cancel")
    root.after(50,  rotate_vinyl)

def update_cover_art(songpath):
    global angle, image_on_canvas, original_img, vinyl_tk, songfile
    cover_canvas.delete("all")
    vinyl_canvas.delete("all")

    try:

        image_data = songpath
        if songpath == "assets\\rakebanner.png" or not songpath:
            image = Image.open(songpath).copy()
            img = Image.open("assets\\rakebanner.png").convert("RGBA").copy()
        else:
            image = Image.open(io.BytesIO(image_data)).copy()
            img = Image.open(io.BytesIO(image_data)).convert("RGBA").copy()
            
        image = image.resize((500, 223), Image.Resampling.LANCZOS)
        radius = 5
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        rounded_image = Image.new("RGBA", image.size)
        rounded_image.paste(image, (0, 0), mask=mask)
        tk_image = ImageTk.PhotoImage(rounded_image)
        cover_canvas.create_image(0, 0, anchor=NW, image=tk_image)
        cover_canvas.image = tk_image

        if songpath == "assets\\rakebanner.png" or not songpath:
            image = Image.open("assets\\rakelogo.png").copy()
            img = Image.open("assets\\rakelogo.png").convert("RGBA").copy()

        angle = 0
        img = ImageOps.fit(img, (50, 50), centering=(0.5, 0.5))
        mask = Image.new("L", (50, 50), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 49, 49), fill=255)
        circular_img = Image.new("RGBA", (50, 50))
        circular_img.paste(img, (0, 0), mask=mask)
        center = 50 // 2
        label_radius = 2.5
        
        if songpath != "assets\\rakebanner.png":
            draw_label = ImageDraw.Draw(circular_img)
            draw_label.ellipse((center - label_radius, center - label_radius, center + label_radius, center + label_radius), fill='#242424')

        original_img = circular_img
        vinyl_tk = ImageTk.PhotoImage(circular_img)
        image_on_canvas = vinyl_canvas.create_image(0, 0, anchor=NW, image=vinyl_tk)
        vinyl_canvas.image = vinyl_tk
    except Exception as e:
        msg = CTkMessagebox(title="Updating Art Error", message=e, icon="cancel")

def pause_unpause(Event):
    try:
        if str(root.focus_get()) == '.!ctkentry.!entry':
            return 
        if current_song:
            if pygame.mixer.music.get_busy():
                play_btn.configure(text='▶')
                root.title('Rake V')
                pygame.mixer.music.pause()
            else:
                play_btn.configure(text='II')
                root.title(f'{artist} - {title} ({songs_playlist})')
                pygame.mixer.music.unpause()
    except Exception as e:
        msg = CTkMessagebox(title="Pausing/Unpausing Error", message=e, icon="cancel")

def next_song(Event):
    global current_song_index, current_song, shuffled
    try:
        if loading:
            return
        
        if current_song:
            if current_song_index == len(playlists_order[songs_playlist]) - 1:
                if shuffled:
                    shuffled = False
                    shuffle(None)
                    next_song(None)
                else:
                    current_song_index = 0
            else:
                current_song_index += 1
            if songs_playlist == selected_playlist:
                playlist_songs_list.activate(current_song_index)
            current_song = None
            print('good')
            play_song(None)
    except Exception as e:
        msg = CTkMessagebox(title="Next Song Error", message=e, icon="cancel")

def prev_song(Event):
    global current_song_index, loading, current_song
    try:
        if loading:
            return
        
        if current_song:
            if int(seek_slider.get()) >= 3:
                current_song = None
                play_song(None)
                return
            if current_song_index == 0:
                current_song_index = len(playlists_order[songs_playlist]) - 1
            else:
                current_song_index -= 1
            if songs_playlist == selected_playlist:
                playlist_songs_list.activate(current_song_index)
            play_song(None)
        loading = False
    except Exception as e:
        msg = CTkMessagebox(title="Previous Song Error", message=e, icon="cancel")

def shuffle(Event):
    global shuffled, playlists_order, loading, current_song_index, selected_playlist
    try:
        if loading or not playlists_order:
            return
        loading = True
        if not shuffled:
            shuffled = True
            shuffle_btn.configure(text_color='#b70007')
            for playlist in playlists_order:
                random.shuffle(playlists_order[playlist])
            if playlist_songs_list.size() <= 1:
                loading = False
                return
            if current_song:
                playlists_order[songs_playlist].remove(current_song)
                playlists_order[songs_playlist].insert(0, current_song)
            current_song_index = 0
            selected_playlist = None
            loading = False
            selected_playlist = None
            load_playlist_songs(None)
        else:
            shuffled = False
            shuffle_btn.configure(text_color='gray80')
            playlists_order = copy.deepcopy(original_playlists_order)
            if current_song:
                current_song_index = playlists_order[songs_playlist].index(current_song)
            selected_playlist = None
            loading = False
            load_playlist_songs(None)
    except Exception as e:
        msg = CTkMessagebox(title="Shuffling Error", message=e, icon="cancel")

def repeat_song(Event):
    global repeat
    try:
        if playlist_songs_list.size() == 0:
            return
        if repeat == False:
            repeat = True
            repeat_btn.configure(text_color='#b70007')
        else:
            repeat = False
            repeat_btn.configure(text_color='gray80')
    except Exception as e:
        msg = CTkMessagebox(title="Repeating Song Error", message=e, icon="cancel")

def change_volume(Event):
    try:
        if volume_slider.get() == 0:
            mute_btn.configure(text='🔇', text_color='red')
        elif volume_slider.get() <= 20:
            mute_btn.configure(text='🔈', text_color='gray80')
        elif volume_slider.get() <= 21:
            mute_btn.configure(text='🔉', text_color='gray80')
        elif volume_slider.get() > 51:
            mute_btn.configure(text='🔊', text_color='gray80')
        pygame.mixer.music.set_volume(volume_slider.get()/100)
    except Exception as e:
        msg = CTkMessagebox(title="Volume Error Error", message=e, icon="cancel")
    
def mute(Event):
    global last_volume
    try:
        if last_volume and volume_slider.get() == 0:
            volume_slider.set(last_volume)
            change_volume(None)
            return
        last_volume = volume_slider.get()
        volume_slider.set(0)
        change_volume(None)
    except Exception as e:
        msg = CTkMessagebox(title="Muting Error", message=e, icon="cancel")

def sync_playlists():
    global playlists_order, original_playlists_order, selected_playlist, current_song_index
    try:
        if original_playlists_order:
            updated_playlists_order = {}
            for playlist in os.listdir(playlists_main_path):
                path = Path(playlists_main_path + '/' + playlist)
                if path.is_dir():
                    songs = [f for f in os.listdir(playlists_main_path + playlist) if f.lower().endswith('.mp3')]
                    updated_playlists_order[playlist] = [songname[:-4] for songname in songs]        
            if updated_playlists_order != original_playlists_order:
                removed_playlists = [p for p in playlists_order if p not in updated_playlists_order]
                added_playlists = [p for p in updated_playlists_order if p not in playlists_order]
                
                for p in removed_playlists:
                    if p == selected_playlist:
                        playlist_songs_list.delete("all")
                        playlist_list.deactivate(playlist_list.curselection())
                        selected_playlist = None
                    playlist_list.delete(list(playlists_order.keys()).index(p))
                    playlists_order.pop(p, None)
                    original_playlists_order.pop(p, None)

                for p in added_playlists:
                    if not shuffled:
                        playlists_order[p] = updated_playlists_order[p]
                    else:
                        playlists_order[p] = updated_playlists_order[p]
                        random.shuffle(playlists_order[p])
                    original_playlists_order[p] = updated_playlists_order[p]
                    playlist_list.insert(END, p)


                for p, songs in updated_playlists_order.items():
                    old_songs = playlists_order[p]
                    true_songs = original_playlists_order.get(p, old_songs)

                    added_songs = [s for s in songs if s not in true_songs]
                    removed_songs = [s for s in true_songs if s not in songs]

                    original_playlists_order[p] = songs

                    if original_playlists_order:
                        for song in removed_songs:
                            if p == selected_playlist:
                                playlists_order[p].remove(song)
                            else:
                                playlists_order[p] = songs
                        for song in added_songs:
                            if current_song and p == songs_playlist:
                                playlists_order[p].insert(current_song_index + 1, song)
                            else:
                                playlists_order[p] = songs
                         
                    if p == selected_playlist and removed_songs or p == selected_playlist and added_songs:
                        selected_playlist = None
                        load_playlist_songs(None)
    except Exception as e:
        msg = CTkMessagebox(title="Auto Sync Error", message=e, icon="cancel")
                            

def check_events(event=None):
    global original_playlists_order, playlists_order, current_song, selected_playlist, selected_playlist_changed
    try:
        for event in pygame.event.get():
            if event.type == SONG_END:
                if repeat == True:
                    current_song = None
                    play_song(None)
                else:
                    next_song(None)
        
        if current_song:
            if seek_click == False:
                seek_slider.set(pygame.mixer.music.get_pos()/1000+new_pos)
                m, s = divmod(int(seek_slider.get()), 60)
                song_pos.configure(text=f'{m:02d}:{s:02d}')
            else:
                m, s = divmod(int(seek_slider.get()), 60)
                song_pos.configure(text=f'{m:02d}:{s:02d}')
        else:
            song_pos.configure(text='--:--')

        sync_playlists()
    except Exception as e:
        msg = CTkMessagebox(title="Checking for Events Error", message=e, icon="cancel")
    root.after(200, check_events)

def seek_clicked(Event):
    global seek_click
    seek_click = True

def seek_released(Event):
    global seek_click, new_pos
    try:
        new_pos =  seek_slider.get()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.play(start=new_pos)
        else:
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.play(start=new_pos)
            pygame.mixer.music.pause()
            change_volume(None)

        seek_click = False
    except Exception as e:
        msg = CTkMessagebox(title="Seek Error", message=e, icon="cancel")

def animate_search_bar(target_x, target_width, duration=100):
    try:
        steps = 50
        delay = duration // steps

        current_x = search_bar.winfo_x()
        current_width = search_bar.cget("width")

        delta_x = (target_x - current_x) / steps
        delta_w = (target_width - current_width) / steps

        def step(i=0):
            nonlocal current_x, current_width
            if i >= steps:
                search_bar.place(x=target_x, y=5)
                search_bar.configure(width=target_width)

                if target_width == 300:
                    update_search_results()
                
                return

            current_x += delta_x
            current_width += delta_w

            search_bar.place(x=int(current_x), y=5)
            search_bar.configure(width=int(current_width))

            root.after(delay, lambda: step(i + 1))
        step()
    except Exception as e:
        msg = CTkMessagebox(title="Animating Search Bar Error", message=e, icon="cancel")

def search_bar_delay(Event):
    global search_delay
    try:
        if search_delay:
            root.after_cancel(search_delay)
        search_delay = root.after(200, update_search_results)
    except Exception as e:
        msg = CTkMessagebox(title="Search Bar Delay Error", message=e, icon="cancel")

def update_search_results():
    global no_results
    try:
        no_results = False

        search_query = search_bar.get().lower()
        if not search_query.strip(' '):
            search_box.place_forget()
            search_box.delete("all")
            return

        search_box.place_forget()
        search_box.delete("all")
        
        search_matches = []
        print(playlist_list.size())
        if not playlists_order:
            search_box.insert(0, 'No Results Found!')
            search_box.insert(1, 'Download from YouTube')
        else:  
            for songs in original_playlists_order.values():
                for song in songs:
                    if search_query in song.lower():
                        search_matches.append(song)
            if len(search_matches) == 0:
                search_box.insert(0, 'No Results Found!')
                search_box.insert(1, 'Download from YouTube')
                no_results = True
            else:
                for song in search_matches:
                    search_box.insert(END, song)
                
        search_box.place(x=285, y=35)
        search_box.update_idletasks()
    except Exception as e:
        pass
        #msg = CTkMessagebox(title="Updating Search Results Error", message=e, icon="cancel")

def play_search_box(Event):
    global songs_playlist, current_song_index, current_song, no_results
    try:
        root.focus_set()
        searched_song = search_box.get()
        if no_results:
            if searched_song == 'Download from YouTube':
                start_thread(None)
            search_box.place_forget()
            return
        search_bar.delete(0, END)
        clear_focus(None)
        current_song = None
        search_box.place_forget()
        animate_search_bar(310, 250)
        for playlist, songs in playlists_order.items():
            for song in songs:
                if song == searched_song:
                    songs_playlist = playlist
                    current_song_index = playlists_order[playlist].index(searched_song)
                    if selected_playlist == playlist:
                        playlist_songs_list.activate(current_song_index)
                        playlist_songs_list.see(current_song_index)
                        play_song(None)
                    else:
                        playlist_list.activate(list(playlists_order).index(playlist))
                        load_playlist_songs(None)
                        playlist_songs_list.activate(current_song_index)
                        playlist_songs_list.see(current_song_index)
                        play_song(None)
                    return
    except Exception as e:
        msg = CTkMessagebox(title="Playing Search Box Error", message=e, icon="cancel")

def clear_focus(event=None):
    try:
        if event and getattr(event, "widget", None):
            widget_name = str(event.widget)
            if str(search_bar) not in widget_name and '.!ctkframe5.!canvas' not in str(event.widget) and '.!ctkframe5.!ctkscrollbar' not in str(event.widget):
                    root.focus_set()
                    search_box.place_forget()
            
    except Exception as e:
        msg = CTkMessagebox(title="Clearing Focus Error", message=e, icon="cancel")

def download():
    global playlists_order, original_playlists_order, selected_playlist, download_to

    download_to = selected_playlist
    if not selected_playlist:
        msg = CTkMessagebox(title="No Playlist Selected", message="Select a Playlist to Download to!", icon="warning")
        return
    videos_search = VideosSearch(search_bar.get(), limit=1)
    url = videos_search.result()['result'][0]['link']
    
    search_bar.delete(0, END)
    search_bar.insert(0, "Downloading...")
    search_bar.configure(state="disabled")

    final_folder = os.path.join(playlists_main_path, selected_playlist)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': final_folder + r'\%(title)s.%(ext)s',
        'noplaylist': True,
        'ffmpeg_location': "C:\\Users\\Jayden\\Desktop\\Rake V\\ffmpeg-2025-10-30-git-00c23bafb0-full_build\\ffmpeg-2025-10-30-git-00c23bafb0-full_build\\bin\\ffmpeg.exe",
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'writethumbnail': True,
        'addmetadata': True,
        'quiet': True,
        'no_warnings': True,
}


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        ydl.download([url])
        yt_title = info.get("title")
    search_bar.configure(state='normal')
    search_bar.delete(0, END)

def start_thread(event):
    print('a')
    t = Thread(target=download)
    t.daemon = True
    t.start()

def unload(event):
    global seek_click, selected_playlist, rotation_speed, songs_playlist, artist, title, current_song, current_song_index
    try:
        print("good")
        playlist_songs_list.delete("all")
        if selected_playlist:
            playlist_list.deactivate(playlist_list.curselection())
        selected_playlist = None
        current_song = None
        current_song_index = None
        songs_playlist = None
        artist = None
        title = None
        song_title.configure(text='Rake V')
        artist_label.configure(text='By Jk')
        seek_click = True
        new_pos = 0
        seek_slider.set(0)
        seek_click = False
        song_length.configure(text='--:--')
        play_btn.configure(text='II')
        pygame.mixer.music.unload()
        angle = 0
        rotation_speed = 0
        update_cover_art("assets\\rakebanner.png")
    except Exception as e:
        msg = CTkMessagebox(title="Unloading Error", message=e, icon="cancel")

def animate_click(event):
    global widget
    try:
        widget = event.widget
        widget = widget.master
        widget.place(x=widget.winfo_x(), y=widget.winfo_y()+2)
    except Exception as e:
        msg = CTkMessagebox(title="Animating Click Error", message=e, icon="cancel")

def animate_release(event):
    try:
        widget.place(x=widget.winfo_x(), y=widget.winfo_y()-2)
    except Exception as e:
        msg = CTkMessagebox(title="Animating Release Error", message=e, icon="cancel")

def click_sound(event):
    try:
        sound_thread = playsound('assets\\click.mp3', block=False)
    except Exception as e:
        msg = CTkMessagebox(title="Type Sound Error", message=e, icon="cancel")

def startup_sound(event):
    try:
        if not pygame.mixer.music.get_busy():
            sound_thread = playsound('assets\\startup.wav', block=False)
    except Exception as e:
        msg = CTkMessagebox(title="Startup Sound Error", message=e, icon="cancel")


def minimize_window(event):
    try:
        ctypes.windll.user32.ShowWindow(hwnd, 11)
    except:
        msg = CTkMessagebox(title="Minmizing Window Error", message=e, icon="cancel")
    
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_move(event):
    try:
        x = root.winfo_pointerx() - root.x
        y = root.winfo_pointery() - root.y
        root.geometry(f"+{x}+{y}")
    except:
        msg = CTkMessagebox(title="Title Bar Moving Error", message=e, icon="cancel")

def see_current_song(event=None):
    try:
        if current_song:
            playlist_list.activate(list(playlists_order.keys()).index(songs_playlist))
            selected_playlist = None
            load_playlist_songs(None)
            playlist_songs_list.see(current_song_index)
    except:
        msg = CTkMessagebox(title="Seeing Current Song Error", message=e, icon="cancel")

def focus_search_bar(event):
    search_bar.focus_set()

def close_window(event):
    try:
        pygame.mixer.music.stop()
        save_state(None)
        root.destroy()
    except:
        msg = CTkMessagebox(title="Closing Window Error", message=e, icon="cancel")

def restart_song(event):
    global current_song
    try:
        if songs_playlist == selected_playlist:
            current_song = None
            play_song(None)
    except:
        msg = CTkMessagebox(title="Restarting Song Error", message=e, icon="cancel")


button_background = '#111111'
top_bar_color = '#111111'

root = ctk.CTk()
root.overrideredirect(True)
root.attributes("-alpha", 0)
root.title("Rake V")
root.geometry("865x340")
root.resizable(0, 0)
root.iconbitmap("assets\\rakelogo.ico")

hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
style = style & ~WS_EX_TOOLWINDOW
style = style | WS_EX_APPWINDOW
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)
SW_MINIMIZE = 6

playlist_list = CTkListbox(root, corner_radius=3, fg_color=button_background, border_color=button_background, height=212, hover_color='#383838', highlight_color='#b70007')
playlist_list.place(x=5, y=38)
playlist_list.bind("<Button-1>", load_playlist_songs, add='+')

playlist_songs_list = CTkListbox(root, height=212, corner_radius=3, fg_color=button_background, border_color=button_background, hover_color='#383838', highlight_color='#b70007')
playlist_songs_list.place(x=687, y=38)
playlist_songs_list.bind("<Button-1>", update_songs_playlist, add='+')
playlist_songs_list.bind("<Double-Button-1>", restart_song)

buttom_bar = ctk.CTkFrame(root, fg_color=button_background, height=78, width=866)
buttom_bar.place(x=0, y=264)

top_bar = ctk.CTkFrame(root, fg_color=top_bar_color, width=866, height=36, corner_radius=0)
top_bar.place(x=0, y=0)
top_bar.bind("<Button-1>", start_move)
top_bar.bind("<ButtonRelease-1>", stop_move)
top_bar.bind("<B1-Motion>", on_move)
top_bar.lower()

logo_canvas = ctk.CTkCanvas(top_bar, cursor='hand2', width=30, height=30, bg='black', highlightthickness=0)
logo_canvas.place(x=5, y=3)
logo_canvas.bind("<Button-1>", unload)

logo_image = Image.open("assets\\rakelogo.png").convert("RGBA").copy()
resized_logo_img = logo_image.resize((30, 30), Image.Resampling.LANCZOS)
logo_img = ImageTk.PhotoImage(resized_logo_img)
logo_canvas.create_image(0, 0, anchor=NW, image=logo_img)
logo_canvas.image = logo_img

close_btn = ctk.CTkLabel(top_bar, text='✕')
close_btn.place(x=840, y=5)

min_btn = ctk.CTkLabel(top_bar, text="–")
min_btn.place(x=800, y=5)

help_btn = ctk.CTkLabel(top_bar, text='❓')
help_btn.place(x=755, y=5)

import_btn = ctk.CTkLabel(root, text='+', bg_color=top_bar_color, cursor='hand2', font=("Poppins", 25))
import_btn.place(x=183, y=5)
root.bind("<Control-plus>", import_playlists, add='+')

play_btn = ctk.CTkLabel(root, text='II', bg_color=button_background, fg_color=button_background, cursor='hand2', font=("Poppins", 35))
play_btn.place(x=433, y=274)
root.bind("<space>", pause_unpause, add='+')

next_btn = ctk.CTkLabel(root, text='▶|', bg_color=button_background, fg_color=button_background, cursor='hand2', font=("Poppins", 35), text_color='gray80')
next_btn.place(x=480, y=274)
root.bind("<Control-Right>", next_song, add='+')

prev_btn = ctk.CTkLabel(root, text='|◀', bg_color=button_background, fg_color=button_background, cursor='hand2', font=("Poppins", 35), text_color='gray80')
prev_btn.place(x=375, y=274)  
root.bind("<Control-Left>", prev_song, add='+')

shuffle_btn = ctk.CTkLabel(root, text='🔀', bg_color=button_background, fg_color=button_background, cursor='hand2', font=("Poppins", 35), text_color='gray80')
shuffle_btn.place(x=321, y=273)
root.bind("<Control-s>", shuffle, add='+')

repeat_btn = ctk.CTkLabel(root, cursor='hand2', bg_color=button_background, fg_color=button_background, text='🔁', font=("Poppins", 35), text_color='gray80')
repeat_btn.place(x=524, y=273)
root.bind("<Control-r>", repeat_song, add='+')

volume_slider = ctk.CTkSlider(root, button_color='white', button_hover_color='gray60', bg_color=button_background, from_=0, to=100, width=150, command=change_volume)
volume_slider.place(x=707,  y=293)
volume_slider.set(50)

mute_btn = ctk.CTkLabel(root, text='🔉', bg_color=button_background, text_color='gray80', fg_color=button_background, font=("Segoe UI", 20), cursor="hand2")
mute_btn.place(x=680, y=285)
root.bind("<Control-m>", mute, add='+')

seek_slider = ctk.CTkSlider(root, width=400, corner_radius=5, button_color='white', bg_color=button_background, button_hover_color='gray80')
seek_slider.place(x=233, y=318)
seek_slider.set(0)
seek_slider.bind("<Button-1>", seek_clicked, add='+')
seek_slider.bind("<ButtonRelease-1>", seek_released, add='+')
seek_slider.configure(state='disabled')

cover_canvas = ctk.CTkCanvas(root, background=button_background, highlightthickness=0, width=500, height=223, bg='#242424')
cover_canvas.place(x=183, y=39)

vinyl_canvas = ctk.CTkCanvas(root, cursor='hand2', background=button_background, width=50, height=50, highlightthickness=0)
vinyl_canvas.place(x=8, y=275)
vinyl_canvas.bind("<Button-1>", see_current_song)

song_length = ctk.CTkLabel(root, bg_color=button_background, fg_color=button_background, text='--:--')
song_length.place(x=637, y=312)

song_pos = ctk.CTkLabel(root, corner_radius=0, bg_color=button_background, fg_color=button_background, text='--:--')
song_pos.place(x=198, y=312)

song_title = ctk.CTkLabel(root, cursor='hand2', bg_color=button_background, fg_color=button_background, text=title, height=1, font=("Poppins", 12, "bold"))
song_title.place(x=63, y=283)
song_title.bind("<Button-1>", see_current_song)

artist_label = ctk.CTkLabel(root, bg_color=button_background, fg_color=button_background, text=artist, height=1, font=("Poppins", 12), text_color='#AAAAAA')
artist_label.place(x=63, y=302)

search_bar = ctk.CTkEntry(root, font=("Poppins", 12), corner_radius=20, bg_color=top_bar_color, border_color='#242424', width=250, placeholder_text='Search...')
search_bar.place(x=310, y=5)
search_bar.bind("<KeyRelease>", click_sound, add='+')
search_bar.bind("<KeyRelease>", search_bar_delay, add='+')
search_bar.bind("<FocusIn>", lambda e=None: animate_search_bar(285, 300), add='+')
search_bar.bind("<FocusOut>", lambda e=None: animate_search_bar(310, 250), add='+')
root.bind("<Control-f>", focus_search_bar)

search_box = CTkListbox(root, width=272, border_color=button_background, fg_color=button_background, corner_radius=0, hover_color='#383838', highlight_color='#FF7400', command=play_search_box)
search_box.place(x=285, y=35)
search_box.place_forget()

update_cover_art("assets\\rakebanner.png")
load_state()

buttons = [play_btn, next_btn, close_btn, min_btn, import_btn, prev_btn, shuffle_btn, repeat_btn, mute_btn]
for btn in buttons:
    btn.bind("<Button-1>", animate_click, add='+')
    btn.bind("<ButtonRelease-1>", animate_release, add='+')
shuffle_btn.bind("<ButtonRelease-1>", shuffle, add='+')
next_btn.bind("<ButtonRelease-1>", next_song, add='+')
play_btn.bind("<ButtonRelease-1>", pause_unpause, add='+')
mute_btn.bind("<ButtonRelease-1>", mute, add='+')
repeat_btn.bind("<ButtonRelease-1>", repeat_song, add='+')
prev_btn.bind("<ButtonRelease-1>", prev_song, add='+')
import_btn.bind("<ButtonRelease-1>", import_playlists)
close_btn.bind("<Button-1>", close_window)
min_btn.bind("<Button-1>", minimize_window)

def save_state(Event):
    try:
        state = {
            "playlists_main_path": playlists_main_path,
            "songs_playlist": songs_playlist,
            "current_song": current_song,
            "current_song_index": current_song_index,
            "new_pos": int(seek_slider.get()),
            "playlists_order": playlists_order,
            "original_playlists_order": original_playlists_order,
            "shuffled": shuffled,
            "repeat": repeat,
            "volume": int(volume_slider.get()),
            "artist": artist,
            "title": title,
            "selected_playlist": selected_playlist
        }
        with open("config.json", "w") as f:
            json.dump(state, f)
    except Exception as e:
        msg = CTkMessagebox(title="Saving Error", message=e, icon="cancel")

startup_sound(None)
check_events(None)
rotate_vinyl()
root.bind("<Button-1>", clear_focus)
root.protocol("WM_DELETE_WINDOW", lambda: close_window)

root.update_idletasks()
root.after(0, lambda: root.attributes("-alpha", 1))

root.mainloop()
