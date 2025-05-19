import pygame

pygame.init()

pygame.display.set_caption("My Super Game")

SIZE = WIDTH, HEIGHT = 1280, 960
FPS = 60
BG_COLOR = (255, 255, 255)

screen = pygame.display.set_mode(SIZE)

def main(screen):
    clock = pygame.time.Clock()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        screen.fill(BG_COLOR)
        clock.tick(FPS)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(screen)

