import pygame
import random
import math
import numpy as np  # Import numpy for easier vector math if needed

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PARTICLE_COUNT = 200  # Increased count for better shape definition
BACKGROUND_COLOR = (10, 10, 20)
MAX_SPEED = 3.5
STEERING_FORCE = 0.15  # Slightly stronger steering
APPROACH_RADIUS = 60  # Slightly larger approach radius
SHAPE_SWITCH_INTERVAL = 300  # Frames between shape changes (5 seconds at 60 FPS)
TRANSITION_BOOST = 4.0  # Velocity boost during transition

# --- Shape Generation Functions ---
def get_circle_points(num_points, center_x, center_y, radius):
    """Generates points forming a circle."""
    points = []
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def get_diamond_points(num_points, center_x, center_y, width, height):
    """Generates points forming a diamond shape."""
    points = []
    half_w, half_h = width / 2, height / 2
    points_per_side = num_points // 4
    extra_points = num_points % 4

    # Top-left to Top-right
    for i in range(points_per_side + (1 if extra_points > 0 else 0)):
        ratio = i / (points_per_side + (1 if extra_points > 0 else 0) - 1) if (points_per_side + (1 if extra_points > 0 else 0)) > 1 else 0.5
        points.append((center_x + ratio * half_w, center_y - half_h + ratio * half_h))
    # Top-right to Bottom-right
    for i in range(points_per_side + (1 if extra_points > 1 else 0)):
        ratio = i / (points_per_side + (1 if extra_points > 1 else 0) - 1) if (points_per_side + (1 if extra_points > 1 else 0)) > 1 else 0.5
        points.append((center_x + half_w - ratio * half_w, center_y + ratio * half_h))
    # Bottom-right to Bottom-left
    for i in range(points_per_side + (1 if extra_points > 2 else 0)):
        ratio = i / (points_per_side + (1 if extra_points > 2 else 0) - 1) if (points_per_side + (1 if extra_points > 2 else 0)) > 1 else 0.5
        points.append((center_x - ratio * half_w, center_y + half_h - ratio * half_h))
    # Bottom-left to Top-left
    for i in range(points_per_side):
        ratio = i / (points_per_side - 1) if points_per_side > 1 else 0.5
        points.append((center_x - half_w + ratio * half_w, center_y - ratio * half_h))

    # Ensure exact number of points if division wasn't perfect
    while len(points) < num_points:
        points.append(points[0])  # Add duplicates if needed, less ideal
    return points[:num_points]

def get_heart_points(num_points, center_x, center_y, scale):
    """Generates points forming a heart shape using parametric equations."""
    points = []
    for i in range(num_points):
        # Parametric equation for a heart shape
        t = (i / num_points) * 2 * math.pi
        x = center_x + scale * 16 * (math.sin(t) ** 3)
        y = center_y - scale * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((x, y))
    return points

def distribute_points_on_polygon(vertices, num_points):
    """Distributes points relatively evenly along the edges of a polygon."""
    points = []
    total_length = 0
    segment_lengths = []

    # Calculate total perimeter length
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]  # Wrap around for the last segment
        length = math.dist(p1, p2)
        segment_lengths.append(length)
        total_length += length

    if total_length < 1e-6:  # Avoid division by zero if polygon is just a point
        return [vertices[0]] * num_points

    # Distribute points based on segment length
    points_so_far = 0
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
        length = segment_lengths[i]
        num_segment_points = int(round((length / total_length) * num_points))

        # Ensure at least one point if segment has length, handle last segment point distribution
        if i == len(vertices) - 1:
            num_segment_points = num_points - points_so_far  # Assign remaining points
        elif length > 1e-6 and num_segment_points == 0:
            num_segment_points = 1  # Add at least one point for non-zero length segments

        # Interpolate points along the segment (excluding the end point, it's the start of the next)
        for j in range(num_segment_points):
            ratio = j / num_segment_points if num_segment_points > 0 else 0
            x = p1[0] + (p2[0] - p1[0]) * ratio
            y = p1[1] + (p2[1] - p1[1]) * ratio
            points.append((x, y))
            points_so_far += 1

            if points_so_far >= num_points:  # Stop if we've generated enough points
                return points[:num_points]

    # If rounding caused fewer points, add duplicates of the first point
    while len(points) < num_points:
        points.append(points[0])

    return points[:num_points]

def get_bird_points(num_points, center_x, center_y, scale):
    """Generates points for a simple bird silhouette."""
    # Define vertices relative to (0,0), then scale and translate
    bird_vertices = [
        (0, 0), (-2, -1), (-4, -1), (-3, 0), (-4, 1),  # Tail
        (-2, 1), (0, 2), (2, 1),  # Body/Back Wing
        (4, 1), (3, 0), (4, -1),  # Head/Beak
        (2, -1), (0, 0)  # Under Body/Front Wing
    ]
    scaled_vertices = [(center_x + vx * scale, center_y - vy * scale) for vx, vy in bird_vertices]  # Invert Y for screen coords
    return distribute_points_on_polygon(scaled_vertices, num_points)

def get_lion_points(num_points, center_x, center_y, scale):
    """Generates points for a simple lion head silhouette."""
    # Define vertices for mane and face outline
    lion_vertices = [
        # Mane outline (simplified octagon/circle)
        (0, 4), (-2, 3.5), (-3.5, 2), (-4, 0), (-3.5, -2),
        (-2, -3.5), (0, -4), (2, -3.5), (3.5, -2), (4, 0),
        (3.5, 2), (2, 3.5), (0, 4),
    ]
    scaled_vertices = [(center_x + vx * scale, center_y - vy * scale) for vx, vy in lion_vertices]
    return distribute_points_on_polygon(scaled_vertices, num_points)

# --- Particle Class ---
class Particle:
    def __init__(self, target_x, target_y):
        """Initializes a particle near center, with a target."""
        self.x = random.uniform(WIDTH / 2 - 50, WIDTH / 2 + 50)
        self.y = random.uniform(HEIGHT / 2 - 50, HEIGHT / 2 + 50)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.target_x = target_x
        self.target_y = target_y
        self.color = (random.randint(100, 255), random.randint(50, 150), random.randint(150, 255))
        self.size = random.uniform(1.5, 4.5)

    def set_target(self, tx, ty):
        self.target_x = tx
        self.target_y = ty

    def apply_force(self, fx, fy):
        """Applies a force to the particle's velocity."""
        self.vx += fx
        self.vy += fy

    def update(self):
        """Updates the particle's state, steering towards the target."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist > 0.1:  # Avoid division by zero and jittering at target
            # Calculate desired velocity (pointing towards target)
            desired_vx = (dx / dist) * MAX_SPEED
            desired_vy = (dy / dist) * MAX_SPEED

            # Implement easing: slow down when close to the target
            if dist < APPROACH_RADIUS:
                # Map distance within approach radius to a speed factor (0 to 1)
                speed_factor = max(0.05, dist / APPROACH_RADIUS)  # Ensure minimum speed to avoid stopping completely before reaching
                desired_vx *= speed_factor
                desired_vy *= speed_factor

            # Calculate steering force
            steer_vx = desired_vx - self.vx
            steer_vy = desired_vy - self.vy

            # Limit steering force
            steer_mag = math.sqrt(steer_vx ** 2 + steer_vy ** 2)
            if steer_mag > STEERING_FORCE:
                steer_vx = (steer_vx / steer_mag) * STEERING_FORCE
                steer_vy = (steer_vy / steer_mag) * STEERING_FORCE

            # Apply steering force to velocity
            self.vx += steer_vx
            self.vy += steer_vy

            # Limit overall speed
            speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if speed > MAX_SPEED:
                self.vx = (self.vx / speed) * MAX_SPEED
                self.vy = (self.vy / speed) * MAX_SPEED

        # Apply some drag/friction
        self.vx *= 0.98
        self.vy *= 0.98

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Optional: Update color based on velocity or distance
        speed_ratio = min(1, math.sqrt(self.vx ** 2 + self.vy ** 2) / MAX_SPEED)
        r = int(50 + 200 * speed_ratio)
        g = int(150 - 100 * speed_ratio)
        b = int(200 - 150 * speed_ratio)
        self.color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def draw(self, screen):
        """Draws the particle on the screen."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# --- Main Setup ---
try:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shape Morphing Particles")
    clock = pygame.time.Clock()

    # Define shapes and their parameters
    shapes = [
        lambda n: get_circle_points(n, WIDTH / 2, HEIGHT / 2, 200),
        lambda n: get_diamond_points(n, WIDTH / 2, HEIGHT / 2, 350, 350),
        lambda n: get_heart_points(n, WIDTH / 2, HEIGHT / 2 - 30, 15),  # Heart needs Y offset and scaling
        lambda n: get_bird_points(n, WIDTH / 2, HEIGHT / 2, 40),  # Bird needs scaling
        lambda n: get_lion_points(n, WIDTH / 2, HEIGHT / 2, 45),  # Lion needs scaling
        lambda n: get_circle_points(n, WIDTH / 2, HEIGHT / 2, 100),  # Smaller circle
    ]
    current_shape_index = 0
    shape_switch_timer = 0

    # Generate initial target points and create particles
    target_points = shapes[current_shape_index](PARTICLE_COUNT)
    particles = [Particle(target_points[i][0], target_points[i][1]) for i in range(PARTICLE_COUNT)]

    # --- Game Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Update ---
        shape_switch_timer += 1
        if shape_switch_timer >= SHAPE_SWITCH_INTERVAL:
            shape_switch_timer = 0
            current_shape_index = (current_shape_index + 1) % len(shapes)
            target_points = shapes[current_shape_index](PARTICLE_COUNT)
            random.shuffle(target_points)  # Shuffle to make transitions more dynamic

            # Apply transition boost and set new targets
            center_x, center_y = WIDTH / 2, HEIGHT / 2  # Boost away from screen center
            for i, p in enumerate(particles):
                # Calculate direction away from center
                dx = p.x - center_x
                dy = p.y - center_y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                boost_vx = 0
                boost_vy = 0
                if dist > 1:  # Avoid division by zero if particle is at center
                    boost_vx = (dx / dist) * TRANSITION_BOOST
                    boost_vy = (dy / dist) * TRANSITION_BOOST

                p.apply_force(boost_vx, boost_vy)  # Give it a push
                p.set_target(target_points[i][0], target_points[i][1])  # Assign new target

        for p in particles:
            p.update()

        # --- Draw ---
        screen.fill(BACKGROUND_COLOR)
        for p in particles:
            p.draw(screen)

        pygame.display.flip()
        clock.tick(60)

except ImportError:
    print("Pygame is not installed. Please install it using: pip install pygame")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()  # Print detailed traceback for debugging
finally:
    pygame.quit()
    print("Program finished.")

