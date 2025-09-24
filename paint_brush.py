import pygame
import sys
import math
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

#  color palette
class Colors:
    #  colors
    BACKGROUND = (243, 243, 243)  # Light gray background
    SURFACE = (255, 255, 255)     # White surface
    ACCENT = (0, 120, 215)        # Windows blue
    ACCENT_LIGHT = (0, 153, 255)  # Lighter blue
    TEXT = (0, 0, 0)              # Black text
    TEXT_LIGHT = (118, 118, 118)  # Gray text
    BORDER = (225, 225, 225)      # Light border
    TOOLBAR = (250, 250, 250)     # Slightly different toolbar color
    
    # Brush colors 
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (196, 43, 28)
    GREEN = (19, 161, 14)
    BLUE = (0, 120, 215)
    YELLOW = (251, 188, 5)
    PURPLE = (136, 23, 152)
    ORANGE = (247, 99, 12)
    PINK = (227, 0, 140)
    TEAL = (0, 183, 195)

# Constants
WIDTH, HEIGHT = 1000, 900  # Increased height to accommodate canvas
CANVAS_WIDTH, CANVAS_HEIGHT = 900, 500

# Set up the display 
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Paint Brush ")

# Create canvas
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(Colors.WHITE)

# Fonts
try:
    title_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
    header_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
    normal_font = pygame.font.SysFont("Segoe UI", 14)
    small_font = pygame.font.SysFont("Segoe UI", 12)
except:
    # Fallback fonts
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    header_font = pygame.font.SysFont("Arial", 16, bold=True)
    normal_font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)

# Brush properties
brush_color = Colors.BLACK
brush_size = 3
brush_type = "round"  # round, square, spray, marker, eraser
drawing = False
last_pos = None

# Color palette 
colors = [
    Colors.BLACK, Colors.RED, Colors.GREEN, Colors.BLUE, 
    Colors.YELLOW, Colors.PURPLE, Colors.ORANGE, Colors.PINK, Colors.TEAL
]
color_names = ["Black", "Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Pink", "Teal"]

# Brush sizes
brush_sizes = [1, 3, 5, 8, 12, 18]
brush_size_names = ["Fine", "Thin", "Medium", "Thick", "Very Thick", "Extra Thick"]

# Brush types with icons
brush_types = [
    {"name": "Round", "value": "round", "icon": "●"},
    {"name": "Square", "value": "square", "icon": "■"},
    {"name": "Spray", "value": "spray", "icon": "✨"},
    {"name": "Marker", "value": "marker", "icon": "🖍️"},
    {"name": "Eraser", "value": "eraser", "icon": "🧽"}
]

# UI Elements
class Button:
    def __init__(self, x, y, width, height, text, color=Colors.ACCENT, text_color=Colors.WHITE, rounded=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.rounded = rounded
        self.hovered = False
        
    def draw(self, surface):
        # Draw rounded rectangle for Windows 11 style
        if self.rounded:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            if self.hovered:
                pygame.draw.rect(surface, Colors.ACCENT_LIGHT, self.rect, width=2, border_radius=6)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            
        # Draw text
        text_surf = normal_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_hovered(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class ColorButton:
    def __init__(self, x, y, size, color, name):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.name = name
        self.selected = False
        
    def draw(self, surface):
        # Draw color circle with selection indicator
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2 - 2)
        
        if self.selected:
            # Selection indicator (ring around the color)
            pygame.draw.circle(surface, Colors.ACCENT, self.rect.center, self.rect.width//2, width=3)
        else:
            # Border
            pygame.draw.circle(surface, Colors.BORDER, self.rect.center, self.rect.width//2, width=1)
            
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # Calculate distance from center
            dx = pos[0] - self.rect.centerx
            dy = pos[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            return distance <= self.rect.width//2
        return False

class BrushSizeButton:
    def __init__(self, x, y, size, display_size, name):
        self.rect = pygame.Rect(x, y, 60, 40)
        self.size = size
        self.display_size = display_size
        self.name = name
        self.selected = False
        
    def draw(self, surface):
        # Draw button background
        if self.selected:
            pygame.draw.rect(surface, Colors.ACCENT, self.rect, border_radius=4)
            text_color = Colors.WHITE
        else:
            pygame.draw.rect(surface, Colors.SURFACE, self.rect, border_radius=4)
            pygame.draw.rect(surface, Colors.BORDER, self.rect, width=1, border_radius=4)
            text_color = Colors.TEXT
            
        # Draw brush preview
        center_x = self.rect.centerx
        center_y = self.rect.centery - 5
        pygame.draw.circle(surface, Colors.BLACK if not self.selected else Colors.WHITE, 
                          (center_x, center_y), self.display_size)
        
        # Draw size name
        text_surf = small_font.render(self.name, True, text_color)
        text_rect = text_surf.get_rect(center=(center_x, self.rect.bottom - 10))
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class BrushTypeButton:
    def __init__(self, x, y, width, height, brush_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.brush_type = brush_type
        self.selected = False
        
    def draw(self, surface):
        # Draw button background
        if self.selected:
            pygame.draw.rect(surface, Colors.ACCENT, self.rect, border_radius=6)
            text_color = Colors.WHITE
        else:
            pygame.draw.rect(surface, Colors.SURFACE, self.rect, border_radius=6)
            pygame.draw.rect(surface, Colors.BORDER, self.rect, width=1, border_radius=6)
            text_color = Colors.TEXT
            
        # Draw icon and text
        icon_surf = normal_font.render(self.brush_type["icon"], True, text_color)
        icon_rect = icon_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 8))
        surface.blit(icon_surf, icon_rect)
        
        name_surf = small_font.render(self.brush_type["name"], True, text_color)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
        surface.blit(name_surf, name_rect)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Create UI elements
clear_button = Button(WIDTH - 120, 20, 100, 40, "Clear Canvas", Colors.RED)
save_button = Button(WIDTH - 240, 20, 100, 40, "Save", Colors.GREEN)

# Create color buttons
color_buttons = []
for i, (color, name) in enumerate(zip(colors, color_names)):
    color_buttons.append(ColorButton(20 + i*70, 80, 40, color, name))

# Create brush size buttons
brush_size_buttons = []
for i, (size, name) in enumerate(zip(brush_sizes, brush_size_names)):
    brush_size_buttons.append(BrushSizeButton(20 + i*70, 150, size, size//2 + 1, name))

# Create brush type buttons
brush_type_buttons = []
for i, btype in enumerate(brush_types):
    brush_type_buttons.append(BrushTypeButton(20 + i*110, 210, 100, 60, btype))

# Drawing functions
def draw_round_brush(surface, color, start_pos, end_pos, size):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, int(math.hypot(dx, dy)))
    
    for i in range(distance):
        x = int(start_pos[0] + (i/distance) * dx)
        y = int(start_pos[1] + (i/distance) * dy)
        pygame.draw.circle(surface, color, (x, y), size)

def draw_square_brush(surface, color, start_pos, end_pos, size):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, int(math.hypot(dx, dy)))
    
    for i in range(distance):
        x = int(start_pos[0] + (i/distance) * dx)
        y = int(start_pos[1] + (i/distance) * dy)
        pygame.draw.rect(surface, color, (x-size//2, y-size//2, size, size))

def draw_spray_brush(surface, color, start_pos, end_pos, size):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, int(math.hypot(dx, dy)))
    
    for i in range(distance):
        x = int(start_pos[0] + (i/distance) * dx)
        y = int(start_pos[1] + (i/distance) * dy)
        
        # Spray effect
        for _ in range(size * 2):
            angle = pygame.time.get_ticks() % 360
            radius = (pygame.time.get_ticks() % size)
            spray_x = x + int(radius * math.cos(math.radians(angle)))
            spray_y = y + int(radius * math.sin(math.radians(angle)))
            pygame.draw.circle(surface, color, (spray_x, spray_y), 1)

def draw_marker_brush(surface, color, start_pos, end_pos, size):
    # Semi-transparent marker effect
    marker_size = max(2, size)  # Ensure minimum size of 2
    marker_surface = pygame.Surface((marker_size*2, marker_size*2), pygame.SRCALPHA)
    pygame.draw.circle(marker_surface, (*color, 100), (marker_size, marker_size), marker_size)
    
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, int(math.hypot(dx, dy)))
    
    # Fix: Ensure step is at least 1
    step = max(1, size // 2)
    for i in range(0, distance, step):
        x = int(start_pos[0] + (i/distance) * dx)
        y = int(start_pos[1] + (i/distance) * dy)
        surface.blit(marker_surface, (x-marker_size, y-marker_size))

def save_canvas():
    # Create saves directory if it doesn't exist
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    # Generate filename with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saves/painting_{timestamp}.png"
    
    try:
        pygame.image.save(canvas, filename)
        print(f"Canvas saved as {filename}")
        return True
    except Exception as e:
        print(f"Error saving canvas: {e}")
        return False

# Initialize selected buttons
color_buttons[0].selected = True  # Black selected by default
brush_size_buttons[1].selected = True  # Size 3 selected by default
brush_type_buttons[0].selected = True  # Round brush selected by default

# Main game loop
clock = pygame.time.Clock()

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        # Update button hover states
        clear_button.is_hovered(mouse_pos)
        save_button.is_hovered(mouse_pos)
        
        # Handle button clicks
        if clear_button.is_clicked(mouse_pos, event):
            canvas.fill(Colors.WHITE)
            
        if save_button.is_clicked(mouse_pos, event):
            if save_canvas():
                # Show save confirmation (you could add a visual indicator)
                pass
        
        # Handle color selection
        for button in color_buttons:
            if button.is_clicked(mouse_pos, event):
                for b in color_buttons:
                    b.selected = False
                button.selected = True
                brush_color = button.color
        
        # Handle brush size selection
        for button in brush_size_buttons:
            if button.is_clicked(mouse_pos, event):
                for b in brush_size_buttons:
                    b.selected = False
                button.selected = True
                brush_size = button.size
        
        # Handle brush type selection
        for button in brush_type_buttons:
            if button.is_clicked(mouse_pos, event):
                for b in brush_type_buttons:
                    b.selected = False
                button.selected = True
                brush_type = button.brush_type["value"]
        
        # Handle drawing
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if clicking on canvas area
                canvas_rect = pygame.Rect(50, 300, CANVAS_WIDTH, CANVAS_HEIGHT)
                if canvas_rect.collidepoint(mouse_pos):
                    drawing = True
                    # Adjust coordinates for canvas
                    canvas_pos = (mouse_pos[0] - 50, mouse_pos[1] - 300)
                    last_pos = canvas_pos
        
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                last_pos = None
        
        elif event.type == MOUSEMOTION:
            if drawing and last_pos is not None:
                canvas_rect = pygame.Rect(50, 300, CANVAS_WIDTH, CANVAS_HEIGHT)
                if canvas_rect.collidepoint(mouse_pos):
                    # Adjust coordinates for canvas
                    canvas_pos = (mouse_pos[0] - 50, mouse_pos[1] - 300)
                    
                    # Use eraser if selected
                    current_color = Colors.WHITE if brush_type == "eraser" else brush_color
                    
                    if brush_type == "round" or brush_type == "eraser":
                        draw_round_brush(canvas, current_color, last_pos, canvas_pos, brush_size)
                    elif brush_type == "square":
                        draw_square_brush(canvas, current_color, last_pos, canvas_pos, brush_size)
                    elif brush_type == "spray":
                        draw_spray_brush(canvas, current_color, last_pos, canvas_pos, brush_size)
                    elif brush_type == "marker":
                        draw_marker_brush(canvas, current_color, last_pos, canvas_pos, brush_size)
                    
                    last_pos = canvas_pos
    
    # Draw everything
    screen.fill(Colors.BACKGROUND)
    
    # Draw title bar
    pygame.draw.rect(screen, Colors.SURFACE, (0, 0, WIDTH, 60))
    title_text = title_font.render("Paint Brush - Windows 11 Style", True, Colors.TEXT)
    screen.blit(title_text, (20, 20))
    
    # Draw toolbar
    pygame.draw.rect(screen, Colors.TOOLBAR, (0, 60, WIDTH, 200), border_radius=10)
    pygame.draw.rect(screen, Colors.BORDER, (0, 60, WIDTH, 200), width=1, border_radius=10)
    
    # Draw section headers
    colors_text = header_font.render("Colors", True, Colors.TEXT)
    screen.blit(colors_text, (20, 60))
    
    brush_size_text = header_font.render("Brush Size", True, Colors.TEXT)
    screen.blit(brush_size_text, (20, 130))
    
    brush_type_text = header_font.render("Brush Type", True, Colors.TEXT)
    screen.blit(brush_type_text, (20, 200))
    
    # Draw buttons
    clear_button.draw(screen)
    save_button.draw(screen)
    
    # Draw color buttons
    for button in color_buttons:
        button.draw(screen)
    
    # Draw brush size buttons
    for button in brush_size_buttons:
        button.draw(screen)
    
    # Draw brush type buttons
    for button in brush_type_buttons:
        button.draw(screen)
    
    # Draw canvas area
    pygame.draw.rect(screen, Colors.SURFACE, (50, 300, CANVAS_WIDTH, CANVAS_HEIGHT), border_radius=8)
    pygame.draw.rect(screen, Colors.BORDER, (50, 300, CANVAS_WIDTH, CANVAS_HEIGHT), width=2, border_radius=8)
    
    # Draw canvas content
    screen.blit(canvas, (50, 300))
    
    # Draw current brush info
    brush_info = f"Current: {brush_type.capitalize()} Brush, Size: {brush_size}"
    info_text = normal_font.render(brush_info, True, Colors.TEXT_LIGHT)
    screen.blit(info_text, (50, 820))
    
    # Draw help text
    help_text = small_font.render("Tip: Use different brush types and sizes for various effects", True, Colors.TEXT_LIGHT)
    screen.blit(help_text, (50, 850))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()