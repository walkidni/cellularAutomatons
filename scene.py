import pygame
from patterns import SquaredCellularPattern, FireForestPattern


# __screenSize__ = (500,500) #(1280,1280)
# self._cell_size = 10 

def getColorCell(colors ,n):
    return colors[n]

class Scene:
    _mouseCoords = (0,0)

    def __init__(self, automatonPattern, rows=500, cols=500, cell_size=10, *args, **kwargs):
        pygame.init()
        
        if kwargs is None:
            args = [v for k,v in kwargs]
        
        self._screen = pygame.display.set_mode((rows, cols))
        self._font = pygame.font.SysFont('Arial',25)

        self._rows = rows
        self._cols = cols
        
        self._pattern_rows = rows//cell_size
        self._pattern_cols = cols//cell_size
        self._pattern = automatonPattern(self._pattern_rows , self._pattern_cols, *args)
        self._cell_size = cell_size
        self._colors = self._pattern.colors
        # print(self._pattern.to_numpy().shape)

    def drawMe(self):
        if self._pattern is None:
            return
        self._screen.fill((100,100,100))
        for x in range(self._pattern_rows):
            for y in range(self._pattern_cols):
                # print(x,y)
                pygame.draw.rect(
                    surface= self._screen, 
                    color= getColorCell(self._colors, self._pattern.to_numpy()[x,y]),
                    rect= (x*self._cell_size + 1, y*self._cell_size + 1, self._cell_size-2, self._cell_size-2)
                    )
        
        self._drawText(self._pattern.name, (20,20))


    def _drawText(self, text, position, color = (255,64,64)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        self._pattern.update()

    def eventClic(self, coord, b):
        pass

    def recordMouseMove(self, coord):
        pass