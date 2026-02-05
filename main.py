# pygbag: no_keydown_bootstrap

# Math bird - A Pygame Pygbag - simple math game project
# For further developments and participatiun
# visit and fork: github.com/betakontext/mathbird

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

# Colors (define before any immediate draw)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (135, 206, 250)
YELLOW= (255, 255, 0)
CLOUD_COLOR = (255, 255, 255)
BIRD_COLOR  = (0, 0, 0)

# Immediate initial frame: static play button (avoid blank blue screen)
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
STATE_GOAL_INPUT     = "goal_input"
STATE_PLAY           = "play"
STATE_RESULT         = "result"

state = STATE_CLICK_TO_START

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

animated_values = []

goal = 2
cloud_counter = 0
cloud_entered_counter = 0
cloud_values_sum = 0
CLOUD_MARGIN = 16  # early offscreen cleanup

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
touch_last_pos = None  # (sx, sy)
drag_sensitivity = 0.8  # 0.6–1.0 for mobile
tap_target_active = False
tap_target = None  # (screen_x, screen_y)
tap_speed = 9.0    # pixels per frame

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

    # Bird position
    bird_x = 60
    bird_y = HEIGHT // 2
    wing_flap = 0
    wing_direction = 4

    # Objects
    clouds.clear()
    animated_values.clear()

    # Counters
    cloud_counter = 0
    cloud_entered_counter = 0
    cloud_values_sum = 0

    # Effects
    super_active = False
    super_start_time = 0
    swarm_active = False

    # Audio flap timing
    flap_last = 0
    flap_delay_until = pygame.time.get_ticks() + 600

    # Touch state
    touch_active = False
    touch_last_pos = None
    tap_target_active = False
    tap_target = None

def reset_to_boot():
    """
    Hard return to boot: stop audio, reset run state, clear input buffers,
    exit fullscreen if needed, go to CLICK_TO_START.
    """
    global state, goal_input_buffer, result_input_buffer, result_text
    try:
        stop_all_audio()
    except Exception:
        pass
    try:
        reset_run_state()
    except Exception:
        pass
    # leave DOM-FS if active
    try:
        if is_browser() and is_dom_fullscreen():
            exit_dom_fullscreen()
    except Exception:
        pass

    goal_input_buffer = ""
    result_input_buffer = ""
    result_text = ""
    state = STATE_CLICK_TO_START
    notify_state("click_to_start")

def mark_engaged():
    # First real user input → unlock audio in browsers
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
                print("wind started after engagement")
        except Exception as e:
            print("wind start error:", e)

# Fullscreen toggle
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

    # Stop audio and input on tab hide
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

    # Stop drag/tap when mouse leaves canvas (prevents stuck drag)
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

    # React to parent "close_game" messages
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
    # Visible drawing area
    min_x_draw, max_x_draw = 0, WIDTH
    min_y_draw, max_y_draw = 0, HEIGHT
    # Logic bounds (due to render offsets)
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

def draw_cloud(x, y, size, value, c_counter, g_goal, circles,
               bob_amp=0.0, bob_freq=0.0, phase=0.0, t0=0.0):
    # Seconds
    t = pygame.time.get_ticks() / 1000.0
    dt = t - t0

    # Vertical bob (no horizontal drift)
    dy = bob_amp * math.sin(2.0 * math.pi * bob_freq * dt + phase)

    base_x = x
    base_y = y + int(dy)

    # thresholds for different wobble strength by radius
    large_thr = size * 0.42
    small_thr = size * 0.30

    # Shape wobble: per-circle radius/offset modulation
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

        pygame.draw.circle(
            screen,
            CLOUD_COLOR,
            (base_x + int(ox), base_y + int(oy)),
            r
        )

    # Number in cloud while collecting
    if c_counter < g_goal:
        font = pygame.font.Font(None, 36)
        val_surf = font.render(str(value), True, RED)
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

    nav_text = instructions_font.render("You can use the arrow keys for navigation", True, WHITE)
    fly_text = instructions_font.render("and F to start or restart your flights.", True, WHITE)

    screen.blit(title,    (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - title.get_height() // 2 - 160))
    screen.blit(nav_text, (WIDTH // 2 - nav_text.get_width() // 2, HEIGHT // 2 + 100))
    screen.blit(fly_text, (WIDTH // 2 - fly_text.get_width() // 2, HEIGHT // 2 + 150))

def draw_goal_overlay():
    font = pygame.font.Font(None, 36)
    prompt_text = "How many calculations do you want to add?"
    prompt = font.render(prompt_text, True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 140))
    box_w, box_h = 240, 48
    box = pygame.Rect((WIDTH - box_w)//2, HEIGHT//2 - 20, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box, 2)
    txt = font.render(goal_input_buffer, True, WHITE)
    screen.blit(txt, (box.x + 10, box.y + (box_h - txt.get_height())//2))
    hint = pygame.font.Font(None, 28).render("Type a number and ENTER.", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))

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
    promt_text = "What's your result?"
    promt = promt_font.render(promt_text, True, WHITE)
    screen.blit(promt, (WIDTH // 2 - promt.get_width() // 2, HEIGHT // 2 - 120))
    font = pygame.font.Font(None, 36)
    box_w, box_h = 240, 48
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

async def main():
    global state
    global bird_x, bird_y, wing_flap, wing_direction
    global last_cloud_spawn, cloud_counter, cloud_entered_counter, cloud_values_sum
    global super_active, super_start_time, swarm_active
    global goal_input_buffer, result_input_buffer, result_text, goal
    global suppress_flap_sound, flap_last, flap_delay_until, chirp_last
    global wind_started, WIDTH, HEIGHT, screen
    global touch_active, touch_last_pos, tap_target_active, tap_target

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
                    # 1) Stop audio
                    try: stop_all_audio()
                    except Exception: pass
                    # 2) Ask parent to close
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
                    # 3) Clear inputs
                    touch_active = False
                    tap_target_active = False
                    tap_target = None
                    # 4) exit
                    try: pygame.time.delay(60)
                    except Exception: pass
                    pygame.quit(); sys.exit()

                # Desktop resizing
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
                    # Touch begin
                    if state == STATE_PLAY:
                        if swarm_active:
                            touch_active = False
                            tap_target_active = False
                        else:
                            touch_active = True
                            touch_last_pos = event.pos
                            tap_target_active = True   # set False if you want Drag-only
                            tap_target = event.pos

                # Touch drag
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
                        if state in (STATE_PLAY, STATE_RESULT):
                            reset_run_state()
                            state = STATE_GOAL_INPUT
                            goal_input_buffer = ""
                            result_input_buffer = ""
                            result_text = ""
                            notify_state("goal_input")
                            continue

                    if state == STATE_CLICK_TO_START:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            state = STATE_START
                            notify_state("start")
                            continue

                    if state == STATE_START:
                        if event.key == pygame.K_f:
                            suppress_flap_sound = True
                            wing_flap = 0
                            wing_direction = 4
                            state = STATE_GOAL_INPUT
                            notify_state("goal_input")

                    elif state == STATE_GOAL_INPUT:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            try:
                                val = int(goal_input_buffer.strip()) if goal_input_buffer else goal
                            except Exception:
                                val = goal
                            goal = max(1, val)
                            # Start run
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
                                if int(result_input_buffer.strip()) == cloud_values_sum:
                                    result_text = "Correct!"
                                    if rauschen_sound: rauschen_sound.play()
                                else:
                                    result_text = f"Sorry! {cloud_values_sum} is the correct result"
                                    if wrong_sound: wrong_sound.play()
                            except Exception:
                                result_text = "Invalid input. Please enter a number."
                                if phaser_sound: phaser_sound.play()
                        elif event.key == pygame.K_BACKSPACE:
                            result_input_buffer = result_input_buffer[:-1]
                        elif event.key in (pygame.K_f, pygame.K_SPACE):
                            reset_run_state()
                            state = STATE_GOAL_INPUT
                            goal_input_buffer = ""
                            result_input_buffer = ""
                            result_text = ""
                            notify_state("goal_input")
                        else:
                            if len(result_input_buffer) < 10 and event.unicode.isprintable():
                                result_input_buffer += event.unicode

            keys = pygame.key.get_pressed()

            if state == STATE_PLAY:
                # Keyboard movement still allowed
                if keys[pygame.K_UP]:    bird_y -= bird_speed
                if keys[pygame.K_DOWN]:  bird_y += bird_speed
                if keys[pygame.K_LEFT]:  bird_x -= bird_speed
                if keys[pygame.K_RIGHT]: bird_x += bird_speed

                # Tap-to-target smooth follow
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

                # Clamp only when not in swarm flight
                if not swarm_active:
                    bird_x, bird_y = clamp_bird(bird_x, bird_y)

                # Spawner
                if current_time - last_cloud_spawn > cloud_spawn_time:
                    cloud_y = random.randint(0, HEIGHT - 60)
                    cloud_size = random.randint(50, 100)
                    cloud_value = random.randint(-10, 10) if cloud_counter < goal else 0

                    # Precompute cloud circles (4–7) with animation parameters
                    num_circles = random.randint(4, 7)
                    circles = []
                    for _ in range(num_circles):
                        radius = random.randint(cloud_size // 4, cloud_size // 2)
                        offset_x = random.randint(-cloud_size // 4, cloud_size // 4)
                        offset_y = random.randint(-cloud_size // 4, cloud_size // 4)

                        # stronger but organic wobble
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

                    clouds.append({
                        'x': WIDTH,
                        'y': cloud_y,
                        'size': cloud_size,
                        'value': cloud_value,
                        'passed': False,
                        'circles': circles,
                        'bob_amp': bob_amp, 'bob_freq': bob_freq,
                        'phase': phase, 't0': t0
                    })

                    if cloud_counter < goal:
                        cloud_entered_counter += 1
                    last_cloud_spawn = current_time

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

                    if cloud_counter < goal and rect_bird.colliderect(rect_cloud):
                        cloud_counter += 1
                        cloud_values_sum += cloud['value']
                        if zwitscher_sound:
                            now = pygame.time.get_ticks()
                            if (now - chirp_last) >= chirp_min_interval:
                                zwitscher_sound.play()
                                chirp_last = now
                        animated_values.append({'x': cloud['x'], 'y': cloud['y'], 'value': cloud['value'],
                                                'size': 30, 'color': RED, 'time_started': pygame.time.get_ticks()})
                        scatter_cloud(cloud['x'], cloud['y'])
                        clouds.remove(cloud)

                # Transition to super and then swarm
                if cloud_counter >= goal and not super_active:
                    super_active = True
                    super_start_time = pygame.time.get_ticks()

                # Failsafe
                if super_active and (current_time - super_start_time) > (super_duration + 5000):
                    super_active = False
                    swarm_active = True

                if super_active:
                    if current_time - super_start_time >= super_duration:
                        super_active = False
                        swarm_active = True
                        # End inputs
                        tap_target_active = False
                        tap_target = None
                        touch_active = False
                        touch_last_pos = None

                if swarm_active:
                    # No inputs / clamps
                    touch_active = False
                    tap_target_active = False
                    tap_target = None

                    # Guaranteed fly-out to the right
                    bird_x += max(swarm_speed, 3.0)
                    # Check based on screen position (incl. offset)
                    bird_screen_x = bird_x + BIRD_DRAW_OFFSET_X
                    if bird_screen_x > (WIDTH + 80):
                        bird_x = WIDTH + 80 - BIRD_DRAW_OFFSET_X
                        result_input_buffer = ""
                        result_text = ""
                        state = STATE_RESULT
                        notify_state("result")

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

            if state in (STATE_START, STATE_GOAL_INPUT, STATE_PLAY, STATE_RESULT):
                for av in list(animated_values):
                    elapsed = (current_time - av['time_started']) / 1000
                    if elapsed < 1:
                        av['y'] -= -10 * elapsed
                        av['size'] = 30 + (90 * elapsed)
                        r = RED[0] + (YELLOW[0] - RED[0]) * elapsed
                        g = RED[1] + (YELLOW[1] - RED[1]) * elapsed
                        b = RED[2] + (YELLOW[2] - RED[2]) * elapsed
                        av['color'] = (int(r), int(g), int(b))
                        font = pygame.font.Font(None, int(av['size']))
                        value_text = font.render(str(av['value']), True, av['color'])
                        screen.blit(value_text, (av['x'] - value_text.get_width() // 2, av['y'] - value_text.get_height() // 2))
                    else:
                        animated_values.remove(av)

                # Draw clouds (clip)
                for cloud in clouds:
                    if cloud['x'] > WIDTH or (cloud['x'] + cloud['size']) < 0:
                        continue
                    draw_cloud(
                        cloud['x'], cloud['y'], cloud['size'],
                        cloud.get('value', 0),
                        cloud_counter, goal,
                        cloud['circles'],
                        cloud['bob_amp'], cloud['bob_freq'],
                        cloud['phase'], cloud['t0']
                    )

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

            if state == STATE_START:
                suppress_flap_sound = True
                draw_start_screen()
            elif state == STATE_GOAL_INPUT:
                suppress_flap_sound = True
                draw_goal_overlay()
            elif state == STATE_RESULT:
                suppress_flap_sound = True
                draw_result_overlay()

            pygame.display.flip()
            pygame.time.Clock().tick(60)
            await asyncio.sleep(0)

    except Exception as e:
        # Fallback error screen
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
