# pygbag: no_keydown_bootstrap
# Math bird - A Pygame Pygbag - simple math game project
# For further developments and participations
# visit and fork: https://github.com/betakontext/mathbird
# Copyright (c) 2026 Christoph Medicus
# Licensed under the MIT License

import sys
import random
import asyncio
import math
import pygame
import os

# Get script directory safely
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() or '__file__' in globals() else os.getcwd()
os.chdir(script_dir)

pygame.init()
try:
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=1024)
    pygame.mixer.init()
except pygame.error:
    pass

try:
    import js
except Exception:
    js = None

def notify_state(name):
    if js:
        # In Iframe (to parent)
        try:
            js.window.parent.postMessage({"type": "game_state", "state": name}, "*")
        except Exception:
            pass
        # Direct (self)
        try:
            js.window.postMessage({"type": "game_state_self", "state": name}, "*")
        except Exception:
            pass

def is_browser():
    return js is not None

def get_canvas_element():
    if not is_browser():
        return None
    try:
        return js.document.querySelector("canvas")
    except Exception:
        return None

# DOM Fullscreen (browser)
def request_dom_fullscreen():
    if not is_browser():
        return False
    c = get_canvas_element()
    if not c:
        return False
    try:
        p = c.requestFullscreen()
        try:
            p.then(lambda *_: None).catch(lambda *_: None)
        except Exception:
            pass
        return True
    except Exception:
        return False

def exit_dom_fullscreen():
    if not is_browser():
        return False
    try:
        p = js.document.exitFullscreen()
        try:
            p.then(lambda *_: None).catch(lambda *_: None)
        except Exception:
            pass
        return True
    except Exception:
        return False

def is_dom_fullscreen():
    if not is_browser():
        return False
    try:
        return bool(js.document.fullscreenElement)
    except Exception:
        return False

WIDTH, HEIGHT = 1280, 720

# Screen setup
if is_browser():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Math Bird")
notify_state("click_to_start")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (135, 206, 250)
YELLOW= (255, 255, 0)
GREEN = (50, 220, 120)
CLOUD_COLOR = (255, 255, 255)
BIRD_COLOR  = (0, 0, 0)

# Immediate initial frame: static play button
try:
    screen.fill(BLUE)
    radius = 70
    cx, cy = WIDTH // 2, HEIGHT // 2
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), radius, 4)
    tri_w = int(radius * 0.8)
    tri_h = int(radius * 0.7)
    tri = [(cx - tri_w//4, cy - tri_h//2),
           (cx - tri_w//4, cy + tri_h//2),
           (cx + tri_w//2, cy)]
    pygame.draw.polygon(screen, (255, 255, 255), tri)
    hint_font = pygame.font.Font(None, 28)
    hint = hint_font.render("Press ENTER.", True, WHITE)
    screen.blit(hint, (cx - hint.get_width() // 2, cy + 120))
    pygame.display.flip()
except Exception:
    pass

is_fullscreen = False

ASSETS = os.path.join(os.path.dirname(__file__), "Audio")

def load_sound(name, volume=1.0):
    path = os.path.join(ASSETS, name)
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    except Exception:
        return None

flap_sound      = load_sound("Flap.ogg", 0.5)
wind_sound      = load_sound("Wind.ogg", 0.06)
rauschen_sound  = load_sound("Rauschen.ogg", 1.0)
phaser_sound    = load_sound("Phaser.ogg", 1.0)
wrong_sound     = load_sound("Wrong.ogg", 1.0)
zwitscher_sound = load_sound("Zwitschern.ogg", 0.7)

try:
    pygame.mixer.set_num_channels(16)
    flap_channel = pygame.mixer.Channel(7)
except Exception:
    flap_channel = None

STATE_CLICK_TO_START = "click_to_start"
STATE_START          = "start"
STATE_MODE_SELECT    = "mode_select"
STATE_GOAL_INPUT     = "goal_input"
STATE_PLAY           = "play"
STATE_RESULT         = "result"
STATE_NAME_SAVE      = "name_save"

state = STATE_CLICK_TO_START

# Gameplay mode
MODE_ADD_SUB = "0"
MODE_MUL = "1"
MODE_DIV = "2"
MODE_MIX = "3"
mode = MODE_ADD_SUB
selected_mode_index = 0
MODE_LIST = [MODE_ADD_SUB, MODE_MUL, MODE_DIV, MODE_MIX]

bird_width = 25
bird_height = 40
bird_x = 60
bird_y = HEIGHT // 2
bird_speed = 5
wing_flap = 4.0
wing_direction = 4.0
wing_flap_rate = 0.5
wing_length = 40

# Render offsets for the bird
BIRD_DRAW_OFFSET_X = 50
BIRD_DRAW_OFFSET_Y = -200

clouds = []
cloud_speed = 5
cloud_spawn_time = 2000
last_cloud_spawn = 0

# animated popups: entries with {'x','y','text','size','color','time_started'}
animated_values = []

goal = 2
cloud_counter = 0
cloud_entered_counter = 0
cloud_values_sum = 0.0
CLOUD_MARGIN = 16

super_active = False
super_start_time = 0
super_duration = 2000
swarm_active = False
swarm_speed = 1.5

suppress_flap_sound = True
flap_last = 0
flap_min_interval = 140
flap_delay_until = pygame.time.get_ticks() + 300
chirp_last = 0
chirp_min_interval = 120

wind_started = False
wind_start_at = None

goal_input_buffer = ""
result_input_buffer = ""
result_text = ""

engaged = False

# Touch / Drag / Tap controls
touch_active = False
touch_last_pos = None
drag_sensitivity = 0.8
tap_target_active = False
tap_target = None
tap_speed = 9.0

# Freeze counting after last required cloud was collected
count_freeze = False

# Signs hidden until first collection
show_signs = False

# Track whether the first counted cloud has been collected in this run
first_collected_done = False

# Rects for mouse selection in mode screen
mode_option_rects = {}

# Score related and staged popup timers
flight_bonus = 0
total_score_popup_spawned = False
result_screen_opened_at = 0
bonus_popup_shown = False
result_popup_shown = False
result_popup_shown_at = 0

# Wrong attempt tracking
wrong_answer_given = False

# Name/Score saving
name_input = ""
scores = []  # [{'name','mode','calc','bonus','total'}]
rank_show_until = 0  # show Name & Save ranking until (ms). 0 means not scheduled.
name_saved_once = False  # ensure single-shot save per result

# Auto timings after ENTER on result screen
auto_total_due_at = 0      # ENTER + 1s
auto_name_due_at = 0       # ENTER + 3s
auto_total_hide_at = 0     # ENTER + 3s (so visible 2s)
total_popup_active = False

def stop_all_audio():
    global wind_started, flap_channel
    try:
        for s in (flap_sound, wind_sound, rauschen_sound, phaser_sound, wrong_sound, zwitscher_sound):
            try:
                if s: s.stop()
            except Exception:
                pass
        try:
            for i in range(32):
                try:
                    pygame.mixer.Channel(i).stop()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            pygame.mixer.stop()
        except Exception:
            pass
        wind_started = False
    except Exception:
        pass

def reset_run_state():
    global bird_x, bird_y, wing_flap, wing_direction
    global clouds, animated_values
    global cloud_counter, cloud_entered_counter, cloud_values_sum
    global super_active, super_start_time, swarm_active
    global flap_last, flap_delay_until
    global WIDTH, HEIGHT
    global touch_active, touch_last_pos, tap_target_active, tap_target
    global count_freeze, show_signs, first_collected_done
    global flight_bonus, total_score_popup_spawned
    global result_screen_opened_at, bonus_popup_shown, result_popup_shown, result_popup_shown_at
    global wrong_answer_given, result_input_buffer, result_text, name_input, rank_show_until, name_saved_once
    global auto_total_due_at, auto_name_due_at, auto_total_hide_at, total_popup_active

    bird_x = 60
    bird_y = HEIGHT // 2
    wing_flap = 0
    wing_direction = 4

    clouds.clear()
    animated_values.clear()

    cloud_counter = 0
    cloud_entered_counter = 0

    if mode in (MODE_ADD_SUB, MODE_MIX):
        cloud_values_sum = 0.0
    elif mode == MODE_MUL:
        cloud_values_sum = 1.0
    elif mode == MODE_DIV:
        cloud_values_sum = None

    super_active = False
    super_start_time = 0
    swarm_active = False

    flap_last = 0
    flap_delay_until = pygame.time.get_ticks() + 600

    touch_active = False
    touch_last_pos = None
    tap_target_active = False
    tap_target = None

    count_freeze = False
    show_signs = False
    first_collected_done = False

    flight_bonus = 0
    total_score_popup_spawned = False
    result_screen_opened_at = 0
    bonus_popup_shown = False
    result_popup_shown = False
    result_popup_shown_at = 0
    wrong_answer_given = False

    result_input_buffer = ""
    result_text = ""
    name_input = ""
    rank_show_until = 0
    name_saved_once = False

    auto_total_due_at = 0
    auto_name_due_at = 0
    auto_total_hide_at = 0
    total_popup_active = False

def reset_to_boot():
    global state, goal_input_buffer, result_input_buffer, result_text, name_input, rank_show_until, name_saved_once
    try:
        stop_all_audio()
    except Exception:
        pass
    try:
        reset_run_state()
    except Exception:
        pass
    try:
        if is_browser() and is_dom_fullscreen():
            exit_dom_fullscreen()
    except Exception:
        pass

    goal_input_buffer = ""
    result_input_buffer = ""
    result_text = ""
    name_input = ""
    rank_show_until = 0
    name_saved_once = False
    state = STATE_CLICK_TO_START
    notify_state("click_to_start")

def mark_engaged():
    global engaged, wind_started
    if engaged:
        return
    engaged = True
    if is_browser():
        try:
            if wind_sound and not wind_started:
                wind_sound.set_volume(0.06)
                wind_sound.play(-1)
                wind_started = True
        except Exception:
            pass

def toggle_fullscreen():
    global is_fullscreen, screen
    if is_browser():
        try:
            if is_dom_fullscreen():
                if exit_dom_fullscreen():
                    is_fullscreen = False
            else:
                if request_dom_fullscreen():
                    is_fullscreen = True
        except Exception:
            pass
        return
    try:
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Math Bird")
        pygame.display.flip()
    except Exception:
        is_fullscreen = False

# Browser hooks
if is_browser():
    try:
        js.document.addEventListener(
            "fullscreenchange",
            js.python(lambda evt=None: (globals().__setitem__('is_fullscreen', is_dom_fullscreen())))
        )
    except Exception:
        pass

    try:
        js.document.addEventListener(
            "visibilitychange",
            js.python(lambda evt=None: (
                stop_all_audio(),
                globals().__setitem__('touch_active', False),
                globals().__setitem__('tap_target_active', False)
            ))
        )
    except Exception:
        pass

    try:
        c = get_canvas_element()
        if c:
            c.addEventListener(
                "mouseleave",
                js.python(lambda evt=None: (
                    globals().__setitem__('touch_active', False),
                    globals().__setitem__('tap_target_active', False)
                ))
            )
    except Exception:
        pass

    try:
        def on_message(evt):
            data = evt.data
            t = None
            try:
                t = data.get("type")
            except Exception:
                pass
            if t == "close_game":
                try:
                    stop_all_audio()
                except Exception:
                    pass
                try:
                    pygame.quit()
                except Exception:
                    pass
                try:
                    sys.exit()
                except Exception:
                    pass
        js.window.addEventListener("message", js.python(on_message))
    except Exception:
        pass

def get_logic_bounds():
    min_x_draw, max_x_draw = 0, WIDTH
    min_y_draw, max_y_draw = 0, HEIGHT
    min_x_logic = min_x_draw - BIRD_DRAW_OFFSET_X
    max_x_logic = max_x_draw - BIRD_DRAW_OFFSET_X - bird_width
    min_y_logic = min_y_draw - BIRD_DRAW_OFFSET_Y
    max_y_logic = max_y_draw - BIRD_DRAW_OFFSET_Y - bird_height
    if max_x_logic < min_x_logic: max_x_logic = min_x_logic
    if max_y_logic < min_y_logic: max_y_logic = min_y_logic
    return min_x_logic, max_x_logic, min_y_logic, max_y_logic

def clamp_bird(x, y):
    min_x_logic, max_x_logic, min_y_logic, max_y_logic = get_logic_bounds()
    x = max(min_x_logic, min(max_x_logic, x))
    y = max(min_y_logic, min(max_y_logic, y))
    return x, y

def draw_raven(x, y, flap_offset=0):
    pygame.draw.line(screen, BIRD_COLOR, (x, y + bird_height // 2), (x + bird_width, y + bird_height // 2), 6)
    wing_y_offset = (wing_flap + flap_offset) * wing_direction
    pygame.draw.line(screen, BIRD_COLOR, (x, y + bird_height // 2.3), (x - wing_length, y + bird_height // 2.5 - wing_y_offset), 4)
    pygame.draw.line(screen, BIRD_COLOR, (x + bird_width, y + bird_height // 2.3), (x + bird_width + wing_length, y + bird_height // 2.5 - wing_y_offset), 4)
    pygame.draw.line(screen, BIRD_COLOR, (x, y + bird_height // 2), (x - 10, y + bird_height // 2 - 10), 4)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 35, y + 10), 5)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 35, y + 18), 5)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 25, y + 18), 3)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 10, y + 25), 7)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 30, y + 15), 5)
    pygame.draw.circle(screen, BIRD_COLOR, (x + 40, y + 15), 5)
    pygame.draw.circle(screen, WHITE, (x + 35, y + 15), 4)
    pygame.draw.circle(screen, WHITE, (x + 45, y + 15), 4)
    pygame.draw.circle(screen, (0, 0, 0), (x + 35, y + 15), 2)
    pygame.draw.circle(screen, (0, 0, 0), (x + 45, y + 15), 2)
    pygame.draw.polygon(screen, YELLOW, [(x + 40, y + 17), (x + 45, y + 15), (x + 40, y + 19)])

def draw_cloud(x, y, size, op, value, c_counter, g_goal, circles,
               bob_amp=0.0, bob_freq=0.0, phase=0.0, t0=0.0):
    t = pygame.time.get_ticks() / 1000.0
    dt = t - t0
    dy = bob_amp * math.sin(2.0 * math.pi * bob_freq * dt + phase)
    base_x = x
    base_y = y + int(dy)

    large_thr = size * 0.42
    small_thr = size * 0.30

    for c in circles:
        r0 = c['r0']
        amp_scale = 1.0
        phase_add = 0.0
        if r0 >= large_thr:
            amp_scale = 0.75
            phase_add = math.pi * 0.25
        elif r0 <= small_thr:
            amp_scale = 1.15

        r = r0 + (c['r_amp'] * amp_scale) * math.sin(2.0 * math.pi * c['r_freq'] * dt + c['r_phase'] + phase_add)
        r = max(2, int(r))
        ox = c['ox'] + c['ox_amp'] * math.sin(2.0 * math.pi * c['ox_freq'] * dt + c['ox_phase'])
        oy = c['oy'] + c['oy_amp'] * math.sin(2.0 * math.pi * c['oy_freq'] * dt + c['oy_phase'])

        pygame.draw.circle(screen, CLOUD_COLOR, (base_x + int(ox), base_y + int(oy)), r)

    # Label while collecting
    if c_counter < g_goal and (not count_freeze):
        font = pygame.font.Font(None, 36)
        if not show_signs:
            label = f"{int(value)}"
        else:
            if op == "+":
                label = f"{value:+d}"
            elif op == "-":
                label = f"-{abs(int(value))}"
            elif op == "×":
                label = f"×{int(value)}"
            elif op == "÷":
                label = f"/{int(value)}"
            else:
                label = str(int(value))
        val_surf = font.render(label, True, RED)
        screen.blit(val_surf, (base_x + size // 16 - val_surf.get_width() // 2,
                               base_y + size // 16 - val_surf.get_height() // 2))

def scatter_cloud(x, y):
    for _ in range(20):
        scatter_x = random.randint(-10, 10)
        scatter_y = random.randint(-10, 10)
        scatter_radius = random.randint(4, 14)
        pygame.draw.circle(screen, CLOUD_COLOR, (x + scatter_x, y + scatter_y), scatter_radius)

def draw_start_screen():
    instructions_font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 54)
    title = title_font.render("MATH BIRD", True, YELLOW)

    nav_text = instructions_font.render("Use arrow keys to navigate the bird.", True, WHITE)
    start_text = instructions_font.render("Press ENTER to continue.", True, WHITE)

    screen.blit(title,    (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - title.get_height() // 2 - 160))
    screen.blit(nav_text, (WIDTH // 2 - nav_text.get_width() // 2, HEIGHT // 2 + 100))
    screen.blit(start_text,(WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 150))

def draw_mode_select_screen():
    global mode_option_rects
    mode_option_rects = {}

    font = pygame.font.Font(None, 44)
    small = pygame.font.Font(None, 34)

    title = font.render("Choose your calculation type. Press:", True, WHITE)
    hint = small.render("Then press ENTER to set how many clouds to collect.", True, WHITE)

    y0 = HEIGHT//2 - 160
    x_center = WIDTH//2

    screen.blit(title, (x_center - title.get_width()//2, y0))

    options = [
        (MODE_ADD_SUB, "0 for additions and subtractions"),
        (MODE_MUL,     "1 for multiplications"),
        (MODE_DIV,     "2 for divisions"),
        (MODE_MIX,     "3 to mix all calculation types"),
    ]

    for i, (m, text) in enumerate(options):
        is_selected = (MODE_LIST[selected_mode_index] == m)
        color = WHITE if is_selected else YELLOW
        surf = small.render(text, True, color)
        y = y0 + 60 + i*40
        rect = surf.get_rect()
        rect.topleft = (x_center - surf.get_width()//2, y)
        screen.blit(surf, rect.topleft)
        mode_option_rects[m] = rect

    screen.blit(hint, (x_center - hint.get_width()//2, y0 + 60 + len(options)*40 + 20))

def draw_goal_overlay():
    font = pygame.font.Font(None, 36)
    prompt_text = "How many clouds do you want to collect?"
    prompt = font.render(prompt_text, True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 140))
    box_w, box_h = 240, 48
    box = pygame.Rect((WIDTH - box_w)//2, HEIGHT//2 - 20, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box, 2)
    txt = font.render(goal_input_buffer, True, WHITE)
    screen.blit(txt, (box.x + 10, box.y + (box_h - txt.get_height())//2))
    hint = pygame.font.Font(None, 28).render("Type a number and ENTER.", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))

def format_result_value(v):
    if v is None:
        return ""
    if abs(v - int(round(v))) < 1e-9:
        return str(int(round(v)))
    return f"{v:.3f}"

def draw_result_overlay():
    if cloud_entered_counter == goal:
        result2_text = "SUPERFLY!"
    elif goal < cloud_entered_counter <= goal + 5:
        result2_text = "GOOD FLIGHT!"
    elif cloud_entered_counter > goal:
        result2_text = "BAD FLIGHT!"
    else:
        result2_text = ""
    result2_font = pygame.font.Font(None, 54)
    result2 = result2_font.render(result2_text, True, YELLOW)
    screen.blit(result2, (WIDTH // 2 - result2.get_width() // 2, HEIGHT // 2 - 200))
    counts_font = pygame.font.Font(None, 36)
    counts_text = f"You collected {cloud_counter} of {cloud_entered_counter} clouds."
    counts = counts_font.render(counts_text, True, WHITE)
    screen.blit(counts, (WIDTH // 2 - counts.get_width() // 2, HEIGHT // 2 - 160))
    promt_font = pygame.font.Font(None, 36)
    promt_text = "What's your result? (press ENTER)"
    promt = promt_font.render(promt_text, True, WHITE)
    screen.blit(promt, (WIDTH // 2 - promt.get_width() // 2, HEIGHT // 2 - 120))
    font = pygame.font.Font(None, 36)
    box_w, box_h = 300, 48
    box = pygame.Rect((WIDTH - box_w)//2, HEIGHT//2 - 60, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box, 2)
    txt = font.render(result_input_buffer, True, WHITE)
    screen.blit(txt, (box.x + 10, box.y + (box_h - txt.get_height())//2))
    res_font = pygame.font.Font(None, 48)
    res = res_font.render(result_text, True, YELLOW)
    screen.blit(res, (WIDTH // 2 - res.get_width() // 2, HEIGHT // 2 + 10))
    help1 = font.render("Press F to Fly again.", True, WHITE)
    help2 = font.render("Press Q to exit.", True, WHITE)
    screen.blit(help1, (WIDTH // 2 - help1.get_width() // 2, HEIGHT // 2 + 70))
    screen.blit(help2, (WIDTH // 2 - help2.get_width() // 2, HEIGHT // 2 + 110))

def draw_name_save_overlay(latest_score, top_scores, saved_once, rank_time_left_ms):
    title_font = pygame.font.Font(None, 54)
    font = pygame.font.Font(None, 36)
    small = pygame.font.Font(None, 28)

    title = title_font.render("NAME & SAVE", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    # Name input (locked after first save)
    prompt_text = "Enter your name and press ENTER to save:" if not saved_once else "Saved! Ranking will remain visible."
    prompt = font.render(prompt_text, True, WHITE)
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 160))

    box_w, box_h = 360, 48
    box = pygame.Rect((WIDTH - box_w)//2, 200, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box, 2)
    name_display = name_input if not saved_once else "(locked)"
    name_txt = font.render(name_display, True, WHITE)
    screen.blit(name_txt, (box.x + 10, box.y + (box_h - name_txt.get_height())//2))

    if latest_score:
        calc_str = format_result_value(latest_score['calc'])
        total_str = format_result_value(latest_score['total'])
        latest = small.render(f"Last flight — Mode: {latest_score['mode']}  Calc: {calc_str}  Bonus: {int(latest_score['bonus'])}  Total Score: {total_str}", True, WHITE)
        screen.blit(latest, (WIDTH//2 - latest.get_width()//2, 270))

    y = 320
    header = font.render("Scores (session):", True, WHITE)
    screen.blit(header, (WIDTH//2 - header.get_width()//2, y))
    y += 40
    for i, s in enumerate(top_scores[:8]):
        calc_str = format_result_value(s['calc'])
        total_str = format_result_value(s['total'])
        line = small.render(f"{i+1}. {s['name']} — Mode {s['mode']} — Calc {calc_str} + Bonus {int(s['bonus'])} = {total_str}", True, YELLOW)
        screen.blit(line, (WIDTH//2 - line.get_width()//2, y))
        y += 28

    # Hints: show both timing info and "Press F to fly again"
    info = "Saving shows the ranking for 10s, then returns to start."
    if saved_once and rank_time_left_ms > 0:
        sec_left = max(0, int(math.ceil(rank_time_left_ms / 1000.0)))
        info = f"Ranking will return to start in {sec_left}s."
    hint_info = small.render(info, True, WHITE)
    screen.blit(hint_info, (WIDTH//2 - hint_info.get_width()//2, HEIGHT - 110))

    hint_f = small.render("Press F to fly again.", True, WHITE)
    screen.blit(hint_f, (WIDTH//2 - hint_f.get_width()//2, HEIGHT - 80))

def play_button_pulse(t, base_r=70, amp=10, speed=1.0):
    return int(base_r + amp * (0.5 + 0.5 * math.sin(2 * math.pi * speed * t)))

def draw_play_button(center, t):
    cx, cy = center
    radius = play_button_pulse(t, base_r=70, amp=10, speed=1.0)
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), radius, 4)
    tri_w = int(radius * 0.8)
    tri_h = int(radius * 0.7)
    tri = [(cx - tri_w//4, cy - tri_h//2),
           (cx - tri_w//4, cy + tri_h//2),
           (cx + tri_w//2, cy)]
    pygame.draw.polygon(screen, (255, 255, 255), tri)

def play_button_rect(center):
    cx, cy = center
    size = 200
    return pygame.Rect(cx - size//2, cy - size//2, size, size)

def pick_cloud_op_and_value():
    if mode == MODE_ADD_SUB:
        v = random.randint(-10, 10)
        while v == 0:
            v = random.randint(-10, 10)
        if v >= 0:
            return ("+", v)
        else:
            return ("-", abs(v))
    elif mode == MODE_MUL:
        v = random.randint(1, 9)
        return ("×", v)
    elif mode == MODE_DIV:
        v = random.randint(2, 9)
        return ("÷", v)
    elif mode == MODE_MIX:
        ops = ["+", "-", "×", "÷"]
        op = random.choice(ops)
        if op == "+":
            v = random.randint(1, 10)
        elif op == "-":
            v = random.randint(1, 10)
        elif op == "×":
            v = random.randint(1, 9)
        else:
            v = random.randint(2, 9)
        return (op, v)
    return ("+", random.randint(1, 9))

def apply_op_to_sum(current, op, val):
    if mode == MODE_DIV:
        if current is None:
            if op in ["+", "-"]:
                return float(val if op == "+" else -val)
            elif op == "×":
                return float(val)
            elif op == "÷":
                return float(val)
        else:
            if op == "+":
                return current + val
            if op == "-":
                return current - val
            if op == "×":
                return current * val
            if op == "÷":
                return current / val
        return current

    if mode == MODE_MUL:
        if op == "×":
            return current * val
        if op == "+":
            return current + val
        if op == "-":
            return current - val
        if op == "÷":
            return current / val
        return current

    if op == "+":
        return current + val
    if op == "-":
        return current - val
    if op == "×":
        return current * val
    if op == "÷":
        return current / val
    return current

def check_user_result(user_text, target_value):
    try:
        if "." in user_text or "," in user_text:
            user_text = user_text.replace(",", ".")
            u = float(user_text)
        else:
            u = int(user_text)
            u = float(u)
    except Exception:
        return False
    tol = 1e-3
    return abs(u - float(target_value)) <= tol

def spawn_bonus_popup(bonus_value):
    center_x = WIDTH // 2
    y = HEIGHT // 2 - 250
    now = pygame.time.get_ticks()
    animated_values.append({
        'x': center_x,
        'y': y,
        'text': f"+{int(bonus_value)}",
        'size': 44,
        'color': (50, 220, 120) if bonus_value > 0 else YELLOW,
        'time_started': now
    })

def spawn_result_popup(calc_value):
    center_x = WIDTH // 2
    y = HEIGHT // 2 - 50
    now = pygame.time.get_ticks()
    if isinstance(calc_value, (int, float)):
        is_int = abs(calc_value - int(round(calc_value))) < 1e-9
        txt = f"= {int(round(calc_value))}" if is_int else f"= {calc_value:.2f}"
    else:
        txt = f"= {calc_value}"
    animated_values.append({
        'x': center_x,
        'y': y,
        'text': txt,
        'size': 44,
        'color': WHITE,
        'time_started': now
    })

def spawn_total_popup(total_value):
    center_x = WIDTH // 2
    y = HEIGHT // 2 + 280
    now = pygame.time.get_ticks()
    is_int = abs(total_value - int(round(total_value))) < 1e-9
    txt = f"Total Score: {int(round(total_value))}" if is_int else f"Total Score: {total_value:.2f}"
    animated_values.append({
        'x': center_x,
        'y': y,
        'text': txt,
        'size': 48,
        'color': YELLOW,
        'time_started': now
    })

def mode_label(m):
    return {"0": "Add/Sub", "1": "Mul", "2": "Div", "3": "Mix"}.get(m, m)

async def main():
    global state, mode, selected_mode_index
    global bird_x, bird_y, wing_flap, wing_direction
    global last_cloud_spawn, cloud_counter, cloud_entered_counter, cloud_values_sum
    global super_active, super_start_time, swarm_active
    global goal_input_buffer, result_input_buffer, result_text, goal
    global suppress_flap_sound, flap_last, flap_delay_until, chirp_last
    global wind_started, WIDTH, HEIGHT, screen
    global touch_active, touch_last_pos, tap_target_active, tap_target
    global count_freeze, show_signs, first_collected_done
    global flight_bonus, total_score_popup_spawned
    global result_screen_opened_at, bonus_popup_shown, result_popup_shown, result_popup_shown_at
    global wrong_answer_given, name_input, scores, rank_show_until, name_saved_once
    global auto_total_due_at, auto_name_due_at, auto_total_hide_at, total_popup_active

    clock = pygame.time.Clock()

    try:
        while True:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    try: stop_all_audio()
                    except: pass
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    try: stop_all_audio()
                    except Exception: pass
                    try:
                        if is_browser():
                            try: js.window.parent.postMessage({"type": "pause_audio"}, "*")
                            except Exception: pass
                            try: js.window.parent.postMessage({"type": "close_game"}, "*")
                            except Exception: pass
                            try: js.window.postMessage({"type": "close_game"}, "*")
                            except Exception: pass
                    except Exception:
                        pass
                    touch_active = False
                    tap_target_active = False
                    tap_target = None
                    try: pygame.time.delay(60)
                    except Exception: pass
                    pygame.quit(); sys.exit()

                if event.type == pygame.VIDEORESIZE and not is_browser():
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    continue

                if event.type == pygame.KEYDOWN:
                    if not is_browser():
                        mark_engaged()
                        if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)):
                            toggle_fullscreen(); continue
                    else:
                        if event.key == pygame.K_F11:
                            toggle_fullscreen(); continue

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if is_browser():
                        mark_engaged()
                    if state == STATE_CLICK_TO_START:
                        if play_button_rect((WIDTH//2, HEIGHT//2)).collidepoint(event.pos):
                            state = STATE_START
                            notify_state("start")
                            continue
                    if state == STATE_MODE_SELECT:
                        mx, my = event.pos
                        for m, rect in mode_option_rects.items():
                            if rect.collidepoint(mx, my):
                                selected_mode_index = MODE_LIST.index(m)
                                mode = MODE_LIST[selected_mode_index]
                                break
                    if state == STATE_PLAY:
                        if swarm_active:
                            touch_active = False
                            tap_target_active = False
                        else:
                            touch_active = True
                            touch_last_pos = event.pos
                            tap_target_active = True
                            tap_target = event.pos

                if event.type == pygame.MOUSEMOTION and touch_active and state == STATE_PLAY:
                    if swarm_active:
                        touch_active = False
                        tap_target_active = False
                    if touch_last_pos is not None:
                        dx = event.pos[0] - touch_last_pos[0]
                        dy = event.pos[1] - touch_last_pos[1]
                        bird_x += int(dx * drag_sensitivity)
                        bird_y += int(dy * drag_sensitivity)
                        if not swarm_active:
                            bird_x, bird_y = clamp_bird(bird_x, bird_y)
                    touch_last_pos = event.pos
                    tap_target_active = False

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if swarm_active:
                        touch_active = False
                        tap_target_active = False
                    touch_active = False
                    touch_last_pos = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if state in (STATE_PLAY, STATE_RESULT, STATE_GOAL_INPUT, STATE_MODE_SELECT, STATE_NAME_SAVE):
                            reset_run_state()
                            state = STATE_MODE_SELECT
                            goal_input_buffer = ""
                            result_input_buffer = ""
                            result_text = ""
                            name_input = ""
                            notify_state("mode_select")
                            continue

                    if state == STATE_CLICK_TO_START:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            state = STATE_START
                            notify_state("start")
                            continue

                    if state == STATE_START:
                        if event.key == pygame.K_RETURN:
                            state = STATE_MODE_SELECT
                            notify_state("mode_select")

                    elif state == STATE_MODE_SELECT:
                        if event.key == pygame.K_0:
                            selected_mode_index = 0; mode = MODE_LIST[selected_mode_index]
                        elif event.key == pygame.K_1:
                            selected_mode_index = 1; mode = MODE_LIST[selected_mode_index]
                        elif event.key == pygame.K_2:
                            selected_mode_index = 2; mode = MODE_LIST[selected_mode_index]
                        elif event.key == pygame.K_3:
                            selected_mode_index = 3; mode = MODE_LIST[selected_mode_index]
                        elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                            selected_mode_index = (selected_mode_index + 1) % len(MODE_LIST)
                            mode = MODE_LIST[selected_mode_index]
                        elif event.key in (pygame.K_UP, pygame.K_LEFT):
                            selected_mode_index = (selected_mode_index - 1) % len(MODE_LIST)
                            mode = MODE_LIST[selected_mode_index]
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            state = STATE_GOAL_INPUT
                            notify_state("goal_input")

                    elif state == STATE_GOAL_INPUT:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            try:
                                val = int(goal_input_buffer.strip()) if goal_input_buffer else goal
                            except Exception:
                                val = goal
                            goal = max(1, val)
                            reset_run_state()
                            last_cloud_spawn = pygame.time.get_ticks()
                            suppress_flap_sound = False

                            if wind_sound and not wind_started:
                                wind_sound.play(-1)
                                wind_started = True

                            state = STATE_PLAY
                            notify_state("play")

                        elif event.key == pygame.K_BACKSPACE:
                            goal_input_buffer = goal_input_buffer[:-1]
                        else:
                            if len(goal_input_buffer) < 10 and event.unicode.isprintable():
                                goal_input_buffer += event.unicode

                    elif state == STATE_PLAY:
                        pass

                    elif state == STATE_RESULT:
                        if event.key == pygame.K_RETURN:
                            try:
                                target_calc = cloud_values_sum if cloud_values_sum is not None else 0.0
                                ok = check_user_result(result_input_buffer.strip(), target_calc)
                                if ok:
                                    result_text = "Correct!"
                                    if rauschen_sound: rauschen_sound.play()
                                    if not result_popup_shown:
                                        spawn_result_popup(target_calc)
                                        result_popup_shown = True
                                        result_popup_shown_at = pygame.time.get_ticks()
                                else:
                                    wrong_answer_given = True
                                    if wrong_sound: wrong_sound.play()
                                    result_text = "Try again."
                            except Exception:
                                result_text = "Invalid input. Please enter a number."
                                if phaser_sound: phaser_sound.play()

                            # Auto timers: total at +1s (visible 2s), name at +3s
                            now_ts = pygame.time.get_ticks()
                            auto_total_due_at = now_ts + 1000
                            auto_total_hide_at = now_ts + 3000
                            auto_name_due_at = now_ts + 3000

                        elif event.key == pygame.K_BACKSPACE:
                            result_input_buffer = result_input_buffer[:-1]
                        elif event.key in (pygame.K_f, pygame.K_SPACE):
                            reset_run_state()
                            state = STATE_MODE_SELECT
                            goal_input_buffer = ""
                            result_input_buffer = ""
                            result_text = ""
                            name_input = ""
                            notify_state("mode_select")
                        else:
                            if len(result_input_buffer) < 20 and event.unicode.isprintable():
                                result_input_buffer += event.unicode

                    elif state == STATE_NAME_SAVE:
                        # Allow flight restart anytime with F
                        if event.key in (pygame.K_f, pygame.K_SPACE):
                            reset_run_state()
                            state = STATE_MODE_SELECT
                            notify_state("mode_select")
                        elif event.key == pygame.K_RETURN:
                            # Only allow saving once per result
                            if not name_saved_once:
                                calc_val = (cloud_values_sum if cloud_values_sum is not None else 0.0)
                                calc_part = 0.0 if wrong_answer_given else abs(calc_val)
                                total_val = calc_part + flight_bonus
                                entry = {
                                    'name': name_input.strip() or "Player",
                                    'mode': mode_label(mode),
                                    'calc': calc_part,   # store the positive contribution
                                    'bonus': int(flight_bonus),
                                    'total': total_val
                                }

                                scores.append(entry)
                                scores.sort(key=lambda s: s['total'], reverse=True)
                                # Lock input and show ranking for 10 seconds
                                rank_show_until = pygame.time.get_ticks() + 10000
                                name_saved_once = True
                                name_input = ""  # visually lock
                        elif event.key == pygame.K_BACKSPACE:
                            # Only allow editing before first save
                            if not name_saved_once:
                                name_input = name_input[:-1]
                        else:
                            if not name_saved_once and len(name_input) < 20 and event.unicode.isprintable():
                                name_input += event.unicode

            keys = pygame.key.get_pressed()

            if state == STATE_PLAY:
                if keys[pygame.K_UP]:    bird_y -= bird_speed
                if keys[pygame.K_DOWN]:  bird_y += bird_speed
                if keys[pygame.K_LEFT]:  bird_x -= bird_speed
                if keys[pygame.K_RIGHT]: bird_x += bird_speed

                if tap_target_active and tap_target is not None:
                    bird_screen_x = bird_x + BIRD_DRAW_OFFSET_X
                    bird_screen_y = bird_y + BIRD_DRAW_OFFSET_Y
                    tx, ty = tap_target
                    vx = tx - bird_screen_x
                    vy = ty - bird_screen_y
                    dist = (vx*vx + vy*vy) ** 0.5
                    if dist > 1.0:
                        step = min(tap_speed, dist)
                        if dist > 0:
                            bird_screen_x += vx / dist * step
                            bird_screen_y += vy / dist * step
                        bird_x = int(bird_screen_x - BIRD_DRAW_OFFSET_X)
                        bird_y = int(bird_screen_y - BIRD_DRAW_OFFSET_Y)
                    else:
                        tap_target_active = False

                if not swarm_active:
                    bird_x, bird_y = clamp_bird(bird_x, bird_y)

                # Spawner
                if current_time - last_cloud_spawn > cloud_spawn_time:
                    cloud_y = random.randint(0, HEIGHT - 60)
                    cloud_size = random.randint(50, 100)

                    # Decide if this cloud, upon entering the bird area, will count toward the goal
                    will_count_enter = (not count_freeze) and (cloud_counter < goal)

                    if will_count_enter:
                        # First counting cloud must be a positive addition
                        if not first_collected_done:
                            op, v = ("+", random.randint(1, 10))
                        else:
                            op, v = pick_cloud_op_and_value()
                    else:
                        op, v = ("+", 0)

                    # Precompute cloud circles (4–7)
                    num_circles = random.randint(4, 7)
                    circles = []
                    for _ in range(num_circles):
                        radius = random.randint(cloud_size // 4, cloud_size // 2)
                        offset_x = random.randint(-cloud_size // 4, cloud_size // 4)
                        offset_y = random.randint(-cloud_size // 4, cloud_size // 4)
                        size_factor = max(0.6, min(1.0, (cloud_size / max(1, radius)) * 0.25))
                        r_amp   = max(1.0, radius * random.uniform(0.20, 0.35) * size_factor)
                        r_freq  = random.uniform(0.12, 0.30)
                        r_phase = random.uniform(0.0, math.tau)
                        ox_amp   = random.uniform(2.0, 5.0) * size_factor
                        oy_amp   = random.uniform(2.0, 5.0) * size_factor
                        ox_freq  = random.uniform(0.08, 0.22)
                        oy_freq  = random.uniform(0.10, 0.26)
                        ox_phase = random.uniform(0.0, math.tau)
                        oy_phase = random.uniform(0.0, math.tau)
                        circles.append({
                            'ox': offset_x, 'oy': offset_y,
                            'r0': radius,
                            'r_amp': r_amp, 'r_freq': r_freq, 'r_phase': r_phase,
                            'ox_amp': ox_amp, 'ox_freq': ox_freq, 'ox_phase': ox_phase,
                            'oy_amp': oy_amp, 'oy_freq': oy_freq, 'oy_phase': oy_phase
                        })

                    bob_amp   = random.uniform(3.0, 7.0)
                    bob_freq  = random.uniform(0.15, 0.28)
                    phase     = random.uniform(0.0, math.tau)
                    t0        = pygame.time.get_ticks() / 1000.0

                    if will_count_enter:
                        cloud_entered_counter += 1
                    last_cloud_spawn = current_time

                    clouds.append({
                        'x': WIDTH,
                        'y': cloud_y,
                        'size': cloud_size,
                        'op': op,
                        'value': v,
                        'passed': False,
                        'entered_counted': bool(will_count_enter),
                        'circles': circles,
                        'bob_amp': bob_amp, 'bob_freq': bob_freq,
                        'phase': phase, 't0': t0
                    })

                # Move clouds / offscreen / collision
                for cloud in clouds[:]:
                    cloud['x'] -= cloud_speed

                    if (cloud['x'] + cloud['size']) < -CLOUD_MARGIN:
                        clouds.remove(cloud)
                        continue

                    rect_bird = pygame.Rect(
                        bird_x + BIRD_DRAW_OFFSET_X,
                        bird_y + BIRD_DRAW_OFFSET_Y,
                        bird_width,
                        bird_height
                    )
                    rect_cloud = pygame.Rect(cloud['x'], cloud['y'], cloud['size'], 60)

                    if (not count_freeze) and rect_bird.colliderect(rect_cloud):
                        if cloud_counter < goal:
                            cloud_counter += 1

                            op = cloud.get('op', "+")
                            val = int(cloud.get('value', 0))
                            cloud_values_sum = apply_op_to_sum(cloud_values_sum, op, val)

                            if zwitscher_sound:
                                now = pygame.time.get_ticks()
                                if (now - chirp_last) >= chirp_min_interval:
                                    zwitscher_sound.play()
                                    chirp_last = now

                            # Animated popup text for the collected cloud:
                            # - For the very first collected cloud: show only the number (always positive shown)
                            # - Afterwards: show sign/op as before
                            if not first_collected_done:
                                col_text = f"{abs(val)}"
                            else:
                                if op in ["+","-"]:
                                    col_text = f"{val:+d}" if op == "+" else f"-{abs(val)}"
                                else:
                                    col_text = f"{'×' if op=='×' else '/'}{val}"

                            animated_values.append({
                                'x': cloud['x'], 'y': cloud['y'],
                                'text': col_text,
                                'size': 30, 'color': RED, 'time_started': pygame.time.get_ticks()
                            })
                            scatter_cloud(cloud['x'], cloud['y'])

                            # Mark first collection as done and enable signs for subsequent displays
                            if not first_collected_done:
                                first_collected_done = True
                                show_signs = True

                            clouds.remove(cloud)

                            if cloud_counter >= goal and not count_freeze:
                                count_freeze = True

                                bird_draw_x = bird_x + BIRD_DRAW_OFFSET_X
                                subtract_count = 0
                                for c in clouds:
                                    if c.get('entered_counted'):
                                        cloud_right = c['x'] + c['size']
                                        if cloud_right >= bird_draw_x:
                                            subtract_count += 1
                                            c['entered_counted'] = False
                                if subtract_count:
                                    cloud_entered_counter = max(0, cloud_entered_counter - subtract_count)

                                if not super_active:
                                    super_active = True
                                    super_start_time = pygame.time.get_ticks()
                        else:
                            clouds.remove(cloud)
                        continue

                if cloud_counter >= goal and not super_active:
                    super_active = True
                    super_start_time = pygame.time.get_ticks()

                if super_active and (current_time - super_start_time) > (super_duration + 5000):
                    super_active = False
                    swarm_active = True

                if super_active:
                    if current_time - super_start_time >= super_duration:
                        super_active = False
                        swarm_active = True
                        tap_target_active = False
                        tap_target = None
                        touch_active = False
                        touch_last_pos = None

                if swarm_active:
                    touch_active = False
                    tap_target_active = False
                    tap_target = None

                    bird_x += max(swarm_speed, 3.0)
                    bird_screen_x = bird_x + BIRD_DRAW_OFFSET_X
                    if bird_screen_x > (WIDTH + 80):
                        bird_x = WIDTH + 80 - BIRD_DRAW_OFFSET_X
                        result_input_buffer = ""
                        result_text = ""

                        if cloud_entered_counter == goal:
                            flight_bonus = 100
                        elif goal < cloud_entered_counter <= goal + 5:
                            flight_bonus = 50
                        else:
                            flight_bonus = 0

                        result_screen_opened_at = pygame.time.get_ticks()
                        bonus_popup_shown = False
                        result_popup_shown = False
                        result_popup_shown_at = 0
                        total_score_popup_spawned = False
                        wrong_answer_given = False

                        auto_total_due_at = 0
                        auto_total_hide_at = 0
                        auto_name_due_at = 0
                        total_popup_active = False

                        state = STATE_RESULT
                        notify_state("result")

            # Timed staged popups in result screen
            if state == STATE_RESULT:
                now = pygame.time.get_ticks()
                # Bonus popup 3s after result screen opened
                if not bonus_popup_shown and result_screen_opened_at:
                    if now - result_screen_opened_at >= 3000:
                        spawn_bonus_popup(flight_bonus)
                        bonus_popup_shown = True
                # Auto total popup due (1s after ENTER), once
                if (not total_score_popup_spawned) and auto_total_due_at and now >= auto_total_due_at:
                    raw_calc = (cloud_values_sum if cloud_values_sum is not None else 0.0)
                    calc_part = 0.0 if wrong_answer_given else abs(raw_calc)
                    total_value = calc_part + flight_bonus
                    spawn_total_popup(total_value)
                    total_score_popup_spawned = True
                    total_popup_active = True
                # Hide total popup after 2s visibility (ENTER + 3s)
                if total_popup_active and auto_total_hide_at and now >= auto_total_hide_at:
                    for av in animated_values[:]:
                        if isinstance(av.get('text'), str) and av['text'].startswith("Total:"):
                            animated_values.remove(av)
                    total_popup_active = False
                # Auto switch to name screen at ENTER + 3s
                if auto_name_due_at and now >= auto_name_due_at:
                    state = STATE_NAME_SAVE
                    notify_state("name_save")
                    auto_name_due_at = 0

            # Wing anim + sound
            wing_flap += wing_direction * wing_flap_rate
            crossed = False
            limit = 15
            if wing_flap > limit:
                wing_flap = limit; wing_direction *= -1; crossed = True
            elif wing_flap < -limit:
                wing_flap = -limit; wing_direction *= -1; crossed = True

            allow_flap_sound = (state == STATE_PLAY)
            if crossed and flap_sound and not suppress_flap_sound and allow_flap_sound:
                now = pygame.time.get_ticks()
                if now >= flap_delay_until and (now - flap_last) >= flap_min_interval:
                    if flap_channel and not flap_channel.get_busy(): flap_channel.play(flap_sound)
                    else: flap_sound.play()
                    flap_last = now

            # Render
            screen.fill(BLUE)

            if state == STATE_CLICK_TO_START:
                suppress_flap_sound = True
                tsec = pygame.time.get_ticks() / 1000.0
                draw_play_button((WIDTH // 2, HEIGHT // 2), tsec)
                hint_font = pygame.font.Font(None, 28)
                hint = hint_font.render("Press ENTER.", True, WHITE)
                screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 120))
                pygame.display.flip(); pygame.time.Clock().tick(60); await asyncio.sleep(0); continue

            if state == STATE_START:
                suppress_flap_sound = True
                draw_start_screen()

            elif state == STATE_MODE_SELECT:
                suppress_flap_sound = True
                draw_mode_select_screen()

            elif state == STATE_GOAL_INPUT:
                suppress_flap_sound = True
                draw_goal_overlay()

            elif state in (STATE_PLAY, STATE_RESULT, STATE_NAME_SAVE):
                # Render animated popups
                for av in list(animated_values):
                    elapsed = (current_time - av['time_started']) / 1000.0
                    if elapsed < 1.2:
                        y_offset = -10 * elapsed
                        size_now = int(av.get('size', 30) + 60 * elapsed)
                        color = av.get('color', YELLOW)
                        font = pygame.font.Font(None, size_now)
                        text = av.get('text')
                        if text is None:
                            text = str(av.get('value', ''))
                        surf = font.render(text, True, color)
                        screen.blit(surf, (av['x'] - surf.get_width() // 2, av['y'] + y_offset - surf.get_height() // 2))
                    else:
                        animated_values.remove(av)

                # Draw clouds in PLAY/RESULT
                if state in (STATE_PLAY, STATE_RESULT):
                    for cloud in clouds:
                        if cloud['x'] > WIDTH or (cloud['x'] + cloud['size']) < 0:
                            continue
                        draw_cloud(
                            cloud['x'], cloud['y'], cloud['size'],
                            cloud.get('op', "+"),
                            cloud.get('value', 0),
                            cloud_counter, goal,
                            cloud['circles'],
                            cloud['bob_amp'], cloud['bob_freq'],
                            cloud['phase'], cloud['t0']
                        )

                if state in (STATE_PLAY, STATE_RESULT):
                    draw_raven(bird_x + BIRD_DRAW_OFFSET_X, bird_y + BIRD_DRAW_OFFSET_Y)

                if state == STATE_PLAY and super_active:
                    font = pygame.font.Font(None, 74)
                    text = font.render("WELL DONE!", True, (255, 215, 0))
                    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

                if state == STATE_PLAY and swarm_active:
                    for i in range(30):
                        scatter_x = random.randint(0, 30) * i
                        scatter_y = HEIGHT // 2 + random.randint(-200, 200)
                        flap_offset = random.uniform(-15, 15)
                        draw_raven(WIDTH - scatter_x, scatter_y, flap_offset)

            if state == STATE_RESULT:
                suppress_flap_sound = True
                draw_result_overlay()

            if state == STATE_NAME_SAVE:
                latest_raw = (cloud_values_sum if cloud_values_sum is not None else 0.0)
                latest_calc_part = 0.0 if wrong_answer_given else abs(latest_raw)
                latest_total = latest_calc_part + flight_bonus
                latest = {
                    'name': name_input.strip() or "Player",
                    'mode': mode_label(mode),
                    'calc': latest_calc_part,
                    'bonus': int(flight_bonus),
                    'total': latest_total
                }

                # Remaining time for info text
                time_left = max(0, rank_show_until - pygame.time.get_ticks()) if name_saved_once and rank_show_until else 0
                draw_name_save_overlay(latest, scores, name_saved_once, time_left)
                # Auto-return to start after 10s of showing the ranking (post-save)
                if name_saved_once and rank_show_until and pygame.time.get_ticks() >= rank_show_until:
                    reset_run_state()
                    state = STATE_MODE_SELECT
                    notify_state("mode_select")

            pygame.display.flip()
            pygame.time.Clock().tick(60)
            await asyncio.sleep(0)

    except Exception as e:
        try:
            screen.fill((20, 20, 20))
            font = pygame.font.Font(None, 28)
            lines = ["Python error occurred!", str(e)[:200], "Open browser console (F12) for traceback."]
            y = 40
            for line in lines:
                surf = font.render(line, True, (255, 80, 80))
                screen.blit(surf, (20, y)); y += 36
            pygame.display.flip()
        except Exception:
            pass
        while True:
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
