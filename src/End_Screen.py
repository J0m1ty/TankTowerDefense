import time
from enum import Enum
import pygame
import sys
import math

pygame.font.init()
font = pygame.font.SysFont("avenir", 48)
click = False
keys = []


def main():
    # Global variables that will be set here
    global state_manager
    global click
    global keys

    # Start pygame
    pygame.init()

    # Setup window, screen, and clock
    pygame.display.set_caption("Tank Tower Defense")
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    screen.fill((255, 255, 255))
    # Game loop
    run = True
    while run:
        # Get actively pressed keys
        keys = pygame.key.get_pressed()
        title = font.render("Game Over", True, (2, 2, 2))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 200))
        button_text = font.render("Press 'SPACE' To Return to Menu", True, (2, 2, 2))
        screen.blit(button_text, (screen.get_width() // 2 - button_text.get_width() // 2, 435))

        if keys[pygame.K_BACKSPACE]:
            import Title_Screen
        # Get and process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Update game

        # Render entire display
        pygame.display.flip()

        # Progress time
        clock.tick(60)

        # Reset click frame
        click = False

    # Exit game after loop
    pygame.quit()
    sys.exit()


main()
