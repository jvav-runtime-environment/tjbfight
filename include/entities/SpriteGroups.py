import pygame

class SpriteGroups():
    particlegroup:pygame.sprite.Group
    bulletgroup:pygame.sprite.Group
    playergroup:pygame.sprite.Group
    enemygroup:pygame.sprite.Group
    damagerender:pygame.sprite.Group
    enemybulletgroup:pygame.sprite.Group
    
    def __init__(self):
        self.particlegroup = None       #pclg
        self.bulletgroup = None         #bullets
        self.playergroup = None         #playerg
        self.enemygroup = None          #enemies
        self.damagerender = None        #dmgr
        self.enemybulletgroup = None    #enemybullets
        
#--------------------------------------------
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#在引用SpriteGroups时必须为其各个属性赋值!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#---------------------------------------------