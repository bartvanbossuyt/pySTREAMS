import pygame
from inequality_matrix import InequalityMatrix

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Demo: Inequality Matrix") #window title
clock = pygame.time.Clock()
#insert labels here, it will determine the matrix dimensions
labels = ["k|t_1", "l|t_1", "k|t_2", "l|t_2"]
values = [
    [0, 1, -1, 0], #green = 1, yellow = 0, red = -1
    [0, 0, 1, -1],
    [0, 0, 0, 1],
    [0, 0, 0, 0]
]
#define name, cell size, labels, values, position
matrix = InequalityMatrix("d_1", 60, labels, values, pos=(100, 50))

running = True #do not change 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255)) #white background
    matrix.draw(screen)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
