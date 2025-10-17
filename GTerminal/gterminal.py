
# gterminal.py
import pygame, sys, os, datetime, math, time
from pygame.locals import *

pygame.init()
try:
    pygame.mixer.init()
except:
    pass

# Window
WIDTH, HEIGHT = 1200, 780
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GTerminal 1.0")
CLOCK = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont("consolas", 18)
BIG = pygame.font.SysFont("consolas", 28, bold=True)
SMALL = pygame.font.SysFont("consolas", 14)

# Asset paths
WALLPAPER_PATH = "wallpaper.jpg"   # or wallpaper.png
BOOT_SOUND = "boot.wav"            # optional
ICON_FOLDER = "icons"
SAVE_FOLDER = "saves"
os.makedirs(ICON_FOLDER, exist_ok=True)
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Colors
BG = (10, 10, 12)
PANEL = (28, 28, 34)
WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
TITLE_BG = (25, 90, 170)
WINDOW_BG = (250, 250, 250)
ICON_LABEL = (220, 220, 220)
EVENT_COLOR = (180, 180, 180)
GREEN = (0, 210, 120)
RED = (210, 70, 70)
ACCENT = (60, 160, 240)

# Terminal & event log
input_text = ""
event_log = ["Witaj w GTerminal 1.0. Wpisz: desktop=launch//"]
LOG_LIMIT = 300
def add_event(s):
    event_log.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {s}")
    if len(event_log) > LOG_LIMIT:
        event_log.pop(0)

# Wallpaper loader
def load_wallpaper(path, size):
    if not os.path.exists(path):
        add_event(f"Brak pliku tapety: {path} (włóż wallpaper.jpg obok skryptu).")
        return None
    try:
        img = pygame.image.load(path)
        try:
            img = img.convert_alpha()
        except:
            img = img.convert()
        img = pygame.transform.smoothscale(img, size)
        add_event(f"Tapeta załadowana: {path}")
        return img
    except Exception as e:
        add_event(f"Błąd ładowania tapety: {e}")
        return None

WALLPAPER = load_wallpaper(WALLPAPER_PATH, (WIDTH, HEIGHT))

# Boot sound loader
def try_load_sound(path):
    if not os.path.exists(path):
        add_event(f"Brak pliku dźwięku boot: {path} (opcjonalny)")
        return None
    try:
        snd = pygame.mixer.Sound(path)
        add_event("Dźwięk boot załadowany")
        return snd
    except Exception as e:
        add_event(f"Nie można załadować dźwięku: {e}")
        return None

BOOT_SOUND_OBJ = try_load_sound(BOOT_SOUND)

# Desktop window (windowed desktop)
desktop_open = False
desktop_window = {
    "rect": pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 220),
    "title": "Pulpit",
    "state": "normal",
    "drag": False
}

# Start menu
start_menu_open = False

# Icons
ICON_SIZE = (48, 48)
ICON_GAP_Y = 84
ICON_X = 24
ICON_START_Y = 50

DEFAULT_ICONS = [
    {"name": "notepad.gat", "base": "notepad"},
    {"name": "paint.gat", "base": "paint"},
    {"name": "calc.gat", "base": "calc"},
    {"name": "trashbin.gat", "base": "trashbin"},
    {"name": "clock.gat", "base": "clock"},
]

def load_icon_image(base_name):
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(ICON_FOLDER, base_name + ext)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
            except:
                img = pygame.image.load(p).convert()
            return pygame.transform.smoothscale(img, ICON_SIZE)
    return None

def build_icons_list():
    lst = []
    dx = ICON_X
    dy = ICON_START_Y
    for item in DEFAULT_ICONS:
        lst.append({
            "name": item["name"],
            "img": load_icon_image(item["base"]),
            "pos": (dx, dy),   # relative to desktop content
            "rect": None,
            "is_file": False,
            "path": None
        })
        dy += ICON_GAP_Y
    return lst

DESKTOP_ICONS = build_icons_list()

# Window manager
windows = {}
z_counter = 1
active_window = None
dragging_win = None
drag_offset = (0,0)

def create_window(id_name, title, rect, app_type):
    global z_counter, active_window
    windows[id_name] = {
        "id": id_name,
        "title": title,
        "rect": pygame.Rect(rect),
        "type": app_type,
        "z": z_counter,
        "state": "normal",
        "content": {}
    }
    z_counter += 1
    active_window = id_name
    add_event(f"Uruchomiono {title}")

def bring_to_front(win_id):
    global z_counter, active_window
    if win_id in windows:
        windows[win_id]["z"] = z_counter
        z_counter += 1
        active_window = win_id

def close_window(win_id):
    if win_id in windows:
        add_event(f"Zamknięto {windows[win_id]['title']}")
        del windows[win_id]

def minimize_window(win_id):
    if win_id in windows:
        windows[win_id]["state"] = "minimized"
        add_event(f"Zminimalizowano {windows[win_id]['title']}")

def toggle_maximize(win_id):
    if win_id in windows:
        w = windows[win_id]
        w["state"] = "maximized" if w["state"] != "maximized" else "normal"
        add_event(f"Zmieniono stan {w['title']} -> {w['state']}")

# App initializers
def launch_notepad(filename=None):
    if "notepad" not in windows:
        create_window("notepad", "notepad.gat", (200, 150, 640, 460), "notepad")
        w = windows["notepad"]
        w["content"]["text"] = w["content"].get("text", "")
        if filename:
            w["content"]["filename"] = filename
            # if file exists, load it
            if os.path.exists(os.path.join(SAVE_FOLDER, filename)):
                try:
                    with open(os.path.join(SAVE_FOLDER, filename), "r", encoding="utf-8") as f:
                        w["content"]["text"] = f.read()
                except:
                    pass
        else:
            w["content"]["filename"] = w["content"].get("filename", "notatka.txt")
    else:
        bring_to_front("notepad")

def launch_paint():
    if "paint" not in windows:
        create_window("paint", "paint.gat", (240, 170, 660, 480), "paint")
        w = windows["paint"]
        w["content"]["lines"] = w["content"].get("lines", [])
        w["content"]["drawing"] = False
    else:
        bring_to_front("paint")

def launch_calc():
    if "calc" not in windows:
        create_window("calc", "calc.gat", (420, 200, 360, 340), "calc")
        w = windows["calc"]
        w["content"]["expr"] = ""
        w["content"]["result"] = ""
    else:
        bring_to_front("calc")

def launch_trash():
    if "trash" not in windows:
        create_window("trash", "trashbin.gat", (480, 220, 380, 320), "trash")
        w = windows["trash"]
        w["content"]["items"] = w["content"].get("items", [])
    else:
        bring_to_front("trash")

def launch_clock():
    if "clock" not in windows:
        create_window("clock", "clock.gat", (100, 220, 260, 160), "clock")
    else:
        bring_to_front("clock")

# Terminal interpreter (with version command)
def execute_command(cmd):
    global desktop_open
    cmd = cmd.strip()
    if not cmd:
        return
    # version command
    if cmd == '//gterminal version//':
        add_event("Current version (1.0.0) (GTerminal 1.0.0)")
        return
    if cmd.startswith("print =="):
        if "(" in cmd and ")" in cmd:
            inner = cmd.split("(",1)[1].rsplit(")",1)[0].strip()
            if (inner.startswith('"') and inner.endswith('"')) or (inner.startswith("'") and inner.endswith("'")):
                inner = inner[1:-1]
            add_event(inner)
        else:
            add_event("Błąd składni print.")
        return
    if cmd == 'desktop=launch//':
        if not desktop_open:
            boot_desktop_animation()
        else:
            add_event("Pulpit już uruchomiony.")
        return
    if cmd.startswith('launch =='):
        if '"' in cmd:
            name = cmd.split('"')[1]
        elif "'" in cmd:
            name = cmd.split("'")[1]
        else:
            add_event("Błąd składni launch.")
            return
        if name == "notepad.gat": launch_notepad()
        elif name == "paint.gat": launch_paint()
        elif name == "calc.gat": launch_calc()
        elif name == "trashbin.gat": launch_trash()
        elif name == "clock.gat": launch_clock()
        else:
            add_event(f"Nieznana aplikacja: {name}")
        return
    if cmd.startswith('wallpaper =='):
        if '"' in cmd:
            fname = cmd.split('"')[1]
        else:
            add_event("Błąd składni wallpaper.")
            return
        global WALLPAPER_PATH, WALLPAPER
        if os.path.exists(fname):
            WALLPAPER_PATH = fname
            WALLPAPER = load_wallpaper(WALLPAPER_PATH, (WIDTH, HEIGHT))
            add_event(f"Tapeta zmieniona na {fname}")
        else:
            add_event(f"Plik tapety nie istnieje: {fname}")
        return
    add_event(f"Nieznana komenda: {cmd}")

# Advanced boot animation
def boot_desktop_animation():
    global desktop_open, WALLPAPER
    desktop_open = True
    add_event("Rozpoczynam boot pulpitu...")
    if BOOT_SOUND_OBJ:
        try:
            BOOT_SOUND_OBJ.play()
        except:
            pass
    logo_text = "GTerminal"
    anim_start = pygame.time.get_ticks()
    duration = 2200
    particles = []
    for i in range(100):
        angle = i * (2*math.pi/100)
        speed = 1 + (i % 6)
        particles.append({"x": WIDTH//2, "y": HEIGHT//2 - 40, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": 60 + (i%80)})
    progress = 0.0
    pb_w = WIDTH * 0.6
    pb_h = 22
    pb_x = (WIDTH - pb_w)//2
    pb_y = HEIGHT//2 + 80
    while True:
        dt = CLOCK.tick(60)
        elapsed = pygame.time.get_ticks() - anim_start
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
        SCREEN.fill(BLACK)
        glow_radius = 80 + int(20 * math.sin(elapsed/180.0))
        pygame.draw.circle(SCREEN, (20,40,80), (WIDTH//2, HEIGHT//2 - 40), glow_radius)
        for p in particles:
            if p["life"] > 0:
                p["x"] += p["vx"] * (dt/16)
                p["y"] += p["vy"] * (dt/16)
                p["vy"] += 0.06 * (dt/16)
                p["life"] -= 1 * (dt/16)
                alpha = max(0, min(255, int(255 * (p["life"]/140.0))))
                surf = pygame.Surface((6,6), SRCALPHA); surf.fill((ACCENT[0],ACCENT[1],ACCENT[2],alpha))
                SCREEN.blit(surf, (p["x"], p["y"]))
        total_chars = len(logo_text)
        chars_to_show = int(total_chars * min(1.0, elapsed / duration))
        logo_surface = BIG.render(logo_text[:max(1, chars_to_show)], True, WHITE)
        logo_rect = logo_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        SCREEN.blit(logo_surface, logo_rect.topleft)
        dots = int((elapsed / 300) % 4)
        dots_text = "." * dots
        dot_surf = FONT.render(dots_text, True, WHITE)
        SCREEN.blit(dot_surf, (logo_rect.right + 6, logo_rect.y + 6))
        progress = min(100.0, progress + (dt/40.0) + (math.sin(elapsed/400.0)*0.2))
        pygame.draw.rect(SCREEN, (50,50,60), (pb_x-2, pb_y-2, pb_w+4, pb_h+4))
        pygame.draw.rect(SCREEN, (90,90,110), (pb_x, pb_y, pb_w, pb_h))
        inner_w = int(pb_w * (progress/100.0))
        pygame.draw.rect(SCREEN, GREEN, (pb_x, pb_y, inner_w, pb_h))
        status = "Inicjalizowanie..."
        if progress > 10: status = "Ładowanie sterowników..."
        if progress > 35: status = "Inicjalizacja pulpitu..."
        if progress > 60: status = "Ładowanie ikon..."
        if progress > 85: status = "Finalizowanie..."
        SCREEN.blit(FONT.render(status, True, (200,200,200)), (pb_x, pb_y + pb_h + 8))
        pygame.display.flip()
        if progress >= 100.0:
            pygame.time.delay(400)
            break
    r = desktop_window["rect"]
    content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
    if WALLPAPER:
        wp = pygame.transform.smoothscale(WALLPAPER, (content.width, content.height)).convert()
        for a in range(0,256,8):
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit(); sys.exit()
            SCREEN.fill(BLACK)
            pygame.draw.rect(SCREEN, WINDOW_BG, r)
            pygame.draw.rect(SCREEN, TITLE_BG, (r.x, r.y, r.width, 32))
            SCREEN.blit(BIG.render(desktop_window["title"], True, WHITE), (r.x + 8, r.y + 6))
            surf = wp.copy(); surf.set_alpha(a)
            SCREEN.blit(surf, (content.x, content.y))
            pygame.display.flip()
            CLOCK.tick(60)
        add_event("Boot zakończony.")
    else:
        add_event("Boot zakończony (brak tapety).")

# Shutdown animation (fade out + shrinking logo)
def shutdown_animation_and_exit():
    add_event("Uruchamiam zamykanie systemu...")
    start = pygame.time.get_ticks()
    duration = 900
    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start
        t = min(1.0, elapsed / duration)
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
        SCREEN.fill(BLACK)
        size = int(200 * (1 - t))
        if size < 10: size = 10
        s = pygame.Surface((size, size), SRCALPHA)
        s.fill((0,0,0,0))
        pygame.draw.circle(s, (ACCENT[0], ACCENT[1], ACCENT[2], int(200*(1-t))), (size//2, size//2), size//2)
        SCREEN.blit(s, (WIDTH//2 - size//2, HEIGHT//2 - size//2))
        alpha = int(255 * (1 - t))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(alpha)
        SCREEN.blit(overlay, (0,0))
        pygame.display.flip()
        CLOCK.tick(60)
        if t >= 1.0:
            break
    pygame.time.delay(200)
    pygame.quit()
    sys.exit()

# Drawing helpers
def draw_terminal_area():
    pygame.draw.rect(SCREEN, PANEL, (0, HEIGHT - 48, WIDTH, 48))
    txt = FONT.render("> " + input_text, True, GREEN)
    SCREEN.blit(txt, (12, HEIGHT - 36))
    hint = SMALL.render("Enter aby wykonać | Komendy: desktop=launch//, launch == \"app.gat\"//, wallpaper == \"file.jpg\"//, //gterminal version//", True, (140,140,140))
    SCREEN.blit(hint, (12, HEIGHT - 20))

def draw_event_log():
    rect = pygame.Rect(8, 8, WIDTH - 16, HEIGHT - 160)
    pygame.draw.rect(SCREEN, (14,14,18), rect)
    y = rect.y + 8
    lines = event_log[-(rect.height//18 - 2):]
    for line in lines:
        SCREEN.blit(SMALL.render(line, True, EVENT_COLOR), (rect.x + 8, y))
        y += 18

def draw_desktop_window():
    global start_menu_open
    r = desktop_window["rect"]
    pygame.draw.rect(SCREEN, WINDOW_BG, r)
    pygame.draw.rect(SCREEN, TITLE_BG, (r.x, r.y, r.width, 32))
    SCREEN.blit(FONT.render(desktop_window["title"], True, WHITE), (r.x + 8, r.y + 6))
    close_rect = pygame.Rect(r.x + r.width - 34, r.y + 6, 26, 20)
    pygame.draw.rect(SCREEN, (220,80,80), close_rect)
    SCREEN.blit(FONT.render("X", True, WHITE), (close_rect.x + 7, close_rect.y + 1))
    content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
    if WALLPAPER:
        wp = pygame.transform.smoothscale(WALLPAPER, (content.width, content.height))
        SCREEN.blit(wp, (content.x, content.y))
    else:
        pygame.draw.rect(SCREEN, (10,20,40), content)
    for icon in DESKTOP_ICONS:
        ix = content.x + int(icon["pos"][0])
        iy = content.y + int(icon["pos"][1])
        rect_icon = pygame.Rect(ix, iy, ICON_SIZE[0], ICON_SIZE[1])
        icon["rect"] = rect_icon
        if icon["img"]:
            SCREEN.blit(icon["img"], (ix, iy))
        else:
            pygame.draw.rect(SCREEN, (200,200,200), rect_icon)
            SCREEN.blit(FONT.render("?", True, BLACK), (ix+14, iy+8))
        label_x = ix + ICON_SIZE[0] + 8
        label_y = iy + (ICON_SIZE[1] - FONT.get_height())//2
        SCREEN.blit(SMALL.render(icon["name"], True, ICON_LABEL), (label_x, label_y))
    # Start button bottom-left inside desktop
    sb_x = r.x + 10
    sb_y = r.y + r.height - 36
    sb_w, sb_h = 140, 28
    start_btn_rect = pygame.Rect(sb_x, sb_y, sb_w, sb_h)
    pygame.draw.rect(SCREEN, (40,40,48), start_btn_rect)
    SCREEN.blit(SMALL.render("Start", True, WHITE), (sb_x + 12, sb_y + 6))
    # If start menu open render it
    if start_menu_open:
        sm_w, sm_h = 260, 260
        sm_x = r.x + 10
        sm_y = sb_y - sm_h - 8
        start_menu_rect = pygame.Rect(sm_x, sm_y, sm_w, sm_h)
        pygame.draw.rect(SCREEN, (22,22,28), start_menu_rect)
        pygame.draw.rect(SCREEN, (60,60,70), (sm_x, sm_y, sm_w, 28))
        SCREEN.blit(SMALL.render("Start Menu", True, WHITE), (sm_x + 10, sm_y + 6))
        items = [
            ("Notatnik", lambda: launch_notepad()),
            ("Paint", lambda: launch_paint()),
            ("Kalkulator", lambda: launch_calc()),
            ("Trash", lambda: launch_trash()),
            ("Create text file", "create_text"),
            ("Zmień tapetę", None),
            ("Wyłącz", "shutdown"),
        ]
        iy = sm_y + 40
        for i, it in enumerate(items):
            label = it[0]
            rect_item = pygame.Rect(sm_x + 8, iy, sm_w - 16, 34)
            pygame.draw.rect(SCREEN, (30,30,36), rect_item)
            SCREEN.blit(SMALL.render(label, True, (220,220,220)), (rect_item.x + 8, rect_item.y + 6))
            iy += 40

def draw_app_windows():
    ordered = sorted(windows.values(), key=lambda w: w["z"])
    for w in ordered:
        if w["state"] == "minimized": continue
        if w["state"] == "maximized":
            r = pygame.Rect(6, 46, WIDTH - 12, HEIGHT - 210)
        else:
            r = w["rect"]
        pygame.draw.rect(SCREEN, WINDOW_BG, r)
        pygame.draw.rect(SCREEN, TITLE_BG, (r.x, r.y, r.width, 30))
        SCREEN.blit(FONT.render(w["title"], True, WHITE), (r.x + 8, r.y + 6))
        bx = r.x + r.width - 100
        pygame.draw.rect(SCREEN, (200,200,200), (bx, r.y + 6, 24, 18))
        pygame.draw.rect(SCREEN, (200,200,200), (bx+30, r.y + 6, 24, 18))
        pygame.draw.rect(SCREEN, (240,90,90), (bx+60, r.y + 6, 24, 18))
        SCREEN.blit(FONT.render("_", True, BLACK), (bx+8, r.y + 5))
        SCREEN.blit(FONT.render("□", True, BLACK), (bx+38, r.y + 5))
        SCREEN.blit(FONT.render("X", True, WHITE), (bx+68, r.y + 5))
        content = pygame.Rect(r.x+8, r.y+36, r.width-16, r.height-44)
        pygame.draw.rect(SCREEN, (245,245,245), content)
        if w["type"] == "notepad": draw_notepad(w, content)
        elif w["type"] == "paint": draw_paint(w, content)
        elif w["type"] == "calc": draw_calc(w, content)
        elif w["type"] == "trash": draw_trash(w, content)
        elif w["type"] == "clock": draw_clock_app(w, content)

# Notepad
def draw_notepad(w, area):
    pygame.draw.rect(SCREEN, (255,255,250), area)
    fn = w["content"].get("filename", "notatka.txt")
    SCREEN.blit(SMALL.render(f"Plik: {fn}", True, (80,80,80)), (area.x+6, area.y+6))
    lines = w["content"].get("text", "").split("\n")
    max_lines = max(1, area.height // 18 - 2)
    for i, line in enumerate(lines[-max_lines:]):
        SCREEN.blit(SMALL.render(line, True, BLACK), (area.x+6, area.y+30 + i*18))

def save_notepad(w):
    name = w["content"].get("filename", "notatka.txt")
    safe_name = name.replace("/", "_").replace("\\", "_")
    path = os.path.join(SAVE_FOLDER, safe_name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(w["content"].get("text", ""))
        add_event(f"Zapisano {safe_name} do saves/")
        # add file icon to desktop (first free x)
        px = 300 + (len([i for i in DESKTOP_ICONS if i.get("is_file")]) * 64)
        # clamp px so icon stays inside desktop area (will be re-clamped on render)
        FILE_ICON = {"name": safe_name, "img": None, "pos": (px, 60), "rect": None, "is_file": True, "path": path}
        DESKTOP_ICONS.append(FILE_ICON)
    except Exception as e:
        add_event(f"Błąd zapisu: {e}")

# Create text file helper (automatic unique name) and add icon + open notepad with file
def create_text_file(filename=None):
    # generate unique name if not provided
    base = filename or f"new_file"
    counter = 1
    name = base + ".txt"
    while os.path.exists(os.path.join(SAVE_FOLDER, name)):
        counter += 1
        name = f"{base}_{counter}.txt"
    path = os.path.join(SAVE_FOLDER, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")  # empty file
        add_event(f"Utworzono plik {name} w saves/")
        px = 300 + (len([i for i in DESKTOP_ICONS if i.get("is_file")]) * 64)
        FILE_ICON = {"name": name, "img": None, "pos": (px, 60), "rect": None, "is_file": True, "path": path}
        DESKTOP_ICONS.append(FILE_ICON)
        # open notepad with this file
        launch_notepad(filename=name)
    except Exception as e:
        add_event(f"Błąd tworzenia pliku: {e}")

# Paint
def draw_paint(w, area):
    pygame.draw.rect(SCREEN, (255,255,255), area)
    for seg in w["content"].get("lines", []):
        pygame.draw.line(SCREEN, BLACK, seg[0], seg[1], seg[2])

# Calc
def draw_calc(w, area):
    pygame.draw.rect(SCREEN, (245,245,245), area)
    expr = w["content"].get("expr", "")
    res = w["content"].get("result", "")
    SCREEN.blit(SMALL.render("Wyrażenie:", True, (80,80,80)), (area.x+8, area.y+8))
    SCREEN.blit(SMALL.render(expr, True, BLACK), (area.x+8, area.y+36))
    SCREEN.blit(SMALL.render("Wynik:", True, (80,80,80)), (area.x+8, area.y+72))
    SCREEN.blit(SMALL.render(res, True, BLACK), (area.x+8, area.y+100))

# Trash
def draw_trash(w, area):
    pygame.draw.rect(SCREEN, (250,250,250), area)
    SCREEN.blit(SMALL.render("Kosz (trashbin.gat):", True, (80,80,80)), (area.x+6, area.y+6))
    items = w["content"].get("items", [])
    for i, it in enumerate(items[-(area.height//18 - 2):]):
        SCREEN.blit(SMALL.render(f"- {it}", True, BLACK), (area.x+8, area.y+30 + i*18))

# Clock
def draw_clock_app(w, area):
    pygame.draw.rect(SCREEN, (235,235,255), area)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    SCREEN.blit(BIG.render(now, True, BLACK), (area.x+20, area.y+30))

# Utility: topmost window at pos
def top_window_at(pos):
    top = None; top_z = -1
    for w in windows.values():
        r = w["rect"] if w["state"] != "maximized" else pygame.Rect(6,46,WIDTH-12,HEIGHT-210)
        if r.collidepoint(pos) and w["z"] > top_z:
            top = w; top_z = w["z"]
    return top

# Active window input
def handle_key_for_window(event):
    global input_text
    if active_window is None or active_window not in windows: return False
    w = windows[active_window]
    if w["state"] == "minimized": return False
    if w["type"] == "notepad":
        if event.key == K_BACKSPACE:
            t = w["content"].get("text",""); w["content"]["text"] = t[:-1]
        elif event.key == K_RETURN:
            w["content"]["text"] += "\n"
        elif event.key == K_s and (pygame.key.get_mods() & KMOD_CTRL):
            save_notepad(w)
        elif event.unicode:
            w["content"]["text"] += event.unicode
        return True
    if w["type"] == "calc":
        if event.key == K_BACKSPACE:
            w["content"]["expr"] = w["content"]["expr"][:-1]
        elif event.key == K_RETURN:
            expr = w["content"]["expr"]
            try:
                allowed = "0123456789+-*/(). "
                if all(c in allowed for c in expr):
                    w["content"]["result"] = str(eval(expr))
                else:
                    w["content"]["result"] = "Błąd: niedozwolone znaki"
            except:
                w["content"]["result"] = "Błąd"
        elif event.unicode:
            w["content"]["expr"] += event.unicode
        return True
    return False

# Drag file/icon handling
dragging_icon = None
dragging_icon_offset = (0,0)
moving_icon = None
moving_icon_offset = (0,0)

# Helper: clamp icon relative pos to desktop content bounds
def clamp_icon_pos(rel_x, rel_y):
    r = desktop_window["rect"]
    content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
    max_x = max(0, content.width - ICON_SIZE[0])
    max_y = max(0, content.height - ICON_SIZE[1])
    nx = int(max(0, min(max_x, rel_x)))
    ny = int(max(0, min(max_y, rel_y)))
    return nx, ny

# Main loop
running = True
while running:
    SCREEN.fill(BG)
    mouse_pos = pygame.mouse.get_pos()

    # event log area background
    pygame.draw.rect(SCREEN, (12,12,16), (6,6, WIDTH-12, HEIGHT-160))
    draw_event_log()

    # desktop
    if desktop_open:
        draw_desktop_window()

    # apps
    draw_app_windows()

    # terminal
    draw_terminal_area()
    SCREEN.blit(SMALL.render("Start: kliknij Start (w oknie pulpitu). Ctrl+S w notatniku zapisuje plik na pulpicie. Przeciągnij ikonę pliku do Trash.", True, (150,150,150)), (12, HEIGHT-64))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if handle_key_for_window(event):
                pass
            else:
                if event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == K_RETURN:
                    cmd = input_text.strip(); execute_command(cmd); input_text = ""
                else:
                    if event.unicode:
                        input_text += event.unicode

        elif event.type == MOUSEBUTTONDOWN:
            pos = event.pos
            # desktop interactions
            if desktop_open:
                r = desktop_window["rect"]
                close_rect = pygame.Rect(r.x + r.width - 34, r.y + 6, 26, 20)
                title_rect = pygame.Rect(r.x, r.y, r.width, 32)
                content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
                sb_x = r.x + 10; sb_y = r.y + r.height - 36; sb_w, sb_h = 140, 28
                start_rect_local = pygame.Rect(sb_x, sb_y, sb_w, sb_h)
                if close_rect.collidepoint(pos):
                    desktop_open = False; add_event("Pulpit zamknięty.")
                    start_menu_open = False
                elif title_rect.collidepoint(pos):
                    desktop_window["drag"] = True
                    drag_dx = pos[0] - r.x; drag_dy = pos[1] - r.y
                    drag_offset = (drag_dx, drag_dy)
                elif start_rect_local.collidepoint(pos):
                    start_menu_open = not start_menu_open
                elif start_menu_open:
                    sm_w, sm_h = 260, 260
                    sm_x = r.x + 10; sm_y = sb_y - sm_h - 8
                    sm_rect = pygame.Rect(sm_x, sm_y, sm_w, sm_h)
                    if sm_rect.collidepoint(pos):
                        items = ["Notatnik","Paint","Kalkulator","Trash","Create text file","Zmień tapetę","Wyłącz"]
                        local_y = pos[1] - (sm_y + 40)
                        idx = local_y // 40
                        if 0 <= idx < len(items):
                            choice = items[idx]
                            if choice == "Notatnik": launch_notepad()
                            elif choice == "Paint": launch_paint()
                            elif choice == "Kalkulator": launch_calc()
                            elif choice == "Trash": launch_trash()
                            elif choice == "Create text file":
                                # create new empty file and open it
                                create_text_file()
                            elif choice == "Zmień tapetę":
                                add_event("Użyj komendy: wallpaper == \"ścieżka/do/plik.jpg\"//")
                            elif choice == "Wyłącz":
                                shutdown_animation_and_exit()
                        start_menu_open = False
                    else:
                        start_menu_open = False
                elif content.collidepoint(pos):
                    # check icons (files and apps), support moving icons
                    # iterate reversed to pick top-most visually
                    for icon in reversed(DESKTOP_ICONS):
                        ir = icon.get("rect")
                        if ir and ir.collidepoint(pos):
                            if icon.get("is_file"):
                                dragging_icon = icon
                                dragging_icon_offset = (pos[0]-ir.x, pos[1]-ir.y)
                            else:
                                # start moving icon (left click and hold)
                                moving_icon = icon
                                moving_icon_offset = (pos[0] - ir.x, pos[1] - ir.y)
                            # single click launches non-file icons
                            if not icon.get("is_file"):
                                name = icon["name"]
                                if name == "notepad.gat": launch_notepad()
                                elif name == "paint.gat": launch_paint()
                                elif name == "calc.gat": launch_calc()
                                elif name == "trashbin.gat": launch_trash()
                                elif name == "clock.gat": launch_clock()
                            break
            # app windows interactions
            top = top_window_at(pos)
            if top:
                bring_to_front(top["id"])
                r = top["rect"] if top["state"] != "maximized" else pygame.Rect(6,46,WIDTH-12,HEIGHT-210)
                titlebar = pygame.Rect(r.x, r.y, r.width, 30)
                bx = r.x + r.width - 100
                min_rect = pygame.Rect(bx, r.y + 6, 24, 18)
                max_rect = pygame.Rect(bx+30, r.y + 6, 24, 18)
                close_rect = pygame.Rect(bx+60, r.y + 6, 24, 18)
                if close_rect.collidepoint(pos):
                    close_window(top["id"])
                elif min_rect.collidepoint(pos):
                    minimize_window(top["id"])
                elif max_rect.collidepoint(pos):
                    toggle_maximize(top["id"])
                elif titlebar.collidepoint(pos) and top["state"] != "maximized":
                    dragging_win = top["id"]
                    drag_offset = (pos[0] - r.x, pos[1] - r.y)
                else:
                    if top["type"] == "paint":
                        area = pygame.Rect(r.x+8, r.y+36, r.width-16, r.height-44)
                        if area.collidepoint(pos):
                            top["content"]["drawing"] = True
                            top["content"]["last"] = pos

        elif event.type == MOUSEBUTTONUP:
            dragging_win = None
            desktop_window["drag"] = False
            # finish moving icons
            if moving_icon:
                # clamp position so icon stays inside desktop content
                r = desktop_window["rect"]; content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
                rel_x = moving_icon["pos"][0]; rel_y = moving_icon["pos"][1]
                nx, ny = clamp_icon_pos(rel_x, rel_y)
                moving_icon["pos"] = (nx, ny)
                moving_icon = None
            # finish dragging files (drop to trash)
            if dragging_icon:
                dropped = False
                if "trash" in windows:
                    tr = windows["trash"]
                    tr_rect = tr["rect"] if tr["state"] != "maximized" else pygame.Rect(6,46,WIDTH-12,HEIGHT-210)
                    if tr_rect.collidepoint(event.pos):
                        tr["content"].setdefault("items", []).append(dragging_icon["name"])
                        try: DESKTOP_ICONS.remove(dragging_icon)
                        except: pass
                        add_event(f"Przeniesiono {dragging_icon['name']} do kosza")
                        dropped = True
                if not dropped:
                    # clamp back into desktop if dropped outside
                    r = desktop_window["rect"]; content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
                    rel_x = dragging_icon["pos"][0]; rel_y = dragging_icon["pos"][1]
                    nx, ny = clamp_icon_pos(rel_x, rel_y)
                    dragging_icon["pos"] = (nx, ny)
                    add_event(f"Upuszczono {dragging_icon.get('name')}")
                dragging_icon = None
            for w in windows.values():
                if w["type"] == "paint":
                    w["content"]["drawing"] = False

        elif event.type == MOUSEMOTION:
            pos = event.pos
            if desktop_window.get("drag"):
                r = desktop_window["rect"]
                r.x = pos[0] - drag_offset[0]; r.y = pos[1] - drag_offset[1]
            if 'dragging_win' in locals() and dragging_win and dragging_win in windows:
                w = windows[dragging_win]
                if w["state"] != "maximized":
                    w["rect"].x = pos[0] - drag_offset[0]; w["rect"].y = pos[1] - drag_offset[1]
            # moving icon position while left button held on icon (reposition)
            if moving_icon and pygame.mouse.get_pressed()[0]:
                r = desktop_window["rect"]; content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
                new_rel_x = pos[0] - content.x - moving_icon_offset[0]
                new_rel_y = pos[1] - content.y - moving_icon_offset[1]
                # clamp while dragging so icon never moves outside content
                nx, ny = clamp_icon_pos(new_rel_x, new_rel_y)
                moving_icon["pos"] = (nx, ny)
            # dragging a file icon to drop
            if dragging_icon and pygame.mouse.get_pressed()[0]:
                r = desktop_window["rect"]; content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
                new_rel_x = pos[0] - content.x - dragging_icon_offset[0]
                new_rel_y = pos[1] - content.y - dragging_icon_offset[1]
                # clamp while dragging
                nx, ny = clamp_icon_pos(new_rel_x, new_rel_y)
                dragging_icon["pos"] = (nx, ny)
            for w in windows.values():
                if w["type"] == "paint" and w["content"].get("drawing"):
                    last = w["content"].get("last", pos)
                    w["content"].setdefault("lines", []).append((last, pos, 3))
                    w["content"]["last"] = pos

    # update DESKTOP_ICONS rects (enforce clamp on each render to avoid drifting outside)
    if desktop_open:
        r = desktop_window["rect"]
        content = pygame.Rect(r.x+6, r.y+40, r.width-12, r.height-46)
        for icon in DESKTOP_ICONS:
            px, py = icon["pos"]
            # Clamp stored relative pos here too to be safe
            nx, ny = clamp_icon_pos(px, py)
            icon["pos"] = (nx, ny)
            ix = content.x + int(nx); iy = content.y + int(ny)
            icon["rect"] = pygame.Rect(int(ix), int(iy), ICON_SIZE[0], ICON_SIZE[1])

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()
