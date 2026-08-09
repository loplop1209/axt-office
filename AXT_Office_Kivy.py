# -*- coding: utf-8 -*-
"""
AXT OFFICE — Kivy / Android Edition
Port of the supplied single-file PySide6 application.

Desktop:
    pip install kivy jdatetime sounddevice plyer
    python AXT_Office_Kivy.py

Android:
    See the Buildozer instructions supplied with this file.
    The database schema, sections, settings, themes, dashboard options,
    quotes, search, backup/restore, recorder, custom media, logos and
    Jalali/Gregorian calendar are retained.
"""

import os
import sys
import json
import math
import random
import shutil
import sqlite3
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, date, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.metrics import dp, sp
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.progressbar import ProgressBar
from kivy.uix.colorpicker import ColorPicker

try:
    import jdatetime
except Exception:
    jdatetime = None

try:
    import sounddevice as sd
    import wave
    import queue
except Exception:
    sd = None

try:
    from plyer import filechooser
except Exception:
    filechooser = None

try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except Exception:
    ANDROID = False

try:
    from jnius import autoclass
except Exception:
    autoclass = None


APP_DIR = Path.home() / "AXT_Office"
try:
    APP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    APP_DIR = Path.cwd() / "AXT_Office"
    APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DIR / "axt_office.db"

THEMES = {
    "Dark": {
        "bg": "#0b0e14", "panel": "#121722", "panel2": "#171d2a",
        "text": "#edf2ff", "muted": "#8e9ab3", "border": "#293246",
        "accent": "#6c63ff", "accent2": "#8b83ff", "danger": "#ff5d73",
        "success": "#42d392", "input": "#0f141e", "glow": "#6c63ff",
    },
    "Light": {
        "bg": "#f3f6fb", "panel": "#ffffff", "panel2": "#eef2f8",
        "text": "#172033", "muted": "#667085", "border": "#d9e0eb",
        "accent": "#5b4bff", "accent2": "#7a6fff", "danger": "#dc3545",
        "success": "#159570", "input": "#f8faff", "glow": "#8a80ff",
    },
    "Neon": {
        "bg": "#05070b", "panel": "#0b1017", "panel2": "#101722",
        "text": "#eaffff", "muted": "#79a6ad", "border": "#16414b",
        "accent": "#00e5ff", "accent2": "#00ffc8", "danger": "#ff4d8d",
        "success": "#00ffc8", "input": "#071017", "glow": "#00e5ff",
    },
    "Cyberpunk": {
        "bg": "#090713", "panel": "#130e21", "panel2": "#1b122b",
        "text": "#fff3ff", "muted": "#ad8bb6", "border": "#442058",
        "accent": "#ff2bd6", "accent2": "#ffe600", "danger": "#ff4568",
        "success": "#b8ff00", "input": "#100b19", "glow": "#ff2bd6",
    },
    "Midnight": {
        "bg": "#07111f", "panel": "#0d1a2c", "panel2": "#12233a",
        "text": "#edf7ff", "muted": "#83a0bd", "border": "#203b5b",
        "accent": "#3aa8ff", "accent2": "#65c7ff", "danger": "#ff637d",
        "success": "#45ddb1", "input": "#091524", "glow": "#3aa8ff",
    },
    "Aurora": {
        "bg": "#071514", "panel": "#0c211d", "panel2": "#12312a",
        "text": "#ecfff8", "muted": "#86b9aa", "border": "#1d4b40",
        "accent": "#48e6a0", "accent2": "#78f7c1", "danger": "#ff7085",
        "success": "#6dffbd", "input": "#091c18", "glow": "#48e6a0",
    },
    "Sakura": {
        "bg": "#190f18", "panel": "#251521", "panel2": "#32202d",
        "text": "#fff0f7", "muted": "#c79daf", "border": "#59384b",
        "accent": "#ff7eb6", "accent2": "#ffb3d3", "danger": "#ff667f",
        "success": "#72e0a3", "input": "#1c1119", "glow": "#ff7eb6",
    },
    "Forest": {
        "bg": "#0b1510", "panel": "#122118", "panel2": "#193021",
        "text": "#eefbea", "muted": "#91b09a", "border": "#2d4a34",
        "accent": "#8fd35f", "accent2": "#b6ed7d", "danger": "#ff7777",
        "success": "#6ee7a0", "input": "#0e1b13", "glow": "#8fd35f",
    },
    "Ocean": {
        "bg": "#06131a", "panel": "#0b202b", "panel2": "#10303d",
        "text": "#eafaff", "muted": "#7faeba", "border": "#1d4657",
        "accent": "#36c7ff", "accent2": "#72ddff", "danger": "#ff6e87",
        "success": "#55e0c0", "input": "#081b24", "glow": "#36c7ff",
    },
    "Candy": {
        "bg": "#17111d", "panel": "#24182b", "panel2": "#33203c",
        "text": "#fff6ff", "muted": "#c0a5c9", "border": "#553b61",
        "accent": "#c58cff", "accent2": "#ff8fcf", "danger": "#ff6b83",
        "success": "#77e5b1", "input": "#1c1322", "glow": "#c58cff",
    },
    "Coffee": {
        "bg": "#17100d", "panel": "#251914", "panel2": "#35231c",
        "text": "#fff4e8", "muted": "#c4a58f", "border": "#5b3b2c",
        "accent": "#d79b62", "accent2": "#f1bd83", "danger": "#ff7b68",
        "success": "#83d29c", "input": "#1c120e", "glow": "#d79b62",
    },
}

BACKGROUNDS = [
    "Particles", "Stars", "Waves", "Gradient", "Glow", "Cyber Grid",
    "Space", "Aurora", "Matrix Rain", "Fireflies", "Bubbles",
    "Sticker Rain", "Custom Media",
]

DEFAULT_ROUTINES = {
    0: ["مرتب کردن میز و فضای کار", "۲۰ دقیقه حرکت یا پیاده‌روی",
        "یک کار مهم را بدون حواس‌پرتی انجام بده", "۱۰ دقیقه مطالعه",
        "قبل از خواب فردا را برنامه‌ریزی کن"],
    1: ["یک لیوان آب و صبحانه", "۲۵ دقیقه کار عمیق",
        "یک پیام خوب برای یک نفر بفرست", "۱۵ دقیقه یادگیری",
        "۵ دقیقه جمع‌وجور کردن اتاق"],
    2: ["کمی کشش و حرکت", "یک کار عقب‌افتاده را تمام کن",
        "۳۰ دقیقه روی یک مهارت تمرین کن", "۱۰ دقیقه بدون موبایل استراحت کن",
        "سه چیز خوب امروز را بنویس"],
    3: ["شروع روز بدون شبکه اجتماعی", "یک هدف کوچک را کامل کن",
        "۲۰ دقیقه خلاقیت یا موسیقی", "یک کار برای آینده‌ات انجام بده",
        "وسایل فردا را آماده کن"],
    4: ["میز کار را مرتب کن", "یک کار سخت را اول انجام بده",
        "۱۵ دقیقه مطالعه یا آموزش", "با یک دوست/خانواده وقت بگذران",
        "امروز را مرور کن"],
    5: ["یک پیاده‌روی کوتاه", "یک ایده جدید ثبت کن",
        "۳۰ دقیقه پروژه شخصی", "یک کار کوچک خانه",
        "برای هفته بعد یک هدف بنویس"],
    6: ["استراحت واقعی و بدون عذاب وجدان",
        "یک مکان جدید یا جذاب پیدا کن", "عکس یا خاطره‌ای ثبت کن",
        "یک ساعت برای علاقه‌ات وقت بگذار", "هفته آینده را سبک برنامه‌ریزی کن"],
}

DAILY_IDEAS = [
    "امروز یک مسیر جدید برای پیاده‌روی انتخاب کن.",
    "یک آهنگ کوتاه بساز یا یک ملودی جدید امتحان کن.",
    "۱۰ عکس از چیزهای جالب اطرافت بگیر.",
    "یک گوشه از اتاقت را کاملاً بازطراحی کن.",
    "یک مهارت کوچک را در ۳۰ دقیقه یاد بگیر.",
    "یک غذای ساده جدید درست کن.",
    "یک لیست ۱۰تایی از چیزهایی که دوست داری بساز.",
    "یک پروژه ۲۰ دقیقه‌ای را از صفر شروع کن.",
    "یک مکان جذاب در شهر خودت پیدا کن و برایش برنامه بریز.",
    "امروز یک کار را کاملاً آفلاین انجام بده.",
    "یک پوستر یا طرح گرافیکی کوچک طراحی کن.",
    "یک فایل قدیمی را مرتب و آرشیو کن.",
]

LOCATION_SEEDS = [
    ("برج میلاد", "تهران", "Entertainment", "تهران، ایران", "", "نماد شهری و مناسب برای منظره و عکاسی"),
    ("کاخ گلستان", "تهران", "Travel", "تهران، ایران", "", "فضای تاریخی و معماری جذاب"),
    ("پارک آب و آتش", "تهران", "Nature", "تهران، ایران", "", "برای پیاده‌روی و عکاسی"),
    ("بازار بزرگ تهران", "تهران", "Shopping", "تهران، ایران", "", "فضای شهری و تجربه محلی"),
    ("دریاچه چیتگر", "تهران", "Nature", "تهران، ایران", "", "غروب و دوچرخه‌سواری"),
    ("میدان نقش جهان", "اصفهان", "Travel", "اصفهان، ایران", "", "معماری و گردش شهری"),
    ("روستای ماسوله", "گیلان", "Nature", "گیلان، ایران", "", "طبیعت و معماری پلکانی"),
    ("پارک ملت", "تهران", "Nature", "تهران، ایران", "", "فضای سبز و آرامش"),
    ("CN Tower", "Toronto", "Entertainment", "Toronto, Canada", "", "نمای شهری و تجربه تورنتو"),
    ("Stanley Park", "Vancouver", "Nature", "Vancouver, Canada", "", "طبیعت و دوچرخه‌سواری"),
    ("Banff National Park", "Alberta", "Nature", "Alberta, Canada", "", "طبیعت کوهستانی"),
    ("Old Montreal", "Montreal", "Travel", "Montreal, Canada", "", "خیابان‌های تاریخی و کافه‌ها"),
]


class DB:
    def __init__(self):
        self.path = str(DB_PATH)
        self.c = sqlite3.connect(self.path, check_same_thread=False)
        self.c.row_factory = sqlite3.Row
        self.c.execute("PRAGMA journal_mode=WAL")
        self.c.execute("PRAGMA foreign_keys=ON")
        self.c.executescript("""
        CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,title TEXT,done INTEGER DEFAULT 0,due TEXT,created TEXT);
        CREATE TABLE IF NOT EXISTS routines(id INTEGER PRIMARY KEY,title TEXT,done INTEGER DEFAULT 0,created TEXT);
        CREATE TABLE IF NOT EXISTS countdowns(id INTEGER PRIMARY KEY,title TEXT,target TEXT);
        CREATE TABLE IF NOT EXISTS music(id INTEGER PRIMARY KEY,title TEXT,category TEXT,description TEXT,bpm INTEGER,music_key TEXT,genre TEXT,mood TEXT,cover TEXT,created TEXT);
        CREATE TABLE IF NOT EXISTS lyrics(id INTEGER PRIMARY KEY,title TEXT,content TEXT,status TEXT,genre TEXT,cover TEXT,created TEXT,updated TEXT);
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY,title TEXT,content TEXT,category TEXT,tags TEXT,created TEXT,updated TEXT);
        CREATE TABLE IF NOT EXISTS youtube(id INTEGER PRIMARY KEY,title TEXT,channel TEXT,status TEXT,prompt TEXT,description TEXT,url TEXT,created TEXT);
        CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY,name TEXT,city TEXT,category TEXT,address TEXT,url TEXT,notes TEXT,visited INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY,title TEXT,description TEXT,progress INTEGER DEFAULT 0,score INTEGER DEFAULT 0,deadline TEXT,sticker TEXT);
        CREATE TABLE IF NOT EXISTS quotes(id INTEGER PRIMARY KEY, text TEXT UNIQUE, author TEXT, language TEXT, source TEXT, seen INTEGER DEFAULT 0, created TEXT);
        CREATE TABLE IF NOT EXISTS daily_routines(id INTEGER PRIMARY KEY, day TEXT, item TEXT, done INTEGER DEFAULT 0, UNIQUE(day,item));
        """)
        self.c.commit()

    def all(self, q, p=()):
        return self.c.execute(q, p).fetchall()

    def one(self, q, p=()):
        return self.c.execute(q, p).fetchone()

    def ex(self, q, p=()):
        self.c.execute(q, p)
        self.c.commit()

    def setting(self, key, default=""):
        row = self.one("SELECT v FROM settings WHERE k=?", (key,))
        return row["v"] if row else default

    def set_setting(self, key, value):
        self.ex("INSERT OR REPLACE INTO settings(k,v) VALUES(?,?)", (key, str(value)))

    def close(self):
        try:
            self.c.close()
        except Exception:
            pass


class MotivationService:
    FALLBACK_EN = [
        ("Keep going. Small steps still move you forward.", "AXT"),
        ("You do not need the whole path. Take the next step.", "AXT"),
        ("Progress beats perfection when you keep showing up.", "AXT"),
        ("Build something today that tomorrow-you will thank you for.", "AXT"),
        ("A slow day is still a day you can use well.", "AXT"),
        ("Start small, stay curious, and keep making.", "AXT"),
        ("One focused action can change the direction of a day.", "AXT"),
        ("Your ideas deserve a chance to become real things.", "AXT"),
        ("Mistakes are drafts, not verdicts.", "AXT"),
        ("Make the next version, not the perfect version.", "AXT"),
    ]
    FALLBACK_FA = [
        ("آرام جلو برو؛ مهم این است که متوقف نشوی.", "AXT"),
        ("هر قدم کوچک امروز، بخشی از آینده‌ای است که می‌سازی.", "AXT"),
        ("قرار نیست کامل باشی؛ قرار است ادامه بدهی.", "AXT"),
        ("چیزی که امروز تمرین می‌کنی، فردای تو را می‌سازد.", "AXT"),
        ("اگر سرعتت کم است، باز هم در حال پیش رفتنی.", "AXT"),
        ("به خودت فرصت بده تا تبدیل به کسی شوی که می‌خواهی.", "AXT"),
        ("شروع کوچک، بهتر از برنامه‌ای است که هیچ‌وقت اجرا نمی‌شود.", "AXT"),
        ("امروز فقط یک کار مهم را بهتر از دیروز انجام بده.", "AXT"),
        ("ذهن خلاق با کنجکاوی زنده می‌ماند؛ ادامه بده و بساز.", "AXT"),
        ("تو لازم نیست همه راه را ببینی؛ قدم بعدی کافی است.", "AXT"),
        ("اشتباه، بخشی از نسخه اولیه‌ی هر چیز خوب است.", "AXT"),
        ("وقت ساختن چیزی است که فردای تو به آن افتخار کند.", "AXT"),
    ]

    @staticmethod
    def fetch_english():
        urls = [
            "https://zenquotes.io/api/quotes",
            "https://api.quotable.io/quotes?tags=motivational|inspirational&limit=50",
        ]
        for url in urls:
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "AXT-Office/2.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode("utf-8"))
                result = []
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            text = item.get("q") or item.get("content")
                            author = item.get("a") or item.get("author") or "Unknown"
                            if text:
                                result.append((str(text).strip(), str(author).strip()))
                if result:
                    return result
            except Exception:
                continue
        return []


class AndroidRecorder:
    """Android MediaRecorder wrapper. Uses the microphone directly on Android."""
    def __init__(self):
        self.running = False
        self.output_path = None
        self.recorder = None

    def start(self, output_path):
        if self.running:
            raise RuntimeError("Recorder is already running.")
        self.output_path = str(output_path)
        if ANDROID and autoclass:
            MediaRecorder = autoclass("android.media.MediaRecorder")
            AudioSource = autoclass("android.media.MediaRecorder$AudioSource")
            OutputFormat = autoclass("android.media.MediaRecorder$OutputFormat")
            AudioEncoder = autoclass("android.media.MediaRecorder$AudioEncoder")
            self.recorder = MediaRecorder()
            self.recorder.setAudioSource(AudioSource.MIC)
            self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
            self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            self.recorder.setOutputFile(self.output_path)
            self.recorder.prepare()
            self.recorder.start()
            self.running = True
            return
        if sd is None:
            raise RuntimeError("sounddevice is not installed.")
        import wave as _wave
        import queue as _queue
        self._q = _queue.Queue()
        self._wf = _wave.open(self.output_path, "wb")
        self._wf.setnchannels(1)
        self._wf.setsampwidth(2)
        self._wf.setframerate(44100)
        self._sd = sd

        def callback(indata, frames, time_info, status):
            if self.running:
                self._q.put(bytes(indata))

        self._running = True
        self.running = True

        def writer():
            while self._running or not self._q.empty():
                try:
                    chunk = self._q.get(timeout=0.2)
                except Exception:
                    continue
                try:
                    self._wf.writeframes(chunk)
                except Exception:
                    pass

        self._thread = threading.Thread(target=writer, daemon=True)
        self._thread.start()
        self._stream = self._sd.RawInputStream(
            samplerate=44100, channels=1, dtype="int16",
            callback=callback, blocksize=2048
        )
        self._stream.start()

    def stop(self):
        if not self.running:
            return self.output_path
        if ANDROID and self.recorder is not None:
            try:
                self.recorder.stop()
            except Exception:
                pass
            try:
                self.recorder.release()
            except Exception:
                pass
            self.recorder = None
            self.running = False
            return self.output_path

        self._running = False
        self.running = False
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass
        try:
            self._thread.join(timeout=3)
        except Exception:
            pass
        try:
            self._wf.close()
        except Exception:
            pass
        return self.output_path

    def discard(self):
        p = self.stop()
        if p:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass
        self.output_path = None


class AXTBackground(FloatLayout):
    """Kivy canvas version of the animated background styles."""
    style_name = StringProperty("Particles")
    enabled = BooleanProperty(True)
    intensity = NumericProperty(60)
    phase = NumericProperty(0.0)
    accent = StringProperty("#6c63ff")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rng = random.Random(7319)
        self.particles = [
            (rng.random(), rng.random(), rng.uniform(.001, .004), rng.uniform(1, 3))
            for _ in range(90)
        ]
        self.stars = [
            (rng.random(), rng.random(), rng.uniform(.2, 1), rng.uniform(.5, 2))
            for _ in range(130)
        ]
        self.bind(size=lambda *_: self.redraw(), pos=lambda *_: self.redraw())
        Clock.schedule_interval(self.tick, 1 / 30)

    def tick(self, dt):
        if self.enabled:
            self.phase += .008 * (.25 + self.intensity / 75.0)
            self.redraw()

    def rgba(self, hexv, alpha=1):
        h = hexv.lstrip("#")
        if len(h) == 6:
            return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (alpha,)
        return (1, 1, 1, alpha)

    def redraw(self):
        self.canvas.before.clear()
        if not self.enabled or self.intensity <= 0:
            return
        with self.canvas.before:
            bg = self.rgba(self.app_theme["bg"] if hasattr(self, "app_theme") else "#0b0e14")
            Color(*bg)
            Rectangle(pos=self.pos, size=self.size)
            self._draw_style()

    def _draw_style(self):
        s = self.intensity / 100.0
        w, h = max(1, self.width), max(1, self.height)
        col = self.rgba(self.accent, .18 + .25 * s)
        Color(*col)
        if self.style_name in ("Particles", "Space"):
            for x, y, speed, size in self.particles:
                yy = (y + self.phase * speed * 35) % 1
                Ellipse(pos=(self.x + x*w, self.y + yy*h), size=(dp(size), dp(size)))
        if self.style_name in ("Stars", "Space"):
            for x, y, twinkle, size in self.stars:
                a = .15 + ((math.sin(self.phase * twinkle * 8 + x*20)+1)/2)*.45*s
                Color(0.82, .88, 1, a)
                Ellipse(pos=(self.x+x*w, self.y+y*h), size=(dp(size), dp(size)))
        if self.style_name == "Waves":
            Color(*self.rgba(self.accent, .25))
            for band in range(4):
                pts = []
                base = h*(.25 + band*.18)
                for xx in range(0, int(w)+20, 20):
                    yy = base + math.sin(xx/120 + self.phase*(1.3+band*.2))*(16+18*s)
                    pts += [self.x+xx, self.y+yy]
                if len(pts) >= 4:
                    Line(points=pts, width=1.2)
        if self.style_name in ("Gradient", "Glow", "Aurora"):
            # Kivy does not have the same radial-gradient API as Qt;
            # layered translucent circles reproduce the visual effect.
            for i in range(5):
                x = w*(.15 + i*.18) + math.sin(self.phase*.55+i)*70
                y = h*(.22 + i*.12) + math.cos(self.phase*.4+i)*45
                Color(*self.rgba(self.accent, .035 + .018*s))
                Ellipse(pos=(self.x+x-140, self.y+y-140), size=(280, 280))
        if self.style_name == "Cyber Grid":
            Color(*self.rgba(self.accent, .18*s))
            horizon = int(h*.68)
            for yy in range(horizon, int(h), 32):
                Line(points=[self.x, self.y+yy, self.x+w, self.y+yy], width=1)
            center = self.x+w/2
            for i in range(-14, 15):
                Line(points=[center, self.y+horizon, center+i*110, self.y+h], width=1)
        if self.style_name == "Matrix Rain":
            Color(.15, 1, .58, .3*s)
            for xx in range(0, int(w), 28):
                for yy in range(-28, int(h)+28, 28):
                    y2 = (yy + int(self.phase*70)*((xx//28)%3+1)) % max(1, int(h))
                    # Small vertical strokes stand in for glyph rain.
                    Line(points=[self.x+xx, self.y+y2, self.x+xx, self.y+y2+7], width=1)
        if self.style_name == "Fireflies":
            for x, y, twinkle, size in self.stars:
                a = .12 + ((math.sin(self.phase*twinkle*5+x*30)+1)/2)*.55*s
                Color(1, .86, .35, a)
                Ellipse(pos=(self.x+x*w, self.y+y*h), size=(dp(size+1.5), dp(size+1.5)))
        if self.style_name == "Bubbles":
            Color(*self.rgba("#96d2ff", .22*s))
            for x, y, speed, size in self.particles[:45]:
                yy = (y - self.phase*speed*22) % 1
                radius = 4 + size*2
                Line(circle=(self.x+x*w, self.y+yy*h, radius), width=1)
        if self.style_name == "Sticker Rain":
            Color(*self.rgba(self.accent, .12*s))
            for i, (x, y, speed, size) in enumerate(self.particles[:28]):
                yy = (y + self.phase*speed*34) % 1
                side = 18 + size*7
                RoundedRectangle(pos=(self.x+x*w-side/2, self.y+yy*h-side/2),
                                 size=(side, side), radius=[dp(5)])


class Card(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation="vertical", padding=dp(18), spacing=dp(9), **kwargs)
        self.app_ref = app
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.before.clear()
        t = self.app_ref.theme
        with self.canvas.before:
            Color(*self.app_ref.rgba(t["panel"], self.app_ref.panel_opacity/100))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])
            Color(*self.app_ref.rgba(t["border"], .8))
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(20)), width=1)


class StyledButton(Button):
    kind = StringProperty("normal")

    def __init__(self, app, **kwargs):
        self.app_ref = app
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.color = app.theme_rgba("text")
        self.font_size = sp(13)
        self.bind(pos=self.redraw, size=self.redraw, state=self.redraw)
        self.redraw()

    def redraw(self, *_):
        self.canvas.before.clear()
        t = self.app_ref.theme
        with self.canvas.before:
            if self.kind == "primary":
                Color(*self.app_ref.rgba(t["accent"], 1 if self.state != "down" else .8))
            elif self.kind == "danger":
                Color(*self.app_ref.rgba(t["danger"], .18))
            else:
                Color(*self.app_ref.rgba(t["panel2"], 1))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(13)])
            Color(*self.app_ref.rgba(t["border"], 1))
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(13)), width=1)


class AXTOfficeApp(App):
    title = "AXT OFFICE"

    def build(self):
        self.db = DB()
        self.load_preferences()
        if ANDROID:
            try:
                request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])
            except Exception:
                pass

        Window.clearcolor = self.rgba(self.theme["bg"])
        self.bg = AXTBackground(
            style_name=self.background_name,
            enabled=self.background_enabled,
            intensity=self.intensity,
            accent=self.theme["accent"],
        )
        self.bg.app_theme = self.theme
        self.root_float = FloatLayout()
        self.root_float.add_widget(self.bg)

        self.sm = ScreenManager(transition=NoTransition())
        self.root_float.add_widget(self.sm)

        self.build_navigation()
        self._seed_locations()
        self._ensure_fallback_quotes()
        self._prepare_motivation()
        self.show_dashboard()
        return self.root_float

    # ---------- preferences / theme ----------

    def load_preferences(self):
        self.theme_name = self.db.setting("theme", "Dark")
        if self.theme_name not in THEMES:
            self.theme_name = "Dark"
        try:
            self.custom_themes = json.loads(self.db.setting("custom_themes", "{}"))
        except Exception:
            self.custom_themes = {}
        for name, theme in self.custom_themes.items():
            if isinstance(theme, dict) and all(
                k in theme for k in [
                    "bg","panel","panel2","text","muted","border",
                    "accent","accent2","danger","success","input","glow"
                ]
            ):
                THEMES[name] = theme
        self.theme = THEMES[self.theme_name]
        self.background_name = self.db.setting("background", "Particles")
        if self.background_name not in BACKGROUNDS:
            self.background_name = "Particles"
        self.background_enabled = self.db.setting("background_enabled", "1") != "0"
        try:
            self.intensity = int(self.db.setting("animation_intensity", "60"))
        except Exception:
            self.intensity = 60
        self.effects_enabled = self.db.setting("ui_effects", "1") != "0"
        try:
            self.panel_opacity = max(20, min(98, int(self.db.setting("panel_opacity", "58"))))
        except Exception:
            self.panel_opacity = 58
        try:
            self.background_opacity = max(10, min(100, int(self.db.setting("background_opacity", "80"))))
        except Exception:
            self.background_opacity = 80
        self.language = self.db.setting("language", "فارسی")
        self.calendar_system = self.db.setting("calendar", "Gregorian")
        self.routine_dashboard = self.db.setting("routine_dashboard", "1") != "0"
        self.idea_dashboard = self.db.setting("idea_dashboard", "1") != "0"
        self.quote_dashboard = self.db.setting("quote_dashboard", "1") != "0"
        self.stats_dashboard = self.db.setting("stats_dashboard", "1") != "0"
        self.calendar_dashboard = self.db.setting("calendar_dashboard", "1") != "0"
        self.agenda_dashboard = self.db.setting("agenda_dashboard", "1") != "0"
        self.custom_media_path = self.db.setting("custom_media_path", "")
        self.audio_recorder = AndroidRecorder()

    def apply_theme(self):
        self.theme = THEMES[self.theme_name]
        Window.clearcolor = self.rgba(self.theme["bg"])
        if hasattr(self, "bg"):
            self.bg.style_name = self.background_name
            self.bg.enabled = self.background_enabled
            self.bg.intensity = self.intensity
            self.bg.accent = self.theme["accent"]
            self.bg.app_theme = self.theme
            self.bg.redraw()

    def rgba(self, value, alpha=1):
        value = value.lstrip("#")
        if len(value) != 6:
            return (1, 1, 1, alpha)
        return tuple(int(value[i:i+2], 16)/255 for i in (0,2,4)) + (alpha,)

    def theme_rgba(self, key):
        return self.rgba(self.theme[key])

    def tr(self, fa, en):
        return fa if self.language == "فارسی" else en

    # ---------- shell/navigation ----------

    def build_navigation(self):
        self.nav = BoxLayout(orientation="vertical", size_hint=(None, 1),
                             width=dp(245), padding=dp(14), spacing=dp(6))
        self.root_float.add_widget(self.nav)

        logo = Label(text="✦  AXT\n     OFFICE", markup=True,
                     font_size=sp(24), size_hint_y=None, height=dp(82),
                     color=self.theme_rgba("text"))
        self.nav.add_widget(logo)
        self.nav.add_widget(Label(text="✿  CREATE • PLAN • MAKE  ✿",
                                  size_hint_y=None, height=dp(28),
                                  color=self.theme_rgba("accent2"), font_size=sp(9)))
        self.nav.add_widget(Label(text="PERSONAL COMMAND CENTER",
                                  size_hint_y=None, height=dp(25),
                                  color=self.theme_rgba("accent"), font_size=sp(9)))

        items = [
            ("⌂", "Dashboard", self.show_dashboard),
            ("✓", "Tasks", lambda: self.show_crud("Tasks","tasks", self.task_fields,"title","✓")),
            ("🔥", "Routines", lambda: self.show_crud("Routines","routines", self.routine_fields,"title","🔥")),
            ("◷", "Countdown", lambda: self.show_crud("Countdown","countdowns", self.countdown_fields,"title","◷")),
            ("♫", "Music", self.show_music),
            ("✎", "Lyrics", lambda: self.show_crud("Lyrics","lyrics", self.lyrics_fields,"title","✎")),
            ("▤", "Notes", lambda: self.show_crud("Notes","notes", self.notes_fields,"title","▤")),
            ("▶", "YouTube", lambda: self.show_crud("YouTube","youtube", self.youtube_fields,"title","▶")),
            ("⌖", "Locations", lambda: self.show_crud("Locations","locations", self.location_fields,"name","⌖")),
            ("◎", "Goals", lambda: self.show_crud("Goals","goals", self.goal_fields,"title","◎")),
            ("⌕", "Search", self.show_search),
            ("⇩", "Backup", self.show_backup),
            ("⚙", "Settings", self.show_settings),
        ]
        self.nav_buttons = []
        for icon, text, fn in items:
            b = StyledButton(self, text=f"{icon}   {self.tr(text,text)}",
                             size_hint_y=None, height=dp(43))
            b.bind(on_release=lambda _b, f=fn: f())
            self.nav.add_widget(b)
            self.nav_buttons.append(b)
        self.nav.add_widget(WidgetSpacer())
        self.nav.add_widget(Label(text="●  SYSTEM READY",
                                  size_hint_y=None, height=dp(24),
                                  color=self.theme_rgba("success"), font_size=sp(10)))

        self.content = FloatLayout()
        self.content.pos_hint = {"x": 0}
        self.content.size_hint = (1,1)
        self.content.x = dp(245)
        self.content.width = Window.width - dp(245)
        self.root_float.bind(size=self._resize_content)
        self.root_float.add_widget(self.content)
        # ScreenManager is already a child; place it over the content region.
        self.sm.pos = (dp(245), 0)
        self.sm.size_hint = (None, 1)
        self.sm.width = max(dp(300), Window.width-dp(245))
        self.root_float.remove_widget(self.sm)
        self.root_float.add_widget(self.sm)

    def _resize_content(self, *_):
        self.sm.pos = (dp(245), 0)
        self.sm.width = max(dp(300), self.root_float.width-dp(245))

    def add_screen(self, name):
        if self.sm.has_screen(name):
            self.sm.remove_widget(self.sm.get_screen(name))
        s = Screen(name=name)
        self.sm.add_widget(s)
        return s

    def screen_layout(self, title, sub=""):
        s = self.add_screen("current")
        root = BoxLayout(orientation="vertical", padding=[dp(25),dp(22),dp(18),dp(22)], spacing=dp(12))
        head = BoxLayout(size_hint_y=None, height=dp(78), spacing=dp(12))
        title_box = BoxLayout(orientation="vertical")
        title_box.add_widget(Label(text="AXT OFFICE", size_hint_y=None, height=dp(20),
                                   color=self.theme_rgba("accent"), font_size=sp(10)))
        title_box.add_widget(Label(text=self.tr(title,title), size_hint_y=None, height=dp(38),
                                   color=self.theme_rgba("text"), font_size=sp(29)))
        if sub:
            title_box.add_widget(Label(text=sub, color=self.theme_rgba("muted"), font_size=sp(12)))
        head.add_widget(title_box)
        head.add_widget(WidgetSpacer())
        root.add_widget(head)
        s.add_widget(root)
        self.sm.current = "current"
        return s, root

    # ---------- common widgets ----------

    def label(self, text, size=13, color="text", **kw):
        return Label(text=str(text), color=self.theme_rgba(color),
                     font_size=sp(size), halign="left", valign="middle", **kw)

    def input(self, text="", multiline=False, hint=""):
        x = TextInput(text=str(text or ""), multiline=multiline,
                      hint_text=hint, foreground_color=self.theme_rgba("text"),
                      background_color=self.rgba(self.theme["input"], .96),
                      cursor_color=self.theme_rgba("accent"),
                      padding=[dp(12),dp(9)], font_size=sp(13))
        return x

    def button(self, text, fn=None, kind="normal", height=44):
        b = StyledButton(self, text=text, kind=kind, size_hint_y=None, height=dp(height))
        if fn:
            b.bind(on_release=lambda *_: fn())
        return b

    def popup(self, title, content, size=(.9,.8)):
        p = Popup(title=title, content=content, size_hint=size,
                  title_color=self.theme_rgba("text"),
                  separator_color=self.theme_rgba("accent"))
        p.open()
        return p

    # ---------- seed / motivation ----------

    def _seed_locations(self):
        for name, city, category, address, url, notes in LOCATION_SEEDS:
            if not self.db.one("SELECT id FROM locations WHERE name=? AND city=?", (name,city)):
                self.db.ex(
                    "INSERT INTO locations(name,city,category,address,url,notes,visited) VALUES(?,?,?,?,?,?,0)",
                    (name,city,category,address,url,notes)
                )

    def _ensure_daily_routine(self):
        day = date.today().isoformat()
        if not self.db.one("SELECT id FROM daily_routines WHERE day=? LIMIT 1", (day,)):
            for item in DEFAULT_ROUTINES[date.today().weekday()]:
                self.db.ex("INSERT OR IGNORE INTO daily_routines(day,item,done) VALUES(?,?,0)", (day,item))
        return self.db.all("SELECT * FROM daily_routines WHERE day=? ORDER BY id", (day,))

    def _daily_idea(self):
        key = "daily_idea_date"
        if self.db.setting(key,"") != date.today().isoformat():
            ideas = DAILY_IDEAS[:]
            random.shuffle(ideas)
            self.db.set_setting("daily_idea", ideas[0])
            self.db.set_setting(key, date.today().isoformat())
        return self.db.setting("daily_idea", DAILY_IDEAS[0])

    def _ensure_fallback_quotes(self):
        banks = [("فارسی", MotivationService.FALLBACK_FA), ("English", MotivationService.FALLBACK_EN)]
        for language, bank in banks:
            for text, author in bank:
                self.db.ex(
                    "INSERT OR IGNORE INTO quotes(text,author,language,source,seen,created) VALUES(?,?,?,?,0,?)",
                    (text,author,language,"AXT fallback",datetime.now().isoformat(timespec="seconds"))
                )

    def _prepare_motivation(self):
        self.current_quote_text, self.current_quote_author = self._next_quote()
        def worker():
            quotes = MotivationService.fetch_english()
            if not quotes:
                return
            try:
                conn = sqlite3.connect(self.db.path)
                now = datetime.now().isoformat(timespec="seconds")
                for text, author in quotes:
                    conn.execute(
                        "INSERT OR IGNORE INTO quotes(text,author,language,source,seen,created) VALUES(?,?,?,?,0,?)",
                        (text,author,"English","Online",now)
                    )
                conn.commit()
                conn.close()
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _next_quote(self):
        lang = "English" if self.language == "English" else "فارسی"
        row = self.db.one("SELECT * FROM quotes WHERE language=? AND seen=0 ORDER BY RANDOM() LIMIT 1",(lang,))
        if not row:
            self.db.ex("UPDATE quotes SET seen=0 WHERE language=?",(lang,))
            row = self.db.one("SELECT * FROM quotes WHERE language=? ORDER BY RANDOM() LIMIT 1",(lang,))
        if not row:
            return self.tr("امروز یک قدم جلوتر برو.","Take one step forward today."), "AXT"
        self.db.ex("UPDATE quotes SET seen=1 WHERE id=?",(row["id"],))
        return str(row["text"]), str(row["author"] or "AXT")

    # ---------- dashboard ----------

    def show_dashboard(self):
        s, root = self.screen_layout("Dashboard","مرکز کنترل زندگی و پروژه‌ها")
        scroll = ScrollView()
        body = GridLayout(cols=1, spacing=dp(14), size_hint_y=None, padding=[0,0,dp(10),dp(20)])
        body.bind(minimum_height=body.setter("height"))

        today = date.today()
        sh = "-"
        if jdatetime:
            try:
                sh = jdatetime.date.fromgregorian(date=today).strftime("%Y/%m/%d")
            except Exception:
                pass

        c = Card(self); c.add_widget(self.label(f"TODAY  •  {today:%Y/%m/%d}   |   شمسی: {sh}",12,"muted"))
        body.add_widget(c)

        if self.quote_dashboard:
            c = Card(self)
            row = BoxLayout(size_hint_y=None,height=dp(35))
            row.add_widget(self.label("✦  "+self.tr("جمله انگیزشی","MOTIVATIONAL QUOTE"),14))
            row.add_widget(WidgetSpacer())
            row.add_widget(self.button("↻", self.refresh_quote, height=35))
            c.add_widget(row)
            c.add_widget(self.label(self.current_quote_text,20,"text", text_size=(None,None)))
            c.add_widget(self.label("— "+self.current_quote_author,12,"muted"))
            body.add_widget(c)

        if self.idea_dashboard:
            c = Card(self)
            c.add_widget(self.label("💡  "+self.tr("ایده امروز","TODAY'S IDEA"),14))
            c.add_widget(self.label(self._daily_idea(),17))
            body.add_widget(c)

        if self.routine_dashboard:
            c = Card(self)
            c.add_widget(self.label("✓  "+self.tr("روتین امروز","TODAY'S ROUTINE"),14))
            for row in self._ensure_daily_routine():
                line = BoxLayout(size_hint_y=None,height=dp(38))
                cb = CheckBox(active=bool(row["done"]), size_hint_x=None,width=dp(32))
                tx = self.label(row["item"],13)
                def sync(box, value, rid=row["id"]):
                    self.db.ex("UPDATE daily_routines SET done=? WHERE id=?",(int(value),rid))
                cb.bind(active=sync)
                line.add_widget(cb); line.add_widget(tx)
                c.add_widget(line)
            body.add_widget(c)

        if self.stats_dashboard:
            grid = GridLayout(cols=2 if Window.width < dp(850) else 4,
                              spacing=dp(12), size_hint_y=None)
            stats = [
                ("OPEN TASKS", self.db.one("SELECT COUNT(*) n FROM tasks WHERE done=0")["n"], "✓"),
                ("ROUTINES", self.db.one("SELECT COUNT(*) n FROM routines")["n"], "🔥"),
                ("GOALS", self.db.one("SELECT COUNT(*) n FROM goals")["n"], "◎"),
                ("MUSIC IDEAS", self.db.one("SELECT COUNT(*) n FROM music")["n"], "♫"),
            ]
            for lab,val,icon in stats:
                card=Card(self)
                card.add_widget(self.label(icon,22))
                card.add_widget(self.label(val,28))
                card.add_widget(self.label(lab,11,"muted"))
                grid.add_widget(card)
            grid.bind(minimum_height=grid.setter("height"))
            body.add_widget(grid)

        if self.calendar_dashboard or self.agenda_dashboard:
            grid=GridLayout(cols=1,spacing=dp(14),size_hint_y=None)
            grid.bind(minimum_height=grid.setter("height"))
            if self.calendar_dashboard:
                c=Card(self)
                c.add_widget(self.label(self.tr("تقویم","CALENDAR"),14))
                c.add_widget(self.calendar_widget())
                grid.add_widget(c)
            if self.agenda_dashboard:
                c=Card(self)
                c.add_widget(self.label("TODAY / UPCOMING",14))
                upcoming=self.db.all(
                    "SELECT title,due FROM tasks WHERE done=0 AND due IS NOT NULL AND due!='' ORDER BY due ASC LIMIT 8"
                )
                if not upcoming:
                    c.add_widget(self.label("No upcoming tasks.","12","muted"))
                for row in upcoming:
                    line=BoxLayout(size_hint_y=None,height=dp(34))
                    line.add_widget(self.label("☐  "+str(row["title"]),13))
                    line.add_widget(self.label(str(row["due"]),11,"muted",size_hint_x=.35))
                    c.add_widget(line)
                grid.add_widget(c)
            body.add_widget(grid)

        scroll.add_widget(body)
        root.add_widget(scroll)

    def refresh_quote(self):
        self.current_quote_text,self.current_quote_author=self._next_quote()
        self.show_dashboard()

    def calendar_widget(self):
        lay=GridLayout(cols=7,spacing=dp(3),size_hint_y=None)
        lay.bind(minimum_height=lay.setter("height"))
        if self.calendar_system=="Jalali" and jdatetime:
            now=jdatetime.date.today()
            y,m=now.year,now.month
            days=["ش","ی","د","س","چ","پ","ج"]
            for d in days: lay.add_widget(self.label(d,10,"muted",size_hint_y=None,height=dp(25)))
            first=jdatetime.date(y,m,1)
            start=(first.weekday()+2)%7
            for i in range(42):
                jd=first+timedelta(days=i-start)
                b=self.button(str(jd.day),height=34)
                lay.add_widget(b)
        else:
            now=date.today()
            import calendar
            days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            for d in days: lay.add_widget(self.label(d,9,"muted",size_hint_y=None,height=dp(24)))
            first=now.replace(day=1)
            start=first.weekday()
            for i in range(42):
                day=i-start+1
                txt=str(day) if 1<=day<=calendar.monthrange(now.year,now.month)[1] else ""
                lay.add_widget(self.button(txt,height=34) if txt else self.label("",12,size_hint_y=None,height=dp(34)))
        return lay

    # ---------- generic CRUD ----------

    @property
    def task_fields(self):
        return [("title","عنوان","text",""),("due","سررسید","text",date.today().isoformat())]
    @property
    def routine_fields(self):
        return [("title","روتین","text","")]
    @property
    def countdown_fields(self):
        return [("title","عنوان","text",""),("target","تاریخ YYYY-MM-DD","text",(date.today()+timedelta(days=7)).isoformat())]
    @property
    def lyrics_fields(self):
        return [("title","نام آهنگ","text",""),("status","وضعیت","combo",["Draft","Writing","Final","Released"]),
                ("genre","ژانر","text",""),("cover","کاور","text",""),("content","لیریک","memo","")]
    @property
    def notes_fields(self):
        return [("title","عنوان","text",""),("category","دسته","combo",["General","Personal","Work","Music","School","Ideas","Important"]),
                ("tags","تگ‌ها","text",""),("content","متن","memo","")]
    @property
    def youtube_fields(self):
        return [("title","عنوان","text",""),("channel","چنل","text",""),
                ("status","وضعیت","combo",["Idea","Script","Recording","Editing","Published"]),
                ("prompt","پرامپت","memo",""),("description","توضیحات","memo",""),("url","لینک","text","")]
    @property
    def location_fields(self):
        return [("name","نام مکان","text",""),("city","شهر","text",""),
                ("category","دسته","combo",["Travel","Restaurant","Cafe","Nature","Entertainment","Shopping","Other"]),
                ("address","آدرس","text",""),("url","لینک نقشه","text",""),("notes","یادداشت","memo","")]
    @property
    def goal_fields(self):
        return [("title","هدف","text",""),("description","توضیحات","memo",""),
                ("progress","پیشرفت","spin",0),("score","امتیاز","spin",0),
                ("deadline","مهلت","text",""),("sticker","استیکر","text","🎯")]
    @property
    def music_fields(self):
        return [("title","نام","text",""),("category","دسته","combo",["Beat","Vocal","Melody","Chord","Mix","Album"]),
                ("description","توضیحات","memo",""),("bpm","BPM","spin",0),("music_key","Key","text",""),
                ("genre","Genre","text",""),("mood","Mood","text","")]

    def form_popup(self, title, fields, row=None, on_save=None):
        scroll=ScrollView()
        form=GridLayout(cols=1,spacing=dp(7),padding=dp(14),size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        widgets={}
        for name,lab,typ,default in fields:
            form.add_widget(self.label(lab,12,"muted",size_hint_y=None,height=dp(28)))
            val = row[name] if row is not None and name in row.keys() else default
            if typ=="memo":
                x=self.input(val,True)
                x.size_hint_y=None; x.height=dp(120)
            elif typ=="combo":
                opts=list(default)
                x=Spinner(text=str(val or opts[0]),values=opts,size_hint_y=None,height=dp(42))
            elif typ=="spin":
                x=self.input(str(val or 0),False)
                x.input_filter="int"
                x.size_hint_y=None; x.height=dp(42)
            else:
                x=self.input(val,False)
                x.size_hint_y=None; x.height=dp(42)
            widgets[name]=x
            form.add_widget(x)
        buttons=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(8))
        save=self.button("✓ Save",height=44,kind="primary")
        cancel=self.button("Cancel",height=44)
        buttons.add_widget(save);buttons.add_widget(cancel);form.add_widget(buttons)
        scroll.add_widget(form)
        p=self.popup(title,scroll,size=(.94,.88))
        def values():
            out={}
            for name,x in widgets.items():
                if isinstance(x,TextInput):
                    out[name]=x.text
                elif isinstance(x,Spinner):
                    out[name]=x.text
                else:
                    out[name]=x.text
            return out
        def do_save(*_):
            v=values()
            if on_save: on_save(v)
            p.dismiss()
        save.bind(on_release=do_save)
        cancel.bind(on_release=lambda *_:p.dismiss())
        return p

    def show_crud(self,title,table,fields,display,icon=""):
        s,root=self.screen_layout(title)
        toolbar=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(7))
        add=self.button("＋  جدید",kind="primary",height=44)
        edit=self.button("✎  ویرایش",height=44)
        delete=self.button("🗑  حذف",kind="danger",height=44)
        search=self.input(hint="جستجو در این بخش")
        toolbar.add_widget(add);toolbar.add_widget(edit);toolbar.add_widget(delete);toolbar.add_widget(search)
        root.add_widget(toolbar)
        scroll=ScrollView()
        lst=GridLayout(cols=1,spacing=dp(6),size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))
        scroll.add_widget(lst);root.add_widget(scroll)

        selected={"id":None}
        cols=[x[0] for x in fields]

        def load(*_):
            lst.clear_widgets()
            term="%"+search.text.strip()+"%"
            where=" OR ".join(c+" LIKE ?" for c in cols)
            order="id DESC"
            if table=="locations":
                order="CASE WHEN city='تهران' THEN 0 WHEN city IN ('اصفهان','گیلان') THEN 1 WHEN city IN ('Toronto','Vancouver','Montreal','Alberta') THEN 2 ELSE 3 END,id ASC"
            rows=self.db.all(f"SELECT * FROM {table} WHERE {where} ORDER BY {order}",[term]*len(cols))
            for row in rows:
                text=f"{icon}  {row[display]}"
                if table=="music": text+=f"   •   {row['category'] or ''}"
                elif table in ("lyrics","youtube"): text+=f"   •   {row['status'] or ''}"
                elif table=="goals": text+=f"   •   {row['progress'] or 0}%"
                b=self.button(text,height=50)
                b.bind(on_release=lambda _b,rid=row["id"]: selected.update(id=rid))
                lst.add_widget(b)

        def add_item():
            def save(v):
                now=datetime.now().isoformat(timespec="seconds")
                payload={c:v[c] for c in cols}
                existing=self.db.all(f"PRAGMA table_info({table})")
                names={r["name"] for r in existing}
                for stamp in ("created","updated"):
                    if stamp in names and stamp not in payload: payload[stamp]=now
                ic=list(payload.keys())
                self.db.ex(f"INSERT INTO {table}({','.join(ic)}) VALUES({','.join('?' for _ in ic)})",[payload[c] for c in ic])
                load()
            self.form_popup("ایجاد مورد جدید",fields,on_save=save)

        def edit_item():
            rid=selected["id"]
            if not rid: return
            row=self.db.one(f"SELECT * FROM {table} WHERE id=?",(rid,))
            if not row: return
            def save(v):
                self.db.ex(f"UPDATE {table} SET {','.join(c+'=?' for c in cols)} WHERE id=?",
                           [v[c] for c in cols]+[rid])
                load()
            self.form_popup("ویرایش مورد",fields,row=row,on_save=save)

        def remove_item():
            rid=selected["id"]
            if not rid:return
            confirm=BoxLayout(orientation="vertical",padding=dp(15),spacing=dp(10))
            confirm.add_widget(self.label("این مورد حذف شود؟",16))
            yes=self.button("بله، حذف کن",kind="danger")
            no=self.button("انصراف")
            confirm.add_widget(yes);confirm.add_widget(no)
            p=self.popup("حذف",confirm,size=(.8,.4))
            yes.bind(on_release=lambda *_:(self.db.ex(f"DELETE FROM {table} WHERE id=?",(rid,)),p.dismiss(),load()))
            no.bind(on_release=lambda *_:p.dismiss())

        add.bind(on_release=lambda *_:add_item())
        edit.bind(on_release=lambda *_:edit_item())
        delete.bind(on_release=lambda *_:remove_item())
        search.bind(text=load)
        load()

    # ---------- music / recorder ----------

    def show_music(self):
        self.show_crud("Music","music",self.music_fields,"title","♫")
        s=self.sm.get_screen("current")
        root=s.children[0]
        # Insert recorder card above the CRUD toolbar.
        card=Card(self)
        card.add_widget(self.label("🎙  RECORDING STUDIO",15))
        status=self.label("Ready to record",12,"muted")
        row=BoxLayout(size_hint_y=None,height=dp(45),spacing=dp(8))
        start=self.button("●  Start Recording",kind="primary")
        stop=self.button("■  Stop"); stop.disabled=True
        openb=self.button("📂  Open Recordings")
        row.add_widget(start);row.add_widget(stop);row.add_widget(openb)
        card.add_widget(status);card.add_widget(row)
        card.add_widget(self.label("Files are saved in AXT_Office/Recordings.",11,"muted"))
        root.add_widget(card, index=max(0,len(root.children)-2))

        recdir=APP_DIR/"Recordings";recdir.mkdir(exist_ok=True)
        started=[None]

        def start_rec():
            if ANDROID:
                filename=recdir/f"recording_{datetime.now():%Y%m%d_%H%M%S}.3gp"
            else:
                filename=recdir/f"recording_{datetime.now():%Y%m%d_%H%M%S}.wav"
            try:
                self.audio_recorder.start(filename)
                started[0]=datetime.now()
                start.disabled=True;stop.disabled=False
                status.text="● Recording… 00:00"
                Clock.schedule_interval(update_timer,.25)
            except Exception as exc:
                status.text=f"Recorder error: {exc}"

        def update_timer(dt):
            if not started[0]: return
            elapsed=int((datetime.now()-started[0]).total_seconds())
            status.text=f"● Recording… {elapsed//60:02d}:{elapsed%60:02d}"

        def stop_rec():
            if not self.audio_recorder.running:return
            path=self.audio_recorder.stop()
            start.disabled=False;stop.disabled=True
            started[0]=None
            status.text=f"Saved: {Path(path).name}" if path else "Recording finished"

        def open_rec():
            self.choose_path(initial=str(recdir),save=False)

        start.bind(on_release=lambda *_:start_rec())
        stop.bind(on_release=lambda *_:stop_rec())
        openb.bind(on_release=lambda *_:open_rec())

    # ---------- search ----------

    def show_search(self):
        s,root=self.screen_layout("Search","جستجو در همه بخش‌ها")
        q=self.input(hint="عنوان، نام یا عبارت موردنظر")
        root.add_widget(q)
        scroll=ScrollView();lst=GridLayout(cols=1,spacing=dp(6),size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"));scroll.add_widget(lst);root.add_widget(scroll)
        sources=[("tasks","title","✓"),("routines","title","🔥"),("music","title","♫"),("lyrics","title","✎"),
                 ("notes","title","▤"),("youtube","title","▶"),("goals","title","◎"),("locations","name","⌖")]
        def run(*_):
            lst.clear_widgets()
            if not q.text.strip():return
            term="%"+q.text.strip()+"%"
            for table,col,icon in sources:
                for row in self.db.all(f"SELECT {col} FROM {table} WHERE {col} LIKE ? LIMIT 30",(term,)):
                    lst.add_widget(self.button(f"{icon}  [{table}]  {row[col]}",height=45))
        q.bind(text=run)

    # ---------- backup / restore ----------

    def choose_path(self, initial="", save=False, callback=None):
        if filechooser:
            try:
                if save:
                    filechooser.save_file(on_selection=lambda selection: callback(selection[0]) if selection and callback else None)
                else:
                    filechooser.open_file(on_selection=lambda selection: callback(selection[0]) if selection and callback else None)
                return
            except Exception:
                pass
        chooser=FileChooserListView(path=initial or str(APP_DIR), filters=["*.*"])
        box=BoxLayout(orientation="vertical")
        box.add_widget(chooser)
        row=BoxLayout(size_hint_y=None,height=dp(45))
        ok=self.button("انتخاب",kind="primary");cancel=self.button("انصراف")
        row.add_widget(ok);row.add_widget(cancel);box.add_widget(row)
        p=self.popup("انتخاب فایل",box,size=(.95,.9))
        ok.bind(on_release=lambda *_:(callback(chooser.selection[0]) if chooser.selection and callback else None,p.dismiss()))
        cancel.bind(on_release=lambda *_: p.dismiss())

    def show_backup(self):
        s,root=self.screen_layout("Backup","پشتیبان‌گیری و بازیابی امن اطلاعات")
        c=Card(self)
        c.add_widget(self.label("فایل پایگاه‌داده شامل تمام داده‌های AXT OFFICE و تنظیمات ذخیره‌شده است.",13))
        row=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(8))
        make=self.button("💾  ساخت Backup",kind="primary")
        restore=self.button("📂  Restore")
        row.add_widget(make);row.add_widget(restore);c.add_widget(row);root.add_widget(c)

        def make_backup():
            target=APP_DIR/f"AXT_Backup_{datetime.now():%Y%m%d_%H%M%S}.db"
            self.db.c.commit();shutil.copy2(self.db.path,target)
            self.info("Backup",f"Backup ساخته شد:\n{target}")
        def restore_backup(path):
            try:
                self.db.close();shutil.copy2(path,self.db.path);self.db=DB()
                self.load_preferences();self.apply_theme();self.show_dashboard()
            except Exception as exc:
                self.info("Restore error",str(exc))
        make.bind(on_release=lambda *_:make_backup())
        restore.bind(on_release=lambda *_:self.choose_path(callback=restore_backup))

    # ---------- settings ----------

    def show_settings(self):
        s,root=self.screen_layout("Settings","شخصی‌سازی کامل ظاهر، پس‌زمینه، زبان و امکانات داشبورد")
        scroll=ScrollView()
        form=GridLayout(cols=1,spacing=dp(14),size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        appearance=Card(self)
        appearance.add_widget(self.label("🎨  APPEARANCE",14))
        theme=Spinner(text=self.theme_name,values=list(THEMES.keys()),size_hint_y=None,height=dp(42))
        bg=Spinner(text=self.background_name,values=BACKGROUNDS,size_hint_y=None,height=dp(42))
        appearance.add_widget(self.label("Theme / تم",11,"muted"));appearance.add_widget(theme)
        appearance.add_widget(self.label("Background / بک‌گراند",11,"muted"));appearance.add_widget(bg)
        media=self.button("🖼  انتخاب GIF / Video")
        appearance.add_widget(media);form.add_widget(appearance)

        motion=Card(self);motion.add_widget(self.label("◐  OPACITY & MOTION",14))
        animated=CheckBox(active=self.background_enabled,size_hint_x=None,width=dp(35))
        effects=CheckBox(active=self.effects_enabled,size_hint_x=None,width=dp(35))
        motion.add_widget(self.check_row(animated,"Enable animated background"))
        motion.add_widget(self.check_row(effects,"Enable UI shadows and effects"))
        intensity=self.slider_row(motion,"Animation intensity",self.intensity,0,100)
        bgop=self.slider_row(motion,"Background opacity",self.background_opacity,10,100)
        panelop=self.slider_row(motion,"Panel opacity",self.panel_opacity,20,98)
        form.add_widget(motion)

        dash=Card(self);dash.add_widget(self.label("✨  DASHBOARD",14))
        qtog=CheckBox(active=self.quote_dashboard,size_hint_x=None,width=dp(35))
        itog=CheckBox(active=self.idea_dashboard,size_hint_x=None,width=dp(35))
        rtog=CheckBox(active=self.routine_dashboard,size_hint_x=None,width=dp(35))
        stog=CheckBox(active=self.stats_dashboard,size_hint_x=None,width=dp(35))
        ctog=CheckBox(active=self.calendar_dashboard,size_hint_x=None,width=dp(35))
        atog=CheckBox(active=self.agenda_dashboard,size_hint_x=None,width=dp(35))
        for cb,txt in [(qtog,self.tr("نمایش بخش جمله انگیزشی","Show motivational quote")),
                       (itog,self.tr("نمایش ایده تصادفی روز","Show random daily idea")),
                       (rtog,self.tr("نمایش چک‌لیست روتین روزانه","Show daily routine checklist")),
                       (stog,self.tr("نمایش کارت‌های آمار","Show stat cards")),
                       (ctog,self.tr("نمایش تقویم","Show calendar")),
                       (atog,self.tr("نمایش کارهای پیش‌رو","Show upcoming agenda"))]:
            dash.add_widget(self.check_row(cb,txt))
        form.add_widget(dash)

        general=Card(self);general.add_widget(self.label("🌍  GENERAL",14))
        lang=Spinner(text=self.language,values=["فارسی","English"],size_hint_y=None,height=dp(42))
        cal=Spinner(text=self.calendar_system,values=["Gregorian","Jalali"],size_hint_y=None,height=dp(42))
        general.add_widget(self.label("Language / زبان",11,"muted"));general.add_widget(lang)
        general.add_widget(self.label("Calendar / تقویم",11,"muted"));general.add_widget(cal);form.add_widget(general)

        custom=Card(self);custom.add_widget(self.label("🧪  CREATE YOUR THEME",14))
        name=self.input(hint="Theme name");custom.add_widget(name)
        swatches=GridLayout(cols=5,spacing=dp(8),size_hint_y=None)
        swatches.bind(minimum_height=swatches.setter("height"))
        color_keys=["bg","panel","panel2","text","muted","border","accent","accent2","input","glow"]
        color_values={}
        for key in color_keys:
            b=self.button(key,height=50)
            b.background_color=self.theme_rgba(key)
            color_values[key]=self.theme[key]
            b.bind(on_release=lambda _b,k=key:self.pick_color(k,b,color_values))
            swatches.add_widget(b)
        custom.add_widget(swatches)
        save_theme=self.button("💾  Save custom theme",kind="primary")
        custom.add_widget(save_theme);form.add_widget(custom)

        logos=Card(self);logos.add_widget(self.label("🖼  SECTION PNG LOGOS",14))
        for key in ["Dashboard","Tasks","Routines","Countdown","Music","Lyrics","Notes","YouTube","Locations","Goals","Search","Backup","Settings"]:
            row=BoxLayout(size_hint_y=None,height=dp(43),spacing=dp(8))
            row.add_widget(self.label(key,11))
            choose=self.button("Choose PNG",height=40)
            row.add_widget(choose)
            choose.bind(on_release=lambda *_k,k=key:self.choose_logo(k))
            logos.add_widget(row)
        form.add_widget(logos)

        save=self.button("✓  ذخیره همه تنظیمات",kind="primary",height=50);form.add_widget(save)
        scroll.add_widget(form);root.add_widget(scroll)

        theme.bind(text=lambda *_:self.preview_theme(theme.text))
        bg.bind(text=lambda *_:self.change_background(bg.text))
        animated.bind(active=lambda _,v:self.set_background_enabled(v))
        effects.bind(active=lambda _,v:self.set_effects(v))
        intensity.bind(value=lambda _,v:self.set_intensity(v))
        bgop.bind(value=lambda _,v:self.set_bg_opacity(v))
        panelop.bind(value=lambda _,v:self.set_panel_opacity(v))
        media.bind(on_release=lambda *_:self.choose_media_file())
        save_theme.bind(on_release=lambda *_:self.save_custom_theme(name,color_values,theme))
        save.bind(on_release=lambda *_:self.save_settings(lang,cal,qtog,itog,rtog,stog,ctog,atog))

    def check_row(self, cb, text):
        row=BoxLayout(size_hint_y=None,height=dp(40))
        row.add_widget(cb);row.add_widget(self.label(text,12));return row

    def slider_row(self, parent, label, value, mn, mx):
        row=BoxLayout(size_hint_y=None,height=dp(48))
        lab=self.label(f"{label}: {value}%",11,"muted",size_hint_x=.45)
        sl=Slider(min=mn,max=mx,value=value)
        row.add_widget(lab);row.add_widget(sl);parent.add_widget(row)
        sl.bind(value=lambda _,v:lab.__setattr__("text",f"{label}: {int(v)}%"))
        return sl

    def pick_color(self,key,button,values):
        cp=ColorPicker(color=self.rgba(values[key]))
        box=BoxLayout(orientation="vertical")
        box.add_widget(cp)
        ok=self.button("OK",kind="primary")
        box.add_widget(ok)
        p=self.popup(f"Choose {key}",box,size=(.9,.8))
        def done(*_):
            rgba=cp.color
            hx="#%02x%02x%02x"%(int(rgba[0]*255),int(rgba[1]*255),int(rgba[2]*255))
            values[key]=hx;button.background_color=rgba;p.dismiss()
        ok.bind(on_release=done)

    def preview_theme(self,name):
        if name in THEMES:
            self.theme_name=name;self.apply_theme()

    def change_background(self,name):
        self.background_name=name;self.apply_theme()

    def set_background_enabled(self,v):
        self.background_enabled=bool(v);self.apply_theme()
    def set_effects(self,v):
        self.effects_enabled=bool(v)
    def set_intensity(self,v):
        self.intensity=int(v);self.apply_theme()
    def set_bg_opacity(self,v):
        self.background_opacity=int(v);self.apply_theme()
    def set_panel_opacity(self,v):
        self.panel_opacity=int(v);self.apply_theme()

    def choose_media_file(self):
        def picked(path):
            self.custom_media_path=path;self.background_name="Custom Media";self.apply_theme()
        self.choose_path(callback=picked)

    def choose_logo(self,key):
        def picked(path):
            self.db.set_setting("logo_"+key,path)
        self.choose_path(callback=picked)

    def save_custom_theme(self,name_widget,values,theme_spinner):
        n=name_widget.text.strip()
        if not n:
            self.info("Theme","Enter a theme name.");return
        data=dict(values)
        data["danger"]=self.theme["danger"];data["success"]=self.theme["success"]
        THEMES[n]=data;self.custom_themes[n]=data
        self.db.set_setting("custom_themes",json.dumps(self.custom_themes,ensure_ascii=False))
        theme_spinner.values=list(THEMES.keys());theme_spinner.text=n
        self.theme_name=n;self.apply_theme()

    def save_settings(self,lang,cal,qtog,itog,rtog,stog,ctog,atog):
        self.language=lang.text;self.calendar_system=cal.text
        self.quote_dashboard=qtog.active;self.idea_dashboard=itog.active
        self.routine_dashboard=rtog.active;self.stats_dashboard=stog.active
        self.calendar_dashboard=ctog.active;self.agenda_dashboard=atog.active
        pairs={
            "theme":self.theme_name,"background":self.background_name,
            "background_enabled":int(self.background_enabled),
            "animation_intensity":self.intensity,"ui_effects":int(self.effects_enabled),
            "background_opacity":self.background_opacity,"panel_opacity":self.panel_opacity,
            "language":self.language,"calendar":self.calendar_system,
            "routine_dashboard":int(self.routine_dashboard),"idea_dashboard":int(self.idea_dashboard),
            "quote_dashboard":int(self.quote_dashboard),"stats_dashboard":int(self.stats_dashboard),
            "calendar_dashboard":int(self.calendar_dashboard),"agenda_dashboard":int(self.agenda_dashboard),
            "custom_media_path":self.custom_media_path,
        }
        for k,v in pairs.items():self.db.set_setting(k,v)
        self.apply_theme();self.show_dashboard()
        self.info("موفق","تنظیمات ذخیره شد.")

    # ---------- media ----------

    def show_media_preview(self,path):
        ext=Path(path).suffix.lower()
        box=FloatLayout()
        if ext==".gif":
            img=Image(source=path,allow_stretch=True,keep_ratio=True)
            box.add_widget(img)
        elif ext in {".mp4",".mov",".m4v",".webm",".avi",".mkv"}:
            vid=Video(source=path,state="play",options={"eos":"loop"})
            box.add_widget(vid)
        else:
            box.add_widget(self.label("Unsupported media format.",16))
        self.popup("Custom Media",box,size=(.95,.85))

    # ---------- helpers ----------

    def info(self,title,text):
        box=BoxLayout(orientation="vertical",padding=dp(14),spacing=dp(10))
        box.add_widget(self.label(text,13))
        ok=self.button("OK",kind="primary")
        box.add_widget(ok)
        p=self.popup(title,box,size=(.85,.5))
        ok.bind(on_release=lambda *_:p.dismiss())

    def on_stop(self):
        try:
            if self.audio_recorder.running:
                self.audio_recorder.stop()
        except Exception:
            pass
        try:
            self.db.close()
        except Exception:
            pass


class WidgetSpacer(Widget):
    pass


if __name__ == "__main__":
    AXTOfficeApp().run()
