import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mimosa Energy Simulation - Sci-Fi Enhanced")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)
NEON_BLUE = (0, 170, 255)
DARK_GRAY = (50, 50, 50)

# Fonts
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 36)

# Plant parameters
plant_radius = 20
num_plants = 20

# Flywheel parameters
flywheel_x, flywheel_y = WIDTH - 150, HEIGHT // 2
flywheel_radius = 70
flywheel_angle = 0
flywheel_speed = 0
max_speed = 20

# Energy level
energy_level = 0
max_energy = num_plants * 10

# Spark particles
sparks = []

# UI Panels
control_panel = pygame.Rect(0, 0, 200, HEIGHT)
simulation_panel = pygame.Rect(200, 0, WIDTH - 200, HEIGHT)
energy_bar_width = simulation_panel.width - 40

# Plant list
plants = []
def add_plants(num):
    for _ in range(num):
        x = random.randint(50, simulation_panel.width - 50)
        y = random.randint(100, simulation_panel.height - 150)
        plants.append({'x': x, 'y': y, 'state': 'open'})

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, screen):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Buttons
start_button = Button(20, HEIGHT - 150, 150, 50, 'Start', CYAN, DARK_GRAY)
stop_button = Button(20, HEIGHT - 90, 150, 50, 'Stop', RED, DARK_GRAY)
add_plant_button = Button(20, HEIGHT - 210, 150, 50, 'Add Plant', GREEN, DARK_GRAY)

# Initialize plants
add_plants(num_plants)

# Main loop
running = True
clock = pygame.time.Clock()
simulation_active = False

while running:
    screen.fill(BLACK)

    # Draw panels
    pygame.draw.rect(screen, DARK_GRAY, control_panel)
    pygame.draw.rect(screen, BLACK, simulation_panel)

    # Draw buttons
    start_button.draw(screen)
    stop_button.draw(screen)
    add_plant_button.draw(screen)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif start_button.is_clicked(event):
            simulation_active = True
        elif stop_button.is_clicked(event):
            simulation_active = False
        elif add_plant_button.is_clicked(event):
            add_plants(1)
            max_energy = len(plants) * 10  # Update max energy based on the number of plants
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if simulation_active:
                for plant in plants:
                    dist = ((event.pos[0] - plant['x'] - control_panel.width)**2 + (event.pos[1] - plant['y'])**2)**0.5
                    if dist < plant_radius:
                        plant['state'] = 'closed'
                        flywheel_speed = min(flywheel_speed + 1, max_speed)
                        energy_level = min(energy_level + 10, max_energy)
                        # Add spark particles
                        sparks.append({'x': plant['x'], 'y': plant['y'], 'lifetime': 30})

    # Plant simulation
    for plant in plants:
        color = RED if plant['state'] == 'closed' else NEON_BLUE
        pygame.draw.circle(screen, color, (plant['x'] + control_panel.width, plant['y']), plant_radius)
        if plant['state'] == 'closed':
            plant['state'] = 'open'  # Reopen after one frame

    # Flywheel simulation
    if simulation_active:
        flywheel_angle += flywheel_speed
        if flywheel_angle >= 360:
            flywheel_angle -= 360
        flywheel_speed = max(0, flywheel_speed - 0.1)  # Gradual slowdown
        flywheel_glow = (min(255, 100 + energy_level), 100, 255)  # Dynamic glow effect
        pygame.draw.circle(screen, flywheel_glow, (flywheel_x, flywheel_y), flywheel_radius, 3)
        flywheel_end_x = flywheel_x + flywheel_radius * math.cos(math.radians(flywheel_angle))
        flywheel_end_y = flywheel_y + flywheel_radius * math.sin(math.radians(flywheel_angle))
        pygame.draw.line(screen, flywheel_glow, (flywheel_x, flywheel_y), (flywheel_end_x, flywheel_end_y), 3)

    # Sparks display
    for spark in sparks:
        pygame.draw.circle(screen, YELLOW, (spark['x'] + control_panel.width, spark['y']), 5)
        spark['lifetime'] -= 1
    sparks = [spark for spark in sparks if spark['lifetime'] > 0]

    # Energy bar
    pygame.draw.rect(screen, DARK_GRAY, [control_panel.width + 10, 10, energy_bar_width, 20], border_radius=10)
    pygame.draw.rect(screen, YELLOW, [control_panel.width + 10, 10, (energy_level / max_energy) * energy_bar_width, 20], border_radius=10)
    energy_text = font.render(f'Energy: {energy_level}/{max_energy}', True, WHITE)
    screen.blit(energy_text, (control_panel.width + 10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
