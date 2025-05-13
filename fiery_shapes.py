import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fiery Shapes")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
FIERY_COLORS = [RED, ORANGE, YELLOW]

# Particle class
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.color = random.choice(FIERY_COLORS)
        # Make yellow particles slightly smaller/shorter lifespan for effect
        if self.color == YELLOW:
            self.radius = random.randint(2, 4)
            self.lifespan = random.randint(20, 40)
        else:
            self.radius = random.randint(3, 6)
            self.lifespan = random.randint(30, 60)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1
        # Slightly reduce radius over time
        if self.radius > 1 and self.lifespan % 5 == 0:
             self.radius -= 0.5


    def draw(self, surface):
        if self.lifespan > 0:
            # Draw a circle with alpha blending for a softer look
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            alpha = max(0, min(255, int(255 * (self.lifespan / 30)))) # Fade out
            color_with_alpha = self.color + (alpha,)
            pygame.draw.circle(s, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


# --- Shape Point Generation ---
def get_circle_points(center_x, center_y, radius, num_points):
    points = []
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def get_star_points(center_x, center_y, outer_radius, inner_radius, num_points=5):
    points = []
    angle_step = math.pi / num_points
    for i in range(num_points * 2):
        radius = outer_radius if i % 2 == 0 else inner_radius
        angle = i * angle_step - math.pi / 2 # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def get_diamond_points(center_x, center_y, width, height, num_points_per_side=20):
    points = []
    half_w, half_h = width / 2, height / 2
    top = (center_x, center_y - half_h)
    right = (center_x + half_w, center_y)
    bottom = (center_x, center_y + half_h)
    left = (center_x - half_w, center_y)

    corners = [top, right, bottom, left, top] # Add top again to close loop

    for i in range(len(corners) - 1):
        start_x, start_y = corners[i]
        end_x, end_y = corners[i+1]
        for j in range(num_points_per_side):
            t = j / num_points_per_side
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            points.append((x, y))
    return points


# --- Main Loop ---
particles = []
running = True
clock = pygame.time.Clock()

shape_index = 0
shapes = ["circle", "star", "diamond"]
shape_change_time = pygame.time.get_ticks()
shape_duration = 5000 # milliseconds (5 seconds)
points_per_shape = 100 # Number of points to define the shape outline

center_x, center_y = WIDTH // 2, HEIGHT // 2

while running:
    time_now = pygame.time.get_ticks()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Shape Switching ---
    if time_now - shape_change_time > shape_duration:
        shape_index = (shape_index + 1) % len(shapes)
        shape_change_time = time_now
        particles = [] # Clear particles for new shape

    current_shape = shapes[shape_index]

    # --- Particle Generation ---
    if current_shape == "circle":
        shape_points = get_circle_points(center_x, center_y, 150, points_per_shape)
    elif current_shape == "star":
        shape_points = get_star_points(center_x, center_y, 150, 75, 5) # 5-point star
        # Adjust points_per_shape for star as get_star_points generates specific points
    elif current_shape == "diamond":
        shape_points = get_diamond_points(center_x, center_y, 250, 300, points_per_shape // 4)
         # Adjust points_per_shape for diamond

    # Add a few particles each frame based on shape points
    if shape_points: # Ensure points list is not empty
        for _ in range(5): # Add 5 particles per frame
            px, py = random.choice(shape_points)
            particles.append(Particle(px, py))


    # --- Update and Draw ---
    screen.fill(BLACK)

    for particle in particles:
        particle.update()
        particle.draw(screen)

    # Remove dead particles (iterate backwards)
    for i in range(len(particles) - 1, -1, -1):
        if particles[i].lifespan <= 0:
            particles.pop(i)

    # --- Display Update ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(60) # Limit to 60 FPS

pygame.quit()
