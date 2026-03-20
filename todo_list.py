import json
import os
import sys
from dataclasses import dataclass

import pygame


# ---------- Setup ----------
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 980, 680
FPS = 60
DATA_FILE = "todo_data.json"

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("To-Do List")
CLOCK = pygame.time.Clock()


# ---------- Theme ----------
BG = (242, 245, 250)
PANEL = (255, 255, 255)
PANEL_2 = (248, 250, 253)
TEXT = (44, 51, 61)
MUTED = (122, 132, 145)
ACCENT = (88, 101, 242)
ACCENT_HOVER = (70, 83, 223)
SUCCESS = (46, 204, 113)
SUCCESS_HOVER = (38, 184, 99)
DANGER = (235, 87, 87)
DANGER_HOVER = (220, 72, 72)
OUTLINE = (222, 228, 236)
SHADOW = (210, 217, 228)
CHECKED_BG = (236, 247, 240)
INPUT_BG = (250, 251, 253)

TITLE_FONT = pygame.font.SysFont("arial", 34, bold=True)
SUBTITLE_FONT = pygame.font.SysFont("arial", 18)
TEXT_FONT = pygame.font.SysFont("arial", 22)
SMALL_FONT = pygame.font.SysFont("arial", 16)
BUTTON_FONT = pygame.font.SysFont("arial", 18, bold=True)
TASK_FONT = pygame.font.SysFont("arial", 22)
TASK_DONE_FONT = pygame.font.SysFont("arial", 22)
TASK_DONE_FONT.set_strikethrough(True)


# ---------- Storage ----------
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = []
        for item in data:
            if isinstance(item, dict) and "text" in item and "done" in item:
                text = str(item["text"]).strip()
                if text:
                    tasks.append({"text": text, "done": bool(item["done"])})
        return tasks
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


# ---------- Helpers ----------
def draw_rounded_rect(surface, color, rect, radius=16, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius, width=border)


def draw_shadow_card(surface, rect, radius=18):
    shadow_rect = rect.move(0, 6)
    shadow = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (*SHADOW, 65), shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, shadow_rect.topleft)
    pygame.draw.rect(surface, PANEL, rect, border_radius=radius)
    pygame.draw.rect(surface, OUTLINE, rect, width=1, border_radius=radius)


def render_text(text, font, color):
    return font.render(text, True, color)


def truncate_text(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text
    trimmed = text
    while trimmed and font.size(trimmed + "...")[0] > max_width:
        trimmed = trimmed[:-1]
    return trimmed + "..."


# ---------- UI Components ----------
@dataclass
class Button:
    rect: pygame.Rect
    label: str
    base_color: tuple
    hover_color: tuple
    text_color: tuple = (255, 255, 255)
    enabled: bool = True

    def draw(self, surface, mouse_pos):
        color = self.base_color
        if self.enabled and self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        if not self.enabled:
            color = (180, 187, 197)

        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        label_surf = BUTTON_FONT.render(self.label, True, self.text_color)
        label_rect = label_surf.get_rect(center=self.rect.center)
        surface.blit(label_surf, label_rect)

    def is_clicked(self, event):
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class TextInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = 90

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "submit"
            elif event.key == pygame.K_ESCAPE:
                self.text = ""
            else:
                if len(self.text) < self.max_length and event.unicode.isprintable() and event.unicode not in "\r\n\t":
                    self.text += event.unicode
        return None

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface):
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=16)
        pygame.draw.rect(surface, ACCENT if self.active else OUTLINE, self.rect, width=2, border_radius=16)

        display_text = self.text if self.text else "Add a new task..."
        color = TEXT if self.text else MUTED
        text_surf = TEXT_FONT.render(display_text, True, color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 16, self.rect.centery))
        surface.blit(text_surf, text_rect)

        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            if self.text:
                pygame.draw.line(surface, TEXT, (cursor_x, self.rect.y + 12), (cursor_x, self.rect.bottom - 12), 2)


class TodoApp:
    def __init__(self):
        self.tasks = load_tasks()
        self.scroll_offset = 0
        self.input_box = TextInput((40, 118, 590, 52))

        self.add_button = Button(pygame.Rect(648, 118, 120, 52), "Add", ACCENT, ACCENT_HOVER)
        self.clear_done_button = Button(pygame.Rect(782, 118, 158, 52), "Clear Done", DANGER, DANGER_HOVER)

        self.list_rect = pygame.Rect(40, 194, 900, 440)
        self.task_height = 62
        self.task_gap = 12

    def add_task(self):
        text = self.input_box.text.strip()
        if not text:
            return
        self.tasks.insert(0, {"text": text, "done": False})
        self.input_box.text = ""
        self.scroll_offset = 0
        save_tasks(self.tasks)

    def clear_done(self):
        self.tasks = [task for task in self.tasks if not task["done"]]
        self.scroll_offset = 0
        save_tasks(self.tasks)

    def toggle_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = not self.tasks[index]["done"]
            save_tasks(self.tasks)

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            save_tasks(self.tasks)
            max_scroll = max(0, self.content_height() - self.list_rect.height)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def content_height(self):
        if not self.tasks:
            return 0
        return len(self.tasks) * (self.task_height + self.task_gap) - self.task_gap

    def scroll(self, amount):
        max_scroll = max(0, self.content_height() - self.list_rect.height)
        self.scroll_offset = max(0, min(self.scroll_offset + amount, max_scroll))

    def handle_event(self, event):
        result = self.input_box.handle_event(event)
        if result == "submit":
            self.add_task()

        if self.add_button.is_clicked(event):
            self.add_task()
        if self.clear_done_button.is_clicked(event):
            self.clear_done()

        if event.type == pygame.MOUSEWHEEL:
            self.scroll(-event.y * 32)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll(-32)
            elif event.key == pygame.K_DOWN:
                self.scroll(32)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_task_click(event.pos)

    def handle_task_click(self, mouse_pos):
        if not self.list_rect.collidepoint(mouse_pos):
            return

        base_y = self.list_rect.y - self.scroll_offset
        for i, task in enumerate(self.tasks):
            y = base_y + i * (self.task_height + self.task_gap)
            task_rect = pygame.Rect(self.list_rect.x + 14, y, self.list_rect.width - 28, self.task_height)
            if not task_rect.collidepoint(mouse_pos):
                continue

            checkbox_rect = pygame.Rect(task_rect.x + 16, task_rect.y + 16, 30, 30)
            delete_rect = pygame.Rect(task_rect.right - 86, task_rect.y + 13, 70, 36)

            if delete_rect.collidepoint(mouse_pos):
                self.delete_task(i)
            elif checkbox_rect.collidepoint(mouse_pos) or task_rect.collidepoint(mouse_pos):
                self.toggle_task(i)
            break

    def update(self):
        self.input_box.update()
        self.clear_done_button.enabled = any(task["done"] for task in self.tasks)

    def draw_header(self):
        title = render_text("My To-Do List", TITLE_FONT, TEXT)
        subtitle = render_text(
            f"{sum(not t['done'] for t in self.tasks)} active • {sum(t['done'] for t in self.tasks)} completed",
            SUBTITLE_FONT,
            MUTED,
        )
        SCREEN.blit(title, (40, 34))
        SCREEN.blit(subtitle, (42, 74))

    def draw_input_area(self):
        self.input_box.draw(SCREEN)
        mouse_pos = pygame.mouse.get_pos()
        self.add_button.draw(SCREEN, mouse_pos)
        self.clear_done_button.draw(SCREEN, mouse_pos)

    def draw_list(self):
        draw_shadow_card(SCREEN, self.list_rect, radius=22)

        clip_rect = self.list_rect.inflate(-8, -8)
        previous_clip = SCREEN.get_clip()
        SCREEN.set_clip(clip_rect)

        if not self.tasks:
            empty_title = render_text("No tasks yet", TEXT_FONT, TEXT)
            empty_sub = render_text("Type something above and press Add.", SUBTITLE_FONT, MUTED)
            SCREEN.blit(empty_title, empty_title.get_rect(center=(self.list_rect.centerx, self.list_rect.centery - 10)))
            SCREEN.blit(empty_sub, empty_sub.get_rect(center=(self.list_rect.centerx, self.list_rect.centery + 20)))
        else:
            base_y = self.list_rect.y + 14 - self.scroll_offset
            for i, task in enumerate(self.tasks):
                y = base_y + i * (self.task_height + self.task_gap)
                task_rect = pygame.Rect(self.list_rect.x + 14, y, self.list_rect.width - 28, self.task_height)

                if task_rect.bottom < self.list_rect.top or task_rect.top > self.list_rect.bottom:
                    continue

                bg_color = CHECKED_BG if task["done"] else PANEL_2
                pygame.draw.rect(SCREEN, bg_color, task_rect, border_radius=16)
                pygame.draw.rect(SCREEN, OUTLINE, task_rect, width=1, border_radius=16)

                checkbox_rect = pygame.Rect(task_rect.x + 16, task_rect.y + 16, 30, 30)
                pygame.draw.rect(SCREEN, (255, 255, 255), checkbox_rect, border_radius=10)
                pygame.draw.rect(SCREEN, SUCCESS if task["done"] else OUTLINE, checkbox_rect, width=2, border_radius=10)
                if task["done"]:
                    pygame.draw.line(SCREEN, SUCCESS, (checkbox_rect.x + 7, checkbox_rect.y + 16), (checkbox_rect.x + 13, checkbox_rect.y + 22), 3)
                    pygame.draw.line(SCREEN, SUCCESS, (checkbox_rect.x + 13, checkbox_rect.y + 22), (checkbox_rect.x + 23, checkbox_rect.y + 9), 3)

                delete_rect = pygame.Rect(task_rect.right - 86, task_rect.y + 13, 70, 36)
                mouse_pos = pygame.mouse.get_pos()
                delete_color = DANGER_HOVER if delete_rect.collidepoint(mouse_pos) else DANGER
                pygame.draw.rect(SCREEN, delete_color, delete_rect, border_radius=12)
                delete_label = SMALL_FONT.render("Delete", True, (255, 255, 255))
                SCREEN.blit(delete_label, delete_label.get_rect(center=delete_rect.center))

                font = TASK_DONE_FONT if task["done"] else TASK_FONT
                text_color = MUTED if task["done"] else TEXT
                task_text = truncate_text(task["text"], font, task_rect.width - 190)
                text_surf = font.render(task_text, True, text_color)
                text_rect = text_surf.get_rect(midleft=(checkbox_rect.right + 14, task_rect.centery))
                SCREEN.blit(text_surf, text_rect)

        SCREEN.set_clip(previous_clip)
        self.draw_scrollbar()

    def draw_scrollbar(self):
        content_h = self.content_height()
        visible_h = self.list_rect.height
        if content_h <= visible_h or content_h == 0:
            return

        track_rect = pygame.Rect(self.list_rect.right - 10, self.list_rect.y + 16, 6, self.list_rect.height - 32)
        pygame.draw.rect(SCREEN, (230, 235, 241), track_rect, border_radius=8)

        thumb_h = max(50, int(track_rect.height * (visible_h / content_h)))
        max_scroll = content_h - visible_h
        thumb_y = track_rect.y + int((track_rect.height - thumb_h) * (self.scroll_offset / max_scroll))
        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_h)
        pygame.draw.rect(SCREEN, (180, 188, 201), thumb_rect, border_radius=8)

    def draw_footer(self):
        help_text = "Enter = add task   •   Click a task to mark it done   •   Mouse wheel / Up / Down = scroll"
        help_surf = SMALL_FONT.render(help_text, True, MUTED)
        SCREEN.blit(help_surf, help_surf.get_rect(center=(WIDTH // 2, HEIGHT - 24)))

    def draw(self):
        SCREEN.fill(BG)
        self.draw_header()
        self.draw_input_area()
        self.draw_list()
        self.draw_footer()
        pygame.display.flip()


# ---------- Main ----------
def main():
    app = TodoApp()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_tasks(app.tasks)
                pygame.quit()
                sys.exit()
            app.handle_event(event)

        app.update()
        app.draw()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
