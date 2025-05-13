import pygame
import random
import math

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PARTICLE_COUNT = 150
PARTICLE_SIZE = 4
MAX_SPEED = 2
COLOR_SHIFT_SPEED = 0.5 # How fast colors change based on position/time

# --- Initialization ---
try:
    pygame.init()
except pygame.error as e:
    print(f"Error initializing Pygame: {e}")
    print("Please ensure Pygame is installed ('pip install pygame') and your display environment is set up.")
    exit()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vibe Code Morphing Particles")
clock = pygame.time.Clock()

# --- Particle Class ---
class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.vx = random.uniform(-MAX_SPEED, MAX_SPEED)
        self.vy = random.uniform(-MAX_SPEED, MAX_SPEED)
        # Initial color hue based on position (simple "vibe")
        self.color_hue = (self.x / WIDTH) * 360 # Hue based on horizontal position

    def update(self, dt):
        # Move particle
        self.x += self.vx * dt * 60 # Scale speed by dt for frame independence
        self.y += self.vy * dt * 60

        # Bounce off edges
        if self.x <= PARTICLE_SIZE or self.x >= WIDTH - PARTICLE_SIZE:
            self.vx *= -1
            self.x = max(PARTICLE_SIZE, min(self.x, WIDTH - PARTICLE_SIZE)) # Clamp position
        if self.y <= PARTICLE_SIZE or self.y >= HEIGHT - PARTICLE_SIZE:
            self.vy *= -1
            self.y = max(PARTICLE_SIZE, min(self.y, HEIGHT - PARTICLE_SIZE)) # Clamp position

        # Morphing: Shift color hue based on distance from center and time
        dist_center_x = abs(self.x - WIDTH / 2) / (WIDTH / 2)
        dist_center_y = abs(self.y - HEIGHT / 2) / (HEIGHT / 2)
        # Combine distance and add a slow time-based shift
        self.color_hue = (self.color_hue + COLOR_SHIFT_SPEED * dist_center_x * dist_center_y * dt * 60) % 360

    def draw(self, surface):
        # Convert HSL to RGB for Pygame
        color = pygame.Color(0)
        # Saturation and Lightness fixed for vibrant colors
        try:
            color.hsla = (self.color_hue, 100, 50, 100)
        except ValueError: # Handle potential invalid hue values briefly during calculation
             color.hsla = (0, 100, 50, 100) # Default to red if error
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), PARTICLE_SIZE)

# --- Create Particles ---
particles = [Particle() for _ in range(PARTICLE_COUNT)]

# --- Game Loop ---
running = True
print("Starting particle simulation... Press ESC or close the window to exit.")
while running:
    # Delta time ensures consistent speed regardless of frame rate
    # Limit dt to prevent large jumps if frame rate drops significantly
    dt = min(clock.tick(60) / 1000.0, 0.1) # Delta time in seconds, capped

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Allow exit with ESC key
                running = False

    # Update Particles
    for p in particles:
        p.update(dt)

    # Draw
    screen.fill((10, 10, 20)) # Dark blue background
    for p in particles:
        p.draw(screen)

    # Update Display
    pygame.display.flip()

# --- Quit ---
print("Exiting simulation.")
pygame.quit()
