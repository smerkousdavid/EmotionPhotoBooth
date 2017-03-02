from __future__ import print_function
from PIL import Image
from PIL import ImageTk
from printer import Printer
import ImageFont
import ImageDraw
import ttk
import Tkinter as tki
import threading
import datetime
import imutils
import cv2
import os

class GameSelectGUI(object):
    def __init__(self, config, select_game):
        self._config = config
        self._select_game = select_game

        self._root = tki.Toplevel()
        self._style = ttk.Style()
        self._style.theme_use(self._config.window_theme)

        self._spacer = ttk.Label(self._root, text="", background=self._config.background_color, foreground=self._config.background_color)
        self._spacer.pack(pady=25)

        oop_button = ttk.Button(self._root, text="Objective Programming and Networking", command= lambda: self._game_selected("objectoriented"))
        oop_button.pack(padx=100)

 
        eco_button = ttk.Button(self._root, text="Economy After WW2", command= lambda: self._game_selected("economyww2"))
        eco_button.pack(padx=100)       

        ww2_button = ttk.Button(self._root, text="Women In WW2", command= lambda: self._game_selected("womenww2"))
        ww2_button.pack(padx=100)
        '''
        for game_name, game in self._config.get_games():
            temp_game_name = str(game_name)
            temp_button = ttk.Button(self._root, text=game['title'], command= lambda: self._game_selected(temp_game_name))
            temp_button.pack(padx=100)
            print("Loading game: %s" % game_name)
        '''

        self._quit_button = ttk.Button(self._root, text="Quit", command=self._root.destroy)
        self._quit_button.pack(pady=50)

        self._root.wm_title(self._config.window_title)
        self._root.wm_protocol("WM_DELETE_WINDOW", lambda: exit(1))
        self._root.configure(background=self._config.background_color)


    def start(self):
        self._root.mainloop()

    def _game_selected(self, game_id):
        self._select_game(game_id)
        self._root.destroy()
        del self

printer = Printer(None)
printer.setDefaultPrinter()

class SnapshotGUI(object):
    def __init__(self, config, current_frame):
        self._config = config
        self._root = tki.Toplevel()
        self._style = ttk.Style()
        self._style.theme_use(self._config.window_theme)

        self._root.wm_title("Photobooth snapshot")
        self._root.wm_protocol("WM_DELETE_WINDOW", self._root.destroy)
        self._root.configure(background=self._config.background_color)

        self._quit_button = ttk.Button(self._root, text="Quit", command=self._root.destroy)
        self._quit_button.pack(side="bottom", fill="both", expand="yes", padx=10, pady=25)

        self._current_frame = current_frame
        self._image = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        #self._image - cv2.cvtColor(self._image, cv2.COLOR_RGB2GRAY)
        try:
            self._image = Image.fromarray(self._image)
            self._image.thumbnail((self._config.snapshot_max_size, self._config.snapshot_max_size), Image.ANTIALIAS)
            self._image_change = self._image.copy()
            self._image = ImageTk.PhotoImage(self._image)
        except AttributeError as err:
            self._image_change = None
            print("Can't render to a blank window or frame")

        self._panel = tki.Label(self._root, image=self._image)
        self._panel.image = self._image
        self._panel.pack(side="left", padx=10, pady=10)
        time_label = tki.Label(self._root, text="Details", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
        time_label.pack(padx=50, pady=10)

        self._display_name = tki.Label(self._root, text="Name", font=(self._config.font_type, 12), background=self._config.background_color, foreground=self._config.font_color)
        self._display_name.pack(padx=50, pady=5)
        
        sv = tki.StringVar()
        sv_lower = tki.StringVar()

        sv.trace("w", lambda name, index, mode, sv=sv, sv_lower=sv_lower: self._name_changed(sv, sv_lower))
        self._input_name = ttk.Entry(self._root, textvariable=sv)
        self._input_name.pack(padx=10, pady=5)
        self._input_name.focus_set()

        self._display_name = tki.Label(self._root, text="Custom", font=(self._config.font_type, 12), background=self._config.background_color, foreground=self._config.font_color)
        self._display_name.pack(padx=50, pady=5)

        sv_lower.trace("w", lambda name, index, mode, sv=sv, sv_lower=sv_lower: self._name_changed(sv, sv_lower))
        self._input_custom = ttk.Entry(self._root, textvariable=sv_lower)
        self._input_custom.pack(padx=10, pady=5)

        self._print_button = ttk.Button(self._root, text="Print", command=self._print_pressed)
        self._print_button.pack(fill="both", pady=5)

        self._font = ImageFont.truetype(self._config.get_font_file("impact"), self._config.text_font_size)

        self._print_status = tki.Label(self._root, text="Press print", font=(self._config.font_type, 20), background=self._config.background_color, foreground=self._config.font_color)

        self._print_status.pack()

        self._temp_image = None

        #self._preview_button = ttk.Button(self._root, text="Preview", command=self._root.destroy)

    def set_print_status(self, status):
        self._print_status.configure(text=status)

    def _print_completed(self, status):
        if status:
            self.set_print_status("Completed!")
        else:
            self.set_print_status("Failed to print!")

    def _print_pressed(self):
        global printer
        self.set_print_status("Starting...")
        print("Attempting to print photo")
        if self._temp_image is None:
            self.set_print_status("Failed to print!")
        self._temp_image.save("snapshot.jpg")
        self.set_print_status("Printing...")
        printer.printImage("snapshot.jpg", "Team 9 photo booth image", self._print_completed)

    def _name_changed(self, sv, sv_lower):
        current_text = sv.get()
        secondary_text = sv_lower.get()

        print("Attempting to set text on image: %s\n%s" % (current_text, secondary_text))
        if self._image_change is None:
            print("Couldn't edit current image since it's None!")
            return
        
        temp_draw = self._image_change.copy()
        W, H = temp_draw.size
       
        print("HEIGHT: %d" % H)

        try:
            draw = ImageDraw.Draw(temp_draw)
            w, h = draw.textsize(current_text, font=self._font)
            s_w, s_h = draw.textsize(secondary_text, font=self._font)
            draw.text(((W - w) / 2, self._config.text_y_offset), current_text, (255, 255, 255), font=self._font)
            #draw.text((W - w) / 2, (H - (h + self._config.text_y_offset)), secondary_text, (255, 255, 255), font=self._font)
            print("HEIGHT2: %d" % h)
            draw.text(((W - s_w) / 2, (H - (s_h + (self._config.text_y_offset * 2)))), secondary_text, (255, 255, 255), font=self._font)
            self._temp_image = temp_draw.copy()
            self._image = ImageTk.PhotoImage(temp_draw)
            self._panel.configure(image=self._image)
            self._panel.image = self._image
        except Exception as err:
            print("Failed drawing text on image: %s" % str(err))

    def start(self):
        self._root.mainloop()

    def _game_selected(self, game_id):
        self._root.destroy()


class PhotoBoothGUI(object):
    def __init__(self, config, loop_pull, emotion_images):
        self._current_frame = None
        self._config = config
        self._stop_event = threading.Event()
        self._loop_pull = loop_pull
        self._emotion_images = emotion_images

        self._root = tki.Tk()
        self._panel = None
        
        self._style = ttk.Style()
        print("System themes available: %s" % str(self._style.theme_names()))
        print("Setting current theme: %s" % self._config.window_theme)
        self._style.theme_use(self._config.window_theme)
        

        self._btn = ttk.Button(self._root, text="Snapshot", command=self._take_snapshot)
        self._btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        self._current_emotion = None

        self._thread = threading.Thread(target=self._loop)
        self._thread.setDaemon(True)
        self._thread.start()

        self._root.wm_title(self._config.window_title)
        self._root.wm_protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.configure(background=self._config.background_color)
        self._root.attributes("-fullscreen", self._config.window_fullscreen)

        self._canvas = tki.Canvas(self._root, width=self._config.window_width, height=self._config.header_height)
        self._canvas.pack()

        self._canvas.create_rectangle(0, 0, self._config.window_width, self._config.header_height, fill=self._config.accent_color)
 
        self._text_id = None

        self.set_header_text("Press start to play")

        self._main_menu = tki.Menu(self._root, tearoff=0, background=self._config.menu_color, foreground=self._config.font_color)
        self._main_menu.add_command(label="Quit", command=self._on_close)

        self._root.configure(menu=self._main_menu)

        self._countdown = None
        self._emotion_show = None
        self._emotion_text = None
        self._start_button = None
        self._start_attached = None

    def start(self):
        self._root.mainloop()

    def set_header_text(self, text):
        if self._text_id is not None:
            self._canvas.delete(self._text_id)

        self._text_id = self._canvas.create_text(0, 0, text=text, anchor="nw", fill="white", font=(self._config.font_type, 18))
        xOffset, yOffset = self.findCenter(self._canvas, self._text_id)
        self._canvas.move(self._text_id, xOffset, yOffset)

    def set_time_left(self, time_left):
        self._countdown.configure(text=str(time_left))
   
    def set_total_points(self, points):
        self._points_total.configure(text=str(points))

    def set_questions_percentage(self, percentage):
        self._questions_percentage.configure(text=str(percentage))

    def findCenter(self, canvas, item):
        coords = canvas.bbox(item)
        xOffset = (self._config.window_width / 2) - ((coords[2] - coords[0]) / 2)
        yOffset = (self._config.header_height / 2) - ((coords[3] - coords[1]) / 2)
        return xOffset, yOffset

    def _take_snapshot(self):
        print("Snapshot button pressed, saving current snapshot")
        
        snapshot_gui = SnapshotGUI(self._config, self._current_frame)
        snapshot_gui.start()

        #cv2.imwrite(self._config.snapshot_image_name, self._current_frame)

        print("Saved snapshot image as %s" % self._config.snapshot_image_name)

    def attach_start(self, main_game_start):
        self._start_attached = main_game_start

    def attach_tick(self, main_game_tick):
        self._main_game_tick = main_game_tick

    def _on_close(self):
        print("Window close button was pressed")
        self._stop_event.set()
        self._root.destroy()
        exit(1)

    def _loop(self):
        try:
            while not self._stop_event.is_set():
                try:
                    self._current_frame, self._current_emotion = self._loop_pull()
                    if self._current_frame is None:
                        print("Can't render a blank frame")
                        continue

                    self._current_frame = imutils.resize(self._current_frame, width=self._config.booth_width)
                
                    image = cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB)
                    try:
                        image = Image.fromarray(image)
                        image = ImageTk.PhotoImage(image)
                    except AttributeError as err:
                        print("Can't render to a blank window or frame")
                    try:
                        emotion_image = self._emotion_images[self._current_emotion[1][0]]
                    except Exception as err:
                        print("Failed getting emotion image! %s" % str(err))
                        emotion_image = None

                    emotion_image = cv2.cvtColor(emotion_image, cv2.COLOR_BGR2RGB)
                    if emotion_image is not None:
                        emotion_image = Image.fromarray(emotion_image)
                        emotion_image = ImageTk.PhotoImage(emotion_image)

                    if self._panel is None:
                        self._panel = tki.Label(image=image)
                        self._panel.image = image
                        self._panel.pack(side="left", padx=10, pady=10)
                        time_label = tki.Label(text="Time Left (Seconds)", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
                        time_label.pack(pady=10)
                        
                        self._countdown = tki.Label(text="Not playing a game", font=(self._config.font_type, 16), background=self._config.background_color, foreground=self._config.font_color)
                        self._countdown.pack()

                        sep = tki.Frame(height=10, bd=20, relief=tki.SUNKEN, background=self._config.accent_color)
                        sep.pack(fill=tki.X, padx=5, pady=5)

                        status_label = ttk.Label(text="Status", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
                        status_label.pack()

                        if emotion_image is not None:
                            self._emotion_show = ttk.Label(image=emotion_image)
                            self._emotion_show.image = emotion_image
                            self._emotion_show.pack()

                        self._emotion_text = ttk.Label(text="Starting...", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
                        self._emotion_text.pack()

                        sep_lower = tki.Frame(height=10, bd=20, relief=tki.SUNKEN, background=self._config.accent_color)
                        sep_lower.pack(fill=tki.X, padx=5, pady=5)

                        self._questions_label = ttk.Label(text="Questions correct:", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
                        self._questions_label.pack()

                        self._questions_percentage = ttk.Label(text="0%", font=(self._config.font_type, 18), background=self._config.background_color, foreground=self._config.font_color)
                        self._questions_percentage.pack()

                        self._points_label = ttk.Label(text="Total points", font=(self._config.font_type, 21), background=self._config.background_color, foreground=self._config.font_color)
                        self._points_label.pack(pady=10)

                        self._points_total = ttk.Label(text="0", font=(self._config.font_type, 18), background=self._config.background_color, foreground=self._config.font_color)
                        self._points_total.pack()

                        sep_lowest = tki.Frame(height=10, bd=20, relief=tki.SUNKEN, background=self._config.accent_color)
                        sep_lowest.pack(fill=tki.X, padx=5, pady=5)

                        self._start_button = ttk.Button(text="Start the game", command=self._start_attached)
                        self._start_button.pack(fill=tki.BOTH, pady=10)

                    else:
                        self._panel.configure(image=image)
                        self._panel.image = image

                        if emotion_image is not None:
                            self._emotion_show.configure(image=emotion_image)
                            self._emotion_show.image = emotion_image
                        if self._current_emotion[0]:
                            self._emotion_text.configure(text=self._current_emotion[1][1], foreground=self._config.font_color)
                        else:
                            self._emotion_text.configure(text="No face detected", foreground=self._config.font_red_color)
                    self._main_game_tick()
                except RuntimeError as err:
                    print("Caught runtime error! %s" % str(err))
                except Exception as err:
                    print("Caught unknown exception! %s" % str(err))

        except RuntimeError as err:
            print("Caught runtime error! %s" % str(err))
        except Exception as err:
            print("Caught unknown error! %s" % str(err))
