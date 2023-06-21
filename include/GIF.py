import pygame

class GIF(pygame.sprite.Sprite):
    def __init__(self, imgs, deg=0, life=12, loop = False):
        super().__init__()

        self.images = imgs
        self.image = self.images[0]
        
        self.deg = deg
        self.mlife = life
        self.life = life
        self.loop = loop

        self.d = self.life/len(self.images)
        
    def draw(self, surf: pygame.surface.Surface, rect, update = True):
        
        surf.blit(self.images[(self.life // self.d) - 1], rect)
        
        if update:
            self.update()

    def update(self):
        
        self.life = self.life - 1
        
        if self.life <= 1:
            if self.loop:
                self.life = self.mlife
            else:
                self.kill()

    def rotate(self, deg):
        
        self.deg = deg
        
        for i in self.images:
            self.images[self.images.index(i)] = pygame.transform.rotate(i, deg)
            
    def scale(self, size):
        
        for i in self.images:
            self.images[self.images.index(i)] = pygame.transform.scale(i, size)
            
    def flip(self, x = True, y = False):
        
        t_deg = self.deg
        
        self.rotate(-self.deg)
        
        for i in self.images:
            self.images[self.images.index(i)] = pygame.transform.flip(i, x, y)
            
        self.rotate(t_deg)
        
    def isFinished(self):
        
        if (self.life // self.d) - 1 == 0:
            return True
        else:
            return False