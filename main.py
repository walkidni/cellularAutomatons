import sys

from scene import Scene
from patterns import FireForestPattern, SquaredCellularPattern
import pygame

pattern = FireForestPattern
if len(sys.argv) > 1:
    if sys.argv[1] == 'fire' : pattern = FireForestPattern
    if sys.argv[1] == 'squared': pattern = SquaredCellularPattern
# pattern = SquaredCellularPattern
def main():
    scene = Scene(pattern)
    done = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        pygame.display.flip()
        scene.update()
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exiting")
                done = True

    pygame.quit()
if __name__ == '__main__':
    main()