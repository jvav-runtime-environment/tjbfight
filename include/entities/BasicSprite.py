import pygame
import math

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, img, pos):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(center=pos)
        
        self.mass = 1
        self.force = pygame.Vector2(0,0)
        self.apply_friction = True
        self.friction_factor = 0.5
        self.speed = pygame.Vector2(0,0)
        self.deg = self.speed.angle_to((1,0))
        
        self.exact_pos = pygame.Vector2(pos)

    def draw(self, surf: pygame.surface.Surface):
        '''BasicSprite默认的显示方法'''

        surf.blit(pygame.transform.rotate(self.image, self.deg), self.rect)

    def move(self, tracking = False, aim = None, tracking_force = 0):

        self.exact_pos += self.speed
        self.rect.center = self.exact_pos
        
        self.speed += self.force / self.mass
        
        if self.apply_friction:
            self.force *= self.friction_factor
        
        if tracking:
            if aim == None:
                raise ValueError('启用跟踪时,应该为aim赋值')
            
            f = ((aim[0], aim[1]) - self.exact_pos).scale_to_length(tracking_force)
            
        

    def move_to_aim(self, aim):
        '''向aim的方向跟踪'''
        if self.r_speed != 0:
            self.aim_deg = get_degree(self.rect, aim)

            if not self.aim_deg == 0:
                if tleft_test(self.deg, self.aim_deg):
                    if abs(self.deg - abs(self.aim_deg)) <= self.r_speed:
                        self.deg = self.aim_deg
                    else:
                        self.deg += self.r_speed
                else:
                    if abs(self.deg - abs(self.aim_deg)) <= self.r_speed:
                        self.deg = self.aim_deg
                    else:
                        self.deg -= int(abs(self.aim_deg) / (abs(self.aim_deg)/self.r_speed))

            if self.deg >= 360:
                self.deg -= 360
            elif self.deg < 0:
                self.deg += 360

        self.movef()