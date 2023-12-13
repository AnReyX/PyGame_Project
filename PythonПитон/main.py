import pygame

if __name__ == '__main__':
    pygame.init()
    size = width, height = 800, 400
    screen = pygame.display.set_mode(size)
    v = 20
    fps = 60
    R = 0
    clock = pygame.time.Clock()
    running = True
    screen.fill('blue')
    coords_ = (-1000, -1000)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                screen.fill('blue')
                R = 0
                coords_ = event.pos
        pygame.draw.circle(screen, (255, 255, 0), coords_, R)
        R += v / fps
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()