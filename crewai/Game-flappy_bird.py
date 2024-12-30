# ```python
import random

import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Bird properties
BIRD_SIZE = (50, 50)
bird_img = pygame.Surface(BIRD_SIZE)
bird_img.fill(GREEN)
bird_x = 100
bird_y = SCREEN_HEIGHT // 2
bird_velocity = 0
gravity = 1
flap_strength = -10

# Pipe properties
PIPE_WIDTH = 70
PIPE_GAP = 150
pipe_img = pygame.Surface((PIPE_WIDTH, 400))
pipe_img.fill(GREEN)

class Bird:
    def __init__(self):
        self.x = bird_x
        self.y = bird_y
        self.velocity = bird_velocity

    def flap(self):
        self.velocity = flap_strength

    def update(self):
        self.velocity += gravity
        self.y += self.velocity

    def draw(self, screen):
        screen.blit(bird_img, (self.x, self.y))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - 250)
        self.passed = False

    def move(self, speed):
        self.x -= speed

    def draw(self, screen):
        screen.blit(pipe_img, (self.x, self.height - pipe_img.get_height()))
        screen.blit(pipe_img, (self.x, self.height + PIPE_GAP))

def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH)]
    score = 0
    speed = 5
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()

        # Update bird position
        bird.update()

        # Move pipes
        remove_pipes = []
        for pipe in pipes:
            pipe.move(speed)
            if pipe.x + PIPE_WIDTH < 0:
                remove_pipes.append(pipe)

            # Score increment when passing through a pipe
            if not pipe.passed and pipe.x < bird.x:
                score += 1
                pipe.passed = True

        for pipe in remove_pipes:
            pipes.remove(pipe)
            new_pipe = Pipe(SCREEN_WIDTH + PIPE_WIDTH * 2)
            pipes.append(new_pipe)

        # Collision detection
        for pipe in pipes:
            if (bird.x < pipe.x + PIPE_WIDTH and bird.x > pipe.x) or \
               (bird.x + BIRD_SIZE[0] > pipe.x and bird.x + BIRD_SIZE[0] < pipe.x + PIPE_WIDTH):
                if bird.y < pipe.height or bird.y + BIRD_SIZE[1] > pipe.height + PIPE_GAP:
                    game_over = True

        # Ground collision
        if bird.y + BIRD_SIZE[1] >= SCREEN_HEIGHT or bird.y <= 0:
            game_over = True

        # Draw everything
        screen.fill(WHITE)
        for pipe in pipes:
            pipe.draw(screen)
        bird.draw(screen)

        # Display score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", True, GREEN)
        screen.blit(text, (10, 10))

        pygame.display.update()
        clock.tick(30)

    # Game over screen
    screen.fill(WHITE)
    game_over_text = font.render("Game Over", True, GREEN)
    final_score_text = font.render(f"Final Score: {score}", True, GREEN)
    restart_text = font.render("Press SPACE to Restart", True, GREEN)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT * 2 // 3))

    pygame.display.update()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                main()

if __name__ == "__main__":
    main()
# ```

# This code sets up a simple Flappy Bird game using Pygame. The bird can be controlled by pressing the spacebar to flap, and it falls due to gravity. Pipes move from right to left, and the player scores points for passing through them. The game ends if the bird collides with a pipe or the ground. After the game over screen appears, pressing the spacebar restarts the game.