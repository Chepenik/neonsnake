import pygame
import random
import sys
import os
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Set up the game window (square grid)
GRID_SIZE = 24  # Size of each grid cell, you can adjust this to make the grid larger or smaller
GRID_WIDTH, GRID_HEIGHT = 40, 40  # Number of cells in the grid, adjust to change game size
WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (3, 207, 252)
NEON_PINK = (255, 20, 147)
NEON_YELLOW = (255, 255, 0)

# Snake properties
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Starting position of the snake
snake_direction = (1, 0)  # Initial direction of the snake (moving right)
snake_growth = 0  # Growth counter for the snake

# Food properties
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))  # Random food position

# Power-up properties
power_up = None
power_up_timer = 0
POWER_UP_DURATION = 200  # Duration for which the power-up remains on screen

# Score and font
score = 0
font = pygame.font.Font(None, 36)  # Font for displaying score

# High score properties
high_scores_file = "high_scores.txt"
high_scores = []

# Sound effects (uncomment if you have the sound files)
eat_sound = pygame.mixer.Sound("eat.wav")
power_up_sound = pygame.mixer.Sound("power_up.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

# Game clock
clock = pygame.time.Clock()

def load_high_scores():
    """Load high scores from file"""
    global high_scores
    if os.path.exists(high_scores_file):
        with open(high_scores_file, "r") as file:
            high_scores = [line.strip().split(":") for line in file]
            high_scores = [(name, int(score)) for name, score in high_scores]

def save_high_scores():
    """Save high scores to file"""
    global high_scores
    with open(high_scores_file, "w") as file:
        for name, score in high_scores:
            file.write(f"{name}:{score}\n")

def update_high_scores(name, score):
    """Update the high score list"""
    global high_scores
    high_scores.append((name, score))
    high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)[:5]  # Keep top 5 scores
    save_high_scores()

def draw_grid():
    """Draw the game grid"""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(SCREEN, (30, 30, 30), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(SCREEN, (30, 30, 30), (0, y), (WIDTH, y))

def draw_snake():
    """Draw the snake with a glowing effect"""
    for i, segment in enumerate(snake):
        color = NEON_GREEN if i == 0 else NEON_BLUE
        x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
        # Draw main body
        pygame.draw.rect(SCREEN, color, (x, y, GRID_SIZE, GRID_SIZE))
        # Draw glow effect
        for offset in range(1, 5):
            gfxdraw.rectangle(SCREEN, (x-offset, y-offset, GRID_SIZE+offset*2, GRID_SIZE+offset*2), (*color, 50-offset*10))

def draw_food():
    """Draw the food with a pulsating effect"""
    x, y = food[0] * GRID_SIZE, food[1] * GRID_SIZE
    pulse = int(128 + 127 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)  # Pulsating alpha value
    # Draw main food
    pygame.draw.rect(SCREEN, NEON_PINK, (x, y, GRID_SIZE, GRID_SIZE))
    # Draw pulsating glow
    gfxdraw.filled_circle(SCREEN, x + GRID_SIZE // 2, y + GRID_SIZE // 2, GRID_SIZE // 2 + 2, (*NEON_PINK, pulse))

def draw_power_up():
    """Draw the power-up with a spinning effect"""
    if power_up:
        x, y = power_up[0] * GRID_SIZE, power_up[1] * GRID_SIZE
        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        angle = pygame.time.get_ticks() % 360
        points = [
            (center[0] + int(GRID_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle + i * 72)[0]),
             center[1] + int(GRID_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle + i * 72)[1]))
            for i in range(5)
        ]
        pygame.draw.polygon(SCREEN, NEON_YELLOW, points)

def move_snake():
    """Move the snake and handle collisions"""
    global snake, snake_growth, score, food, power_up, power_up_timer

    # Calculate new head position with wrap-around
    new_head = ((snake[0][0] + snake_direction[0]) % GRID_WIDTH, 
                (snake[0][1] + snake_direction[1]) % GRID_HEIGHT)
    
    # Check for collision with self
    if new_head in snake:
        game_over()

    # Add new head to snake
    snake.insert(0, new_head)

    # Handle food collision
    if new_head == food:
        score += 1
        snake_growth += 3
        eat_sound.play()
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if random.random() < 0.2 and not power_up:
            power_up = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            power_up_timer = POWER_UP_DURATION

    # Handle power-up collision
    if new_head == power_up:
        score += 5
        snake_growth += 5
        power_up_sound.play()
        power_up = None

    # Grow snake or remove tail
    if snake_growth > 0:
        snake_growth -= 1
    else:
        snake.pop()

    # Update power-up timer
    if power_up:
        power_up_timer -= 1
        if power_up_timer <= 0:
            power_up = None

def game_over():
    """Display game over screen and handle high score input"""
    global snake, snake_direction, snake_growth, score, food, power_up, power_up_timer

    game_over_sound.play()
    font = pygame.font.Font(None, 72)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    SCREEN.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(1000)

    initials = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(initials) == 3:
                    update_high_scores(initials, score)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha():
                    initials += event.unicode.upper()

        SCREEN.fill(BLACK)
        SCREEN.blit(text, text_rect)
        initials_text = font.render(f"Enter Initials: {initials}", True, WHITE)
        initials_rect = initials_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        SCREEN.blit(initials_text, initials_rect)
        pygame.display.flip()
        clock.tick(10)

    display_high_scores()
    end_screen()

def display_high_scores():
    """Display the high scores"""
    global high_scores

    SCREEN.fill(BLACK)
    font = pygame.font.Font(None, 48)
    title = font.render("High Scores", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
    SCREEN.blit(title, title_rect)

    font = pygame.font.Font(None, 36)
    for i, (name, score) in enumerate(high_scores):
        score_text = font.render(f"{name}: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 40))
        SCREEN.blit(score_text, score_rect)

    pygame.display.flip()
    pygame.time.wait(3000)

def end_screen():
    """Display options to restart or quit after entering initials"""
    font = pygame.font.Font(None, 36)
    text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    SCREEN.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def reset_game():
    """Reset the game to initial state"""
    global snake, snake_direction, snake_growth, score, food, power_up, power_up_timer
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (1, 0)
    snake_growth = 0
    score = 0
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    power_up = None
    power_up_timer = 0

def main():
    """Main game loop"""
    global snake_direction

    load_high_scores()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)
                elif event.key == pygame.K_r:
                    reset_game()

        move_snake()

        SCREEN.fill(BLACK)
        draw_grid()
        draw_snake()
        draw_food()
        draw_power_up()

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(10)  # Control game speed

if __name__ == "__main__":
    main()
