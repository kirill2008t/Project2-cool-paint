import pygame
import sys
from datetime import datetime
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_SIZE = 35
BUTTON_MARGIN = 8
PANEL_HEIGHT = BUTTON_SIZE + BUTTON_MARGIN * 2 + 25

COLORS = [
    ('red', (255, 50, 50)),
    ('green', (50, 255, 50)),
    ('blue', (50, 50, 255)),
    ('yellow', (255, 255, 50)),
    ('black', (30, 30, 30))
]

MODE_FREE = 0
MODE_RECT = 1
MODE_ELLIPSE = 2
MODE_LINE = 3
MODE_ERASER = 4

class CoolPaint:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + PANEL_HEIGHT))
        pygame.display.set_caption("coolpaint")
        
        self.save_folder = "saved_drawings"
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.canvas.fill(WHITE)
        
        self.current_color = BLACK
        self.drawing = False
        self.last_pos = None
        self.brush_size = 3
        self.eraser_size = 25
        
        self.shape_start_pos = None
        self.shape_end_pos = None
        self.drawing_shape = False
        self.current_mode = MODE_FREE
        
        self.panel_collapsed = False
        
        self.save_message = None
        self.save_message_time = 0
        
        self.buttons = []
        self.shape_buttons = []
        self.clear_button = None
        self.collapse_button = None
        self.save_button = None
        self.eraser_button = None
        self.create_buttons()
        
        self.font = pygame.font.Font(None, 18)
        self.big_font = pygame.font.Font(None, 36)
        
    def create_buttons(self):
        self.buttons = []
        self.shape_buttons = []
        
        save_x = BUTTON_MARGIN
        save_y = HEIGHT + BUTTON_MARGIN
        self.save_button = {
            'rect': pygame.Rect(save_x, save_y, BUTTON_SIZE, BUTTON_SIZE),
            'hover': False
        }
        
        collapse_x = save_x + BUTTON_SIZE + BUTTON_MARGIN
        collapse_y = HEIGHT + BUTTON_MARGIN
        self.collapse_button = {
            'rect': pygame.Rect(collapse_x, collapse_y, BUTTON_SIZE, BUTTON_SIZE),
            'hover': False
        }
        
        eraser_x = collapse_x + BUTTON_SIZE + BUTTON_MARGIN
        eraser_y = HEIGHT + BUTTON_MARGIN
        self.eraser_button = {
            'rect': pygame.Rect(eraser_x, eraser_y, BUTTON_SIZE, BUTTON_SIZE),
            'hover': False,
            'selected': False
        }
        
        shapes = [
            ('free', MODE_FREE, "Свободное рисование"),
            ('rect', MODE_RECT, "Прямоугольник"),
            ('ellipse', MODE_ELLIPSE, "Эллипс"),
            ('line', MODE_LINE, "Линия")
        ]
        
        shape_start_x = eraser_x + BUTTON_SIZE + BUTTON_MARGIN
        for i, (shape_name, mode, tooltip) in enumerate(shapes):
            x = shape_start_x + i * (BUTTON_SIZE + BUTTON_MARGIN)
            y = HEIGHT + BUTTON_MARGIN
            button_rect = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
            
            self.shape_buttons.append({
                'rect': button_rect,
                'mode': mode,
                'name': shape_name,
                'tooltip': tooltip,
                'hover': False,
                'selected': (mode == MODE_FREE)
            })
        
        colors_start_x = shape_start_x + len(shapes) * (BUTTON_SIZE + BUTTON_MARGIN)
        for i, (color_name, color_value) in enumerate(COLORS):
            x = colors_start_x + i * (BUTTON_SIZE + BUTTON_MARGIN)
            y = HEIGHT + BUTTON_MARGIN
            button_rect = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
            
            self.buttons.append({
                'rect': button_rect,
                'color': color_value,
                'name': color_name,
                'hover': False,
                'selected': (color_name == 'black')
            })
        
        clear_x = WIDTH - BUTTON_SIZE - BUTTON_MARGIN
        clear_y = HEIGHT + BUTTON_MARGIN
        self.clear_button = {
            'rect': pygame.Rect(clear_x, clear_y, BUTTON_SIZE, BUTTON_SIZE),
            'hover': False
        }
    
    def draw_rounded_rect(self, surface, color, rect, radius=6):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_icon_save(self, rect):
        center_x = rect.centerx
        center_y = rect.centery
        
        pygame.draw.rect(self.screen, WHITE, 
                        (center_x - 10, center_y - 7, 20, 14), 2)
        pygame.draw.rect(self.screen, WHITE,
                        (center_x - 5, center_y - 7, 10, 4), 2)
        pygame.draw.rect(self.screen, WHITE,
                        (center_x + 3, center_y - 3, 5, 5), 1)
        pygame.draw.circle(self.screen, WHITE,
                          (center_x - 5, center_y + 2), 2, 1)
    
    def draw_icon_eraser(self, rect, selected):
        center_x = rect.centerx
        center_y = rect.centery
        
        if selected:
            color = (255, 100, 100)
        else:
            color = (100, 100, 100)
        
        pygame.draw.rect(self.screen, color,
                        (center_x - 10, center_y - 8, 20, 16), 2)
        pygame.draw.rect(self.screen, (255, 150, 150),
                        (center_x - 8, center_y - 6, 16, 12))
        pygame.draw.line(self.screen, (200, 200, 200),
                        (center_x - 6, center_y),
                        (center_x + 6, center_y), 2)
        pygame.draw.circle(self.screen, (255, 200, 200),
                          (center_x - 3, center_y - 2), 2)
        pygame.draw.circle(self.screen, (255, 200, 200),
                          (center_x + 3, center_y + 1), 1)
    
    def draw_icon_collapse(self, rect, collapsed):
        center_x = rect.centerx
        center_y = rect.centery
        
        if collapsed:
            points = [
                (center_x - 7, center_y - 3),
                (center_x, center_y + 4),
                (center_x + 7, center_y - 3)
            ]
        else:
            points = [
                (center_x - 7, center_y + 3),
                (center_x, center_y - 4),
                (center_x + 7, center_y + 3)
            ]
        
        pygame.draw.polygon(self.screen, (80, 80, 80), points)
    
    def draw_icon_clear(self, rect):
        center_x = rect.centerx
        center_y = rect.centery
        
        pygame.draw.rect(self.screen, WHITE,
                        (center_x - 10, center_y - 8, 20, 5), 2)
        pygame.draw.arc(self.screen, WHITE,
                       (center_x - 6, center_y - 12, 12, 8), 0, 3.14, 2)
        pygame.draw.rect(self.screen, WHITE,
                        (center_x - 8, center_y - 4, 16, 12), 2)
        pygame.draw.line(self.screen, WHITE,
                        (center_x - 4, center_y - 2),
                        (center_x - 4, center_y + 6), 1)
        pygame.draw.line(self.screen, WHITE,
                        (center_x, center_y - 2),
                        (center_x, center_y + 6), 1)
        pygame.draw.line(self.screen, WHITE,
                        (center_x + 4, center_y - 2),
                        (center_x + 4, center_y + 6), 1)
    
    def draw_icon_color(self, rect, color, name):
        center_x = rect.centerx
        center_y = rect.centery
        
        pygame.draw.circle(self.screen, color, (center_x, center_y), 12)
        pygame.draw.circle(self.screen, (50, 50, 50), (center_x, center_y), 12, 2)
        
        if name == 'black':
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 4)
    
    def draw_icon_shape(self, rect, mode):
        center_x = rect.centerx
        center_y = rect.centery
        
        if mode == MODE_FREE:
            pygame.draw.line(self.screen, (50, 50, 50),
                           (center_x - 8, center_y + 6),
                           (center_x + 6, center_y - 8), 3)
            pygame.draw.circle(self.screen, (50, 50, 50),
                             (center_x + 6, center_y - 8), 2)
        elif mode == MODE_RECT:
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (center_x - 9, center_y - 7, 18, 14), 2)
        elif mode == MODE_ELLIPSE:
            pygame.draw.ellipse(self.screen, (50, 50, 50),
                              (center_x - 9, center_y - 7, 18, 14), 2)
        elif mode == MODE_LINE:
            pygame.draw.line(self.screen, (50, 50, 50),
                           (center_x - 9, center_y + 7),
                           (center_x + 9, center_y - 7), 3)
    
    def draw_save_button(self):
        rect = self.save_button['rect']
        
        if self.save_button['hover']:
            bg_color = (100, 150, 100)
        else:
            bg_color = (70, 130, 70)
        
        self.draw_rounded_rect(self.screen, bg_color, rect, radius=6)
        pygame.draw.rect(self.screen, (50, 100, 50), rect, 2, border_radius=6)
        self.draw_icon_save(rect)
    
    def draw_eraser_button(self):
        rect = self.eraser_button['rect']
        selected = self.eraser_button['selected']
        
        if selected:
            bg_color = (255, 150, 150)
            self.draw_rounded_rect(self.screen, bg_color, rect, radius=6)
            pygame.draw.rect(self.screen, (255, 50, 50), rect, 2, border_radius=6)
        else:
            if self.eraser_button['hover']:
                bg_color = (230, 230, 230)
            else:
                bg_color = (220, 220, 220)
            self.draw_rounded_rect(self.screen, bg_color, rect, radius=6)
            pygame.draw.rect(self.screen, (150, 150, 150), rect, 2, border_radius=6)
        
        self.draw_icon_eraser(rect, selected)
    
    def draw_shape_buttons(self):
        for button in self.shape_buttons:
            if button['selected']:
                bg_color = (180, 180, 220)
                self.draw_rounded_rect(self.screen, bg_color, button['rect'], radius=6)
                pygame.draw.rect(self.screen, (100, 100, 200), button['rect'], 2, border_radius=6)
            else:
                bg_color = (220, 220, 220)
                self.draw_rounded_rect(self.screen, bg_color, button['rect'], radius=6)
                
                if button['hover']:
                    pygame.draw.rect(self.screen, (150, 150, 150), button['rect'], 2, border_radius=6)
            
            self.draw_icon_shape(button['rect'], button['mode'])
            
            mouse_pos = pygame.mouse.get_pos()
            if button['rect'].collidepoint(mouse_pos):
                self.show_tooltip(button['tooltip'], button['rect'].centerx, button['rect'].y)
    
    def draw_buttons(self):
        if self.panel_collapsed:
            panel_height = BUTTON_SIZE + BUTTON_MARGIN * 2
        else:
            panel_height = PANEL_HEIGHT
        
        panel_rect = pygame.Rect(0, HEIGHT, WIDTH, panel_height)
        self.draw_rounded_rect(self.screen, (240, 240, 240), panel_rect, radius=0)
        pygame.draw.line(self.screen, (180, 180, 180), (0, HEIGHT), (WIDTH, HEIGHT), 2)
        
        self.draw_save_button()
        self.draw_collapse_button()
        self.draw_eraser_button()
        
        if not self.panel_collapsed:
            self.draw_shape_buttons()
            
            for button in self.buttons:
                if button['selected']:
                    self.draw_rounded_rect(self.screen, (200, 200, 200), button['rect'], radius=6)
                    pygame.draw.rect(self.screen, (100, 100, 200), button['rect'], 2, border_radius=6)
                else:
                    self.draw_rounded_rect(self.screen, (240, 240, 240), button['rect'], radius=6)
                    if button['hover']:
                        pygame.draw.rect(self.screen, (180, 180, 180), button['rect'], 2, border_radius=6)
                
                self.draw_icon_color(button['rect'], button['color'], button['name'])
            
            clear_rect = self.clear_button['rect']
            if self.clear_button['hover']:
                bg_color = (130, 130, 130)
            else:
                bg_color = (100, 100, 100)
            
            self.draw_rounded_rect(self.screen, bg_color, clear_rect, radius=6)
            pygame.draw.rect(self.screen, (70, 70, 70), clear_rect, 2, border_radius=6)
            self.draw_icon_clear(clear_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.show_tooltip(button['name'].capitalize(), button['rect'].centerx, button['rect'].y)
            
            if self.clear_button['rect'].collidepoint(mouse_pos):
                self.show_tooltip("Очистить всё", clear_rect.centerx, clear_rect.y)
            
            info_y = HEIGHT + BUTTON_SIZE + BUTTON_MARGIN + 5
            info_height = 20
            
            info_bg = pygame.Rect(0, info_y - 2, WIDTH, info_height + 4)
            pygame.draw.rect(self.screen, (240, 240, 240), info_bg)
            
            if self.current_mode == MODE_ERASER:
                mode_text = "Режим: Ластик"
                mode_color = (200, 50, 50)
            else:
                mode_texts = {
                    MODE_FREE: "Режим: Свободное рисование",
                    MODE_RECT: "Режим: Прямоугольник",
                    MODE_ELLIPSE: "Режим: Эллипс",
                    MODE_LINE: "Режим: Линия"
                }
                mode_text = mode_texts[self.current_mode]
                mode_color = (80, 80, 80)
            
            mode_surface = self.font.render(mode_text, True, mode_color)
            self.screen.blit(mode_surface, (BUTTON_MARGIN, info_y))
            
            hotkey_text = "Горячие клавиши: 1-4 - режимы, E - ластик"
            hotkey_surface = self.font.render(hotkey_text, True, (120, 120, 120))
            hotkey_rect = hotkey_surface.get_rect(midright=(WIDTH - BUTTON_MARGIN, info_y + 5))
            self.screen.blit(hotkey_surface, hotkey_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        if self.save_button['rect'].collidepoint(mouse_pos):
            self.show_tooltip("Сохранить рисунок (Ctrl+S)", self.save_button['rect'].centerx, self.save_button['rect'].y)
        
        if self.collapse_button['rect'].collidepoint(mouse_pos):
            tip_text = "Развернуть панель" if self.panel_collapsed else "Свернуть панель"
            self.show_tooltip(tip_text, self.collapse_button['rect'].centerx, self.collapse_button['rect'].y)
        
        if self.eraser_button['rect'].collidepoint(mouse_pos):
            self.show_tooltip("Ластик (E)", self.eraser_button['rect'].centerx, self.eraser_button['rect'].y)
        
        if self.save_message and pygame.time.get_ticks() - self.save_message_time < 2000:
            message_surface = self.big_font.render(self.save_message, True, (50, 50, 50))
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            bg_rect = message_rect.inflate(40, 20)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((255, 255, 200, 230))
            self.screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, 2, border_radius=8)
            
            self.screen.blit(message_surface, message_rect)
        elif self.save_message:
            self.save_message = None
    
    def show_tooltip(self, text, x, y):
        tooltip = self.font.render(text, True, (50, 50, 50))
        tooltip_rect = tooltip.get_rect(center=(x, y - 15))
        
        if tooltip_rect.left < 0:
            tooltip_rect.left = 5
        if tooltip_rect.right > WIDTH:
            tooltip_rect.right = WIDTH - 5
        if tooltip_rect.top < 0:
            tooltip_rect.top = 5
            
        tooltip_bg = tooltip.get_rect()
        tooltip_bg.inflate_ip(8, 4)
        tooltip_bg.center = tooltip_rect.center
        pygame.draw.rect(self.screen, (255, 255, 200), tooltip_bg, border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 100), tooltip_bg, 1, border_radius=4)
        self.screen.blit(tooltip, tooltip_rect)
    
    def draw_collapse_button(self):
        rect = self.collapse_button['rect']
        
        if self.collapse_button['hover']:
            bg_color = (200, 200, 200)
        else:
            bg_color = (220, 220, 220)
        
        self.draw_rounded_rect(self.screen, bg_color, rect, radius=6)
        pygame.draw.rect(self.screen, (150, 150, 150), rect, 2, border_radius=6)
        self.draw_icon_collapse(rect, self.panel_collapsed)
    
    def clear_canvas(self):
        self.canvas.fill(WHITE)
    
    def draw_line(self, start, end, color, width):
        if start and end:
            pygame.draw.line(self.canvas, color, start, end, width)
    
    def draw_rectangle(self, start, end, color):
        if start and end:
            x = min(start[0], end[0])
            y = min(start[1], end[1])
            width = abs(start[0] - end[0])
            height = abs(start[1] - end[1])
            if width > 0 and height > 0:
                pygame.draw.rect(self.canvas, color, (x, y, width, height), self.brush_size)
    
    def draw_ellipse(self, start, end, color):
        if start and end:
            x = min(start[0], end[0])
            y = min(start[1], end[1])
            width = abs(start[0] - end[0])
            height = abs(start[1] - end[1])
            if width > 0 and height > 0:
                pygame.draw.ellipse(self.canvas, color, (x, y, width, height), self.brush_size)
    
    def draw_line_shape(self, start, end, color):
        if start and end:
            pygame.draw.line(self.canvas, color, start, end, self.brush_size)
    
    def draw_shape_preview(self):
        if self.drawing_shape and self.shape_start_pos and self.shape_end_pos:
            temp_surface = self.canvas.copy()
            
            if self.current_mode == MODE_RECT:
                x = min(self.shape_start_pos[0], self.shape_end_pos[0])
                y = min(self.shape_start_pos[1], self.shape_end_pos[1])
                width = abs(self.shape_start_pos[0] - self.shape_end_pos[0])
                height = abs(self.shape_start_pos[1] - self.shape_end_pos[1])
                if width > 0 and height > 0:
                    pygame.draw.rect(temp_surface, self.current_color, (x, y, width, height), self.brush_size)
            elif self.current_mode == MODE_ELLIPSE:
                x = min(self.shape_start_pos[0], self.shape_end_pos[0])
                y = min(self.shape_start_pos[1], self.shape_end_pos[1])
                width = abs(self.shape_start_pos[0] - self.shape_end_pos[0])
                height = abs(self.shape_start_pos[1] - self.shape_end_pos[1])
                if width > 0 and height > 0:
                    pygame.draw.ellipse(temp_surface, self.current_color, (x, y, width, height), self.brush_size)
            elif self.current_mode == MODE_LINE:
                pygame.draw.line(temp_surface, self.current_color, self.shape_start_pos, self.shape_end_pos, self.brush_size)
            
            self.screen.blit(temp_surface, (0, 0))
    
    def save_canvas(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drawing_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)
            
            pygame.image.save(self.canvas, filepath)
            
            self.save_message = f"Сохранено: {filename}"
            self.save_message_time = pygame.time.get_ticks()
            
            print(f"Рисунок сохранен: {filepath}")
            
        except Exception as e:
            self.save_message = f"Ошибка сохранения!"
            self.save_message_time = pygame.time.get_ticks()
            print(f"Ошибка при сохранении: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_canvas()
                elif event.key == pygame.K_F2:
                    self.save_canvas()
                elif event.key == pygame.K_1:
                    self.set_mode(MODE_FREE)
                elif event.key == pygame.K_2:
                    self.set_mode(MODE_RECT)
                elif event.key == pygame.K_3:
                    self.set_mode(MODE_ELLIPSE)
                elif event.key == pygame.K_4:
                    self.set_mode(MODE_LINE)
                elif event.key == pygame.K_e:
                    self.set_mode(MODE_ERASER)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.save_button['rect'].collidepoint(mouse_pos):
                    self.save_canvas()
                    continue
                
                if self.collapse_button['rect'].collidepoint(mouse_pos):
                    self.panel_collapsed = not self.panel_collapsed
                    continue
                
                if self.eraser_button['rect'].collidepoint(mouse_pos):
                    if self.current_mode == MODE_ERASER:
                        self.set_mode(MODE_FREE)
                    else:
                        self.set_mode(MODE_ERASER)
                    continue
                
                if self.panel_collapsed:
                    continue
                
                for button in self.shape_buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        self.set_mode(button['mode'])
                        break
                
                if self.clear_button['rect'].collidepoint(mouse_pos):
                    self.clear_canvas()
                    continue
                
                for button in self.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        self.current_color = button['color']
                        for btn in self.buttons:
                            btn['selected'] = False
                        button['selected'] = True
                        if self.current_mode == MODE_ERASER:
                            self.set_mode(MODE_FREE)
                        break
                
                if mouse_pos[1] < HEIGHT:
                    if event.button == 1:
                        if self.current_mode == MODE_ERASER:
                            self.drawing = True
                            self.last_pos = mouse_pos
                        elif self.current_mode == MODE_FREE:
                            self.drawing = True
                            self.last_pos = mouse_pos
                        else:
                            self.drawing_shape = True
                            self.shape_start_pos = mouse_pos
                            self.shape_end_pos = mouse_pos
            
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                self.save_button['hover'] = self.save_button['rect'].collidepoint(mouse_pos)
                self.collapse_button['hover'] = self.collapse_button['rect'].collidepoint(mouse_pos)
                self.eraser_button['hover'] = self.eraser_button['rect'].collidepoint(mouse_pos)
                
                if not self.panel_collapsed:
                    for button in self.shape_buttons:
                        button['hover'] = button['rect'].collidepoint(mouse_pos)
                    for button in self.buttons:
                        button['hover'] = button['rect'].collidepoint(mouse_pos)
                    self.clear_button['hover'] = self.clear_button['rect'].collidepoint(mouse_pos)
                
                if self.drawing and mouse_pos[1] < HEIGHT:
                    if self.current_mode == MODE_ERASER:
                        self.draw_line(self.last_pos, mouse_pos, WHITE, self.eraser_size)
                    else:
                        self.draw_line(self.last_pos, mouse_pos, self.current_color, self.brush_size)
                    self.last_pos = mouse_pos
                elif self.drawing_shape and mouse_pos[1] < HEIGHT:
                    self.shape_end_pos = mouse_pos
            
            if event.type == pygame.MOUSEBUTTONUP:
                if self.drawing_shape and self.shape_start_pos and self.shape_end_pos:
                    if self.current_mode == MODE_RECT:
                        self.draw_rectangle(self.shape_start_pos, self.shape_end_pos, self.current_color)
                    elif self.current_mode == MODE_ELLIPSE:
                        self.draw_ellipse(self.shape_start_pos, self.shape_end_pos, self.current_color)
                    elif self.current_mode == MODE_LINE:
                        self.draw_line_shape(self.shape_start_pos, self.shape_end_pos, self.current_color)
                
                self.drawing = False
                self.drawing_shape = False
                self.shape_start_pos = None
                self.shape_end_pos = None
                self.last_pos = None
        
        return True
    
    def set_mode(self, mode):
        self.current_mode = mode
        
        self.eraser_button['selected'] = (mode == MODE_ERASER)
        
        for button in self.shape_buttons:
            button['selected'] = (button['mode'] == mode)
        
        self.drawing = False
        self.drawing_shape = False
        self.shape_start_pos = None
        self.shape_end_pos = None
        self.last_pos = None
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            
            self.screen.fill(WHITE)
            self.screen.blit(self.canvas, (0, 0))
            
            if self.drawing_shape:
                self.draw_shape_preview()
            
            self.draw_buttons()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    app = CoolPaint()
    app.run()

if __name__ == "__main__":
    main()