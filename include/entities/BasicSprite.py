import pygame
import GIF
import SpriteGroups

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, imgs_moving, imgs_attacking, imgs_hitted, pos, hp = 100, mp = 100, san = 100, atk = 10, spin_lock = True):
        super().__init__()
        
        self.image = imgs_moving[0]
        
        '''animation_moving_time = 100
        animation_attacking_time = 100
        animation_hitted_time = 100'''
                
        imgs_hitted_t = []
        hurt_img = pygame.surface.Surface(imgs_hitted[0].get_size())
        for i in imgs_hitted:
            i.blit(hurt_img, (0,0))
            i.set_colorkey(255,0,0,100)
            imgs_hitted_t.append(i)
            
        imgs_hitted = imgs_hitted_t
        
        self.animation_hitted = GIF.GIF(imgs_hitted)
        self.animation_moving = GIF.GIF(imgs_moving)
        self.animation_attacking = GIF.GIF(imgs_attacking)
        
        self.rect = self.image.get_rect(center=pos)
        
        self.mass = 1
        self.force = pygame.Vector2(0,0)
        self.apply_friction = True
        self.friction_factor = 0.5
        self.speed = pygame.Vector2(0,0)
        self.deg = self.speed.angle_to((1,0))
        self.spin_lock = spin_lock
        self.exact_pos = pygame.Vector2(pos)
        
        
        # 数值初始化
        self.hp = hp
        self.maxhp = hp
        self.mp = mp
        self.maxmp = mp
        self.mprecovery = 0.5
        self.san = san
        self.maxsan = san
        self.sanrecovery = 0.5
        self.attack = 10
        self.overwhelmed = False

        self.hit = False
        self.hittime = 0

        self.COMMONATT_MP = 25
        
        self.sprite_groups = SpriteGroups.SpriteGroups

    def draw(self, surf: pygame.surface.Surface):####!!!!!!!!!!!!!!!!!!!
        
            if self.speed.x > 0:
                if not self.spin_lock:
                    self.animation_moving.rotate(self.deg)
                self.animation_moving.draw(surf, self.rect)
                
            elif self.speed.x < 0:
                self.animation_moving.flip()
                if not self.spin_lock:
                    self.animation_moving.rotate(self.deg)
                self.animation_moving.draw(surf, self.rect)
            
            else:
                surf.blit(self.image, self.rect)

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
            
        self.force += f
        
    def rdamage(self, type, ammo):

        if self.hp > 0:
            if 'hp' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

            if 'san' in type:
                self.san -= ammo
                if self.san <= 0:
                    self.san = 0
                    self.overwhelmed = True
                    self.sprite_groups.damagerender.add('破防了!', self.rect.center,(255, 255, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center,(255, 255, 0), 60, 20)

        self.hit = True
        self.hittime = 20