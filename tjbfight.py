import math
import random

import pygame
from pygame.locals import *

# ---基本函数---

def get_degree(start_pos, end_pos):
    x = float(end_pos[0] - start_pos[0])
    y = float(start_pos[1] - end_pos[1])
    r = ((x)**2+(y)**2)**0.5

    if r != 0:
        rad = math.acos(x/r)
    else:
        rad = 0

    degree = math.degrees(rad)

    if y < 0:
        degree = 360 - degree

    return degree

def tleft_test(deg, aim_deg):
    
    if deg < 180:
        if deg < aim_deg < oppo_deg(deg):
            return True
        else:
            return False

    if deg > 180:
        if (aim_deg < oppo_deg(deg)) or (aim_deg > deg):
            return True
        else:
            return False

    if deg == 180:
        if aim_deg > 180:
            return True
        else:
            return False

def oppo_deg(deg):
    deg += 180
    if deg >= 360:
        deg -= 360
    return deg

def get_distance(start, to):
    return math.sqrt((start[0]-to[0])**2+(start[1]-to[1])**2)

def get_mouse_pos():
    x, y = player.rect.center
    x = x - SCREEN_WIDTH/2
    y = y - SCREEN_HEIGHT/2 - 100
    mx, my = pygame.mouse.get_pos()
    return (mx+x, my+y)

def get_spawn_enemy(pos):
    return random.choice([
            Enemy_CH(ENEMYIMG_CH, pos, groups, hp=333),
            Enemy_SXZ(ENEMYIMG_SXZ, pos, groups, 333),
            Enemy_GOD_LEFTHAND(ENEMYIMG_LEFTHAND, pos, groups, 333)
            ])

def change_round(pos):
    global rounds, level, enemies, pclg

    if not level % 5 == 0:
        for i in rounds.keys():
            if i == level:
                for j in rounds[i]:
                    pos = [random.randint(pos[0]-350, pos[0]+350), random.randint(pos[1]-300, pos[1])]
                    j.rect.center = pos
                    j.exact_pos = pos
                    enemies.add(j)
                    for _ in range(25):
                        pclg.add(Particle(random.randint(0, 360), pos, 20, random.uniform(0, 10), 200, (0, 1, 0, 190)))
                return

        for i in range(int(math.sqrt(level*3))):
            pos = [random.randint(pos[0]-350, pos[0]+350), random.randint(pos[1]-300, pos[1])]
            enemies.add(get_spawn_enemy(pos))
            for _ in range(25):
                pclg.add(Particle(random.randint(0, 360), pos, 20, random.uniform(0, 10), 200, (0, 1, 0, 190)))
    else:
        for i in rounds.keys():
            if i == level:
                for j in rounds[i]:
                    pos = [random.randint(pos[0]-350, pos[0]+350), random.randint(pos[1]-300, pos[1])]
                    j.rect.center = pos
                    j.exact_pos = pos
                    j.boss()
                    enemies.add(j)
                    for _ in range(25):
                        pclg.add(Particle(random.randint(0, 360), pos, 20, random.uniform(0, 10), 200, (0, 1, 0, 190)))
                return

        pos = [random.randint(pos[0]-350, pos[0]+350), random.randint(pos[1]-300, pos[1])]
        e = get_spawn_enemy(pos)
        e.boss()
        enemies.add(e)
        for _ in range(25):
            pclg.add(Particle(random.randint(0, 360), pos, 20, random.uniform(0, 10), 200, (0, 1, 0, 190)))

'''def creat_particle(deg, pos, time, speed=5, size=3, colour=(255, 255, 255, 255)):
    global pclg, useableparticles
    if len(useableparticles) == 0:
        pclg.add(Particle(deg, pos, time, speed, size, colour))
    else:
        s = useableparticles.sprites()[0]
        useableparticles.remove(s)
        pclg.add(s.__init__(deg, pos, time, speed, size, colour))'''

# ---提供对组的访问---

class Groups():
    def __init__(self):
        self.particlegroup = pclg
        self.bulletgroup = bullets
        self.playergroup = playerg
        self.enemygroup = enemies
        self.damagerender = dmgr
        self.enemybulletgroup = enemybullets


# ---定义基本类---

class Basic_sprite(pygame.sprite.Sprite):
    def __init__(self, img, pos, deg=1):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(center=pos)
        self.deg = deg                                  # 角度
        self.r_speed = 5                                # 旋转速度
        self.d_r_speed = 0
        self.speed = 10
        self.a = 0                                      # 加速度
        self.d_a = 0                                    # 加速度变化量
        self.exact_pos = [pos[0], pos[1]]                 # 高精度位置

    def update(self, surf: pygame.surface.Surface):
        '''sprite默认的更新方法'''

        surf.blit(pygame.transform.rotate(self.image, self.deg), self.rect)

    def movef(self):
        '''向deg方向移动'''

        self.exact_pos[0] += self.speed*math.cos(math.radians(self.deg))
        self.exact_pos[1] -= self.speed*math.sin(math.radians(self.deg))
        self.rect.center = self.exact_pos

    def update_a(self):
        '''更新速度、加速度'''

        self.a += self.d_a
        self.speed += self.a
        self.r_speed += self.d_r_speed

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


# ---定义伤害显示器---

class Dmgrender():
    def __init__(self, sur):
        self.list = []
        self.sur = sur
        self._circle_cache = {}

    def add(self, string, pos, color, time=-1, size=50):
        font = pygame.font.SysFont('simhei', size)
        surface = self.render(str(string), font, color)
        srect = surface.get_rect()
        srect.center = pos                              # 获取显示坐标
        self.list.append([surface, color, srect, time, random.uniform(-3, 3)])

    def update(self):
        for strings in self.list:

            strings[2].centerx += strings[4]
            strings[2].centery -= 2

            t = 60-strings[3]
            x = strings[0].get_width()*(60*t-t**2)/500
            y = strings[0].get_height()*(60*t-t**2)/500
            
            self.sur.blit(pygame.transform.scale(strings[0], (x, y)), strings[2])

            strings[3] -= 2
            if strings[3] == 0:
                self.list.remove(strings)
        
    def _circlepoints(self, r):
        r = int(round(r))
        if r in self._circle_cache:
            return self._circle_cache[r]
        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def render(self, text, font, gfcolor=pygame.Color('dodgerblue'), ocolor=(255, 255, 255), opx=2):
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))
        return surf


# ---定义粒子效果---

class Particle(pygame.sprite.Sprite):
    def __init__(self, deg, pos, time, speed=5, size=3, colour=(255, 255, 255, 255)):
        super().__init__()

        # 图层初始化
        self.image = pygame.surface.Surface((size, size))
        self.image.convert()
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.image.set_alpha(colour[3])
        pygame.draw.circle(self.image, colour, (math.ceil(size/2), math.ceil(size/2)), math.ceil(size/2))

        # 坐标初始化
        self.rect = self.image.get_rect()
        self.exact_pos = list(pos)
        self.rect.center = self.exact_pos

        # 数值初始化
        self.deg = deg
        self.time = time
        self.speed = speed
        self.size = size

        # 计算变化量
        self.d_size = size/time
        self.d_speed = speed/time

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''

        # 大小，速度更新
        self.speed -= self.d_speed
        self.size -= self.d_size

        # 位置更新
        self.exact_pos[0] += self.speed*math.cos(math.radians(self.deg))
        self.exact_pos[1] -= self.speed*math.sin(math.radians(self.deg))
        self.rect.size = (self.size, self.size)
        self.rect.center = self.exact_pos
        

        # 显示
        surf.blit(pygame.transform.scale(self.image, (int(self.size), int(self.size))), self.rect)
        #pygame.draw.rect(surf, (0,0,0), self.rect, 1)

        # 倒计时
        self.time -= 1
        if self.time <= 0:
            self.kill()


# ---定义敌人类---

class Enemy_CH(Basic_sprite):
    def __init__(self, image, pos, sprite_groups:Groups, hp=100, mp=100, san=100):
        super().__init__(image, pos)

        # 数值初始化
        self.hp = hp
        self.maxhp = hp
        self.mp = 0
        self.maxmp = mp
        self.mprecovery = 0.5
        self.san = san
        self.maxsan = san
        self.sanrecovery = 0.5
        self.attack = 10
        self.overwhelmed = False

        # 被击中和冷却时间:用于呈现击中效果
        self.hit = False
        self.hittime = 15

        # 图层初始化
        self.image = image.copy()
        self.image.convert_alpha()

        # 击中效果初始化
        self.hitsurf = image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))

        # 位置初始化
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # 组初始化
        self.sprite_groups = sprite_groups

        #数值
        self.COMMONATT_MP = 25

    def rdamage(self, type, ammo):
        '''接受伤害'''

        if self.hp > 0:

            # 扣除血量
            if 'hp' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

            # 扣除精神值
            if 'san' in type:
                self.san -= ammo
                if self.san <= 0:
                    self.san = 0
                    self.overwhelmed = True
                    self.sprite_groups.damagerender.add('破防了!', self.rect.center,(255, 255, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center,(255, 255, 0), 60, 20)

        self.hit = True

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''

        #调用AI
        self.AI()

        #数值判断
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp

        # 显示
        if self.hit or self.hp <= 0:
            # 死亡时翻转
            if self.hp <= 0:
                s = pygame.transform.rotate(self.hitsurf, 90)
                s.set_colorkey((255, 0, 0, 125))
                surf.blit(s, self.rect)
            else:
                surf.blit(self.hitsurf, self.rect)

            # 击中时间
            self.hittime -= 1
            if self.hittime == 0:
                self.hittime = 15
                self.hit = False

                # 死亡特效
                if self.hp <= 0:
                    self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                    for i in range(250):
                        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                    self.kill()
                    return
        # 正常时
        else:
            surf.blit(self.image, self.rect)

        self.mp += self.mprecovery

        if self.rect.left <= 0:
            self.rect.left = 0
            self.exact_pos[0] = self.rect.width/2
        elif self.rect.right >= 1800:
            self.rect.right = 1800
            self.exact_pos[0] = 1800 - self.rect.width/2

        miny = self.sprite_groups.playergroup.sprites()[0].rect.top
        if self.rect.bottom >= miny:
            self.rect.bottom = miny
            self.exact_pos[1] = miny - self.rect.height/2

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))

    def common_att(self):
        '''普通攻击'''
        if not self.overwhelmed:
            if self.mp >= self.COMMONATT_MP:
                self.mp -= self.COMMONATT_MP
                self.sprite_groups.enemybulletgroup.add(EnemyBullet_ch(BULLETIMG, self.rect.center, self.attack, player.rect.center, self.sprite_groups, self.attack))
                
    def AI(self):
        '''自动判断攻击'''
        if self.hp >= self.maxhp * 0.5:
            if self.mp >= self.maxmp * 0.7:
                self.common_att()
        else:
            self.common_att()

        self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
        d = get_distance(self.rect.center, self.aim)
        if d >= 300:
            self.move_to_aim((self.aim[0], self.aim[1] - 100))
        else:
            self.deg = oppo_deg(get_degree(self.rect.center, self.aim))
            self.movef()

    def boss(self):
        global screenhpbar_max
        self.maxmp = self.maxmp * 2
        self.mprecovery = 2
        self.image = pygame.transform.scale2x(self.image)
        self.hitsurf = self.image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))
        self.rect.size = (self.rect.width*2,self.rect.height*2)
        self.maxhp = int(math.sqrt(level)) * self.maxhp
        screenhpbar_max = self.maxhp
        self.hp = self.maxhp
        self.attack = int(self.attack * 1.5)
        self.speed = 15
        self.update = self.boss_update
        self.common_att = self.boss_common_att

    def boss_update(self, surf: pygame.surface.Surface):
        '''更新函数'''

        global screenhpbar_hp
        #调用AI
        self.boss_AI()

        #数值判断
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp

        # 显示
        if self.hit or self.hp <= 0:
            # 死亡时翻转
            if self.hp <= 0:
                s = pygame.transform.rotate(self.hitsurf, 90)
                s.set_colorkey((255, 0, 0, 125))
                surf.blit(s, self.rect)
            else:
                surf.blit(self.hitsurf, self.rect)

            # 击中时间
            self.hittime -= 1
            if self.hittime == 0:
                self.hittime = 15
                self.hit = False

                # 死亡特效
                if self.hp <= 0:
                    self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                    for i in range(250):
                        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                    self.kill()
                    return
        # 正常时
        else:
            surf.blit(self.image, self.rect)

        self.mp += self.mprecovery

        for i in range(10):
            r_pos = (random.randint(self.rect.left, self.rect.right), random.randint(self.rect.top, self.rect.bottom))
            self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), r_pos, random.randint(5, 75), 0, random.random()*50, colour=(100, 0, 170, 150)))

        if self.rect.left <= 0:
            self.rect.left = 0
            self.exact_pos[0] = self.rect.width/2
        elif self.rect.right >= 1800:
            self.rect.right = 1800
            self.exact_pos[0] = 1800 - self.rect.width/2

        miny = self.sprite_groups.playergroup.sprites()[0].rect.top
        if self.rect.bottom >= miny:
            self.rect.bottom = miny
            self.exact_pos[1] = miny - self.rect.height/2

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))
        
        screenhpbar_hp = self.hp

    def boss_AI(self):
        '''自动判断攻击'''
        if self.hp >= self.maxhp * 0.5:
            if self.mp >= self.maxmp * 0.7:
                self.common_att()
        else:
            self.common_att()

        self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
        d = get_distance(self.rect.center, self.aim)
        if d >= 400:
            self.move_to_aim((self.aim[0], self.aim[1] - 100))
        else:
            self.deg = -get_degree(self.rect.center, self.aim)
            self.movef()

    def boss_common_att(self):
        '''普通攻击'''
        if not self.overwhelmed:
            if self.mp >= self.COMMONATT_MP:
                self.mp -= self.COMMONATT_MP
                self.sprite_groups.enemybulletgroup.add(EnemyBullet_ch(BULLETIMG, self.rect.center, self.attack, player.rect.center, self.sprite_groups, self.attack, ['hp', 'san']))
   

# ---GIF类---

class GIF(pygame.sprite.Sprite):
    def __init__(self, size, imgs, center, deg=0, life=12):
        super().__init__()

        # 图像加载
        self.images = imgs
        for i in self.images:
            self.images[self.images.index(i)] = pygame.transform.rotate(i, deg)
        for i in self.images:
            self.images[self.images.index(i)] = pygame.transform.scale(i, size)
        
        self.image = self.images[0]

        self.deg = deg
        self.size = size
        self.rect = self.image.get_rect(center=center)
        self.life = life

        self.d = self.life/len(self.images)

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''

        # 绘制
        surf.blit(self.images[int(self.life / self.d)-1], self.rect)

        # 计时
        self.life = self.life - 1
        if self.life <= 1:
            self.kill()


# ---GIF加载器---

'''class GIFloader():
    def __init__(self, particlegroup):
        self.sprite_groups.particlegroup:pygame.sprite.Group = particlegroup
        self.poses = []

    def add(self):
        self.sprite_groups.particlegroup.'''
    

# ---玩家类---

class Player(Basic_sprite):
    def __init__(self, image, sprite_groups:Groups):
        super().__init__(image, (900, 950))

        # 数值初始化
        self.hp = 300
        self.maxhp = 300
        self.mp = 100
        self.maxmp = 100
        self.mprecovery = 0.5
        self.san = 100
        self.maxsan = 100
        self.sanrecovery = 0.5
        self.attack = 10
        self.COMMONATT_MP = 5
        self.SANATT_MP = 1
        self.PARRY_CD = 16
        self.parry_cd = self.PARRY_CD
        self.speed = 15
        self.overwhelmed = False

        # 被击中和冷却时间:用于呈现击中效果
        self.hit = False
        self.hittime = 15

        # 图层初始化
        self.images = [
            image.copy(),
            pygame.transform.flip(image.copy(), 1, 0)
        ]
        self.image = self.images[0]
        
        #重力常数
        self.v_y = 0

        # 位置初始化
        self.rect = self.image.get_rect()
        self.rect.center = (900, 950)

        # 组初始化
        self.sprite_groups = sprite_groups

    def rdamage(self, type, ammo):
        '''接受伤害'''

        if self.hp > 0:

            # 扣除血量
            if 'hp' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

            # 扣除精神值
            if 'san' in type:
                self.san -= ammo
                if self.san <= 0:
                    self.san = 0
                    self.overwhelmed = True
                    self.sprite_groups.damagerender.add('破防了!', self.rect.center,(255, 255, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center,(255, 255, 0), 60, 20)

            if 'heal' in type:
                self.hp += ammo
                self.maxhp += 5
                self.attack *= 1.005
                self.maxmp += 5
                self.mprecovery += 0.01
                self.sprite_groups.damagerender.add('+'+str(ammo), self.rect.center,(0, 255, 0), 60, 50)

        self.hit = True

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''

        global running, gameover

        self.mp += self.mprecovery

        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp
        if self.parry_cd < self.PARRY_CD:
            self.parry_cd += 1

        if self.parry_cd <= 8:
            a = self.parry_cd
            self.parry_cd = self.PARRY_CD
            self.parry()
            self.parry_cd = a

        if self.parry_cd == 1:
            for i in range(50):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 8, 30, 200, (0, 1, 0, 100)))

        

        self.v_y += GRAVITY
        if self.rect.bottom >= 950:
            self.rect.bottom = 925
            self.v_y = 0
        if 925 - self.rect.bottom < self.v_y:
            self.rect.bottom = 925
            self.v_y = 0
        else:
            self.rect.centery += self.v_y

        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= 1800:
            self.rect.right = 1800

        if self.hp <= 0:
            running = False
            gameover = True

        # 显示
        surf.blit(self.image, self.rect)

        if self.hit:
            for i in range(50):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 20, random.uniform(5, 10), 40, (0, 1, 0, 100)))
                self.hit = False

        for i in range(50):
            r_pos = (random.randint(self.rect.left, self.rect.right), self.rect.bottom+7)
            self.sprite_groups.particlegroup.add(Particle(random.randint(75, 105), r_pos, 10, random.uniform(10, 20), 20, (0, 1, 0, 100)))

        self.sprite_groups.particlegroup.add(Particle(random.randint(-45,225), (player.rect.center[0], player.rect.center[1] + 28), 15, random.uniform(0,3), 10, (255, 255, 255, 175)))
        self.sprite_groups.particlegroup.add(Particle(random.randint(-45,225), (player.rect.center[0], player.rect.center[1] + 28), 15, random.uniform(0,3), 20, (245, 82, 27, 225)))
        self.sprite_groups.particlegroup.add(Particle(random.randint(-45,225), (player.rect.center[0], player.rect.center[1] + 28), 15, random.uniform(0,3), 20, (247, 219, 26, 225)))

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))

    def common_att(self):
        '''普通攻击'''
        if not self.overwhelmed:
            if self.mp >= self.COMMONATT_MP:
                self.mp -= self.COMMONATT_MP
                self.sprite_groups.bulletgroup.add(FireBullet(FIREIMG, (self.rect.center[0], player.rect.center[1] + 28), 20, get_mouse_pos(), self.sprite_groups, dmg = self.attack))
    
    def san_att(self):
        if not self.overwhelmed:
            if self.mp >= self.SANATT_MP:
                self.mp -= self.SANATT_MP
                self.sprite_groups.bulletgroup.add(Runes(FIREIMG, (self.rect.center[0], player.rect.center[1] + 28), 20, get_mouse_pos(), self.sprite_groups, dmg = self.attack/2))
    
    def parry(self):
        if self.parry_cd == self.PARRY_CD:
            self.parry_cd = 0
            for i in self.sprite_groups.enemybulletgroup:
                if get_distance(self.rect.center, i.rect.center) < 180:
                    i.deg = oppo_deg(i.deg)
                    i.r_speed = 0
                    i.d_r_speed = 0
                    i.enemyg = self.sprite_groups.enemygroup
                    self.sprite_groups.enemybulletgroup.remove(i)
                    self.sprite_groups.bulletgroup.add(i)

    def move(self, direction):
        if direction == 'left':
            self.rect.centerx -= self.speed
            self.image = self.images[0]
        elif direction == 'right':
            self.rect.centerx += self.speed
            self.image = self.images[1]
        elif direction == 'up' and (self.rect.bottom == 925):
            self.rect.bottom = 924
            self.v_y = -45


# ---子弹类---

class Bullet(Basic_sprite):
    def __init__(self, image, pos, speed, aim, sprite_groups:Groups, dmg=10, type=['hp'], time=90):
        super().__init__(image, pos)
        
        self.image = image
        self.speed = speed
        self.aim = aim
        self.deg = random.randint(0, 360)
        self.dmg = dmg
        self.exact_pos = list(pos)
        self.type = type
        self.r_speed = 60
        self.time = time
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.enemygroup

    def update(self, surf: pygame.surface.Surface):

        if self.time >= 80:
            self.move_to_aim(self.aim)
        else:
            self.movef()

        surf.blit(pygame.transform.rotate(self.image, oppo_deg(self.deg)), self.rect)

        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:], c[0].rect.center, deg=135))
            c[0].rdamage(self.type, self.dmg)
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 15, random.uniform(0, 2), 10))
            self.kill()
            return

        if self.time <= 0:
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360),self.rect.center, 15, random.uniform(0, 2), 10))
            self.kill()

        self.time -= 1


# ---换场---

class Changer(Basic_sprite):
    def __init__(self, sprite_groups:Groups):
        super().__init__(pygame.surface.Surface((90,90)), (900, 700))

        # 数值初始化
        self.hp = 300
        self.maxhp = 300
        
        #重力常数
        self.v_y = 0

        # 组初始化
        self.sprite_groups = sprite_groups

    def rdamage(self, type, ammo):
        '''接受伤害'''

        ammo = ammo * 5

        if self.hp > 0:
            # 扣除血量
            if 'hp' in type or 'san' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

        self.hit = True

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''
        global level

        self.v_y += GRAVITY
        if self.rect.bottom >= 925:
            self.rect.bottom = 925
            self.v_y = 0
        if 925 - self.rect.bottom < self.v_y:
            self.rect.bottom = 925
            self.v_y = 0
        else:
            self.rect.centery += self.v_y
        #print(self.v_y)

        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= 1800:
            self.rect.right = 1800

        # 显示
        surf.blit(self.image, self.rect)

        for i in range(10):
            self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 20, random.uniform(5, 10), 40, (0, 1, 0, 100)))

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-50]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        if self.hp <= 0:
            level += 1
            change_round(self.rect.center)
            self.kill()


# ------------------自定义-------------

class FireBullet(Bullet):
    def __init__(self, image, pos, speed, aim, sprite_groups, dmg=10, type=['hp'], time=50):
        super().__init__(image, pos, speed, aim, sprite_groups, dmg, type, time)
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.enemyg = sprite_groups.enemygroup
        
    def update(self, surf: pygame.surface.Surface):
        if self.time >= 45:
            self.move_to_aim(self.aim)
        else:
            self.movef()

        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 7, random.uniform(0, 2), 40, (245, 82, 27, 225)))
        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 7, random.uniform(0, 2), 40, (247, 219, 26, 225)))

        surf.blit(self.image, self.rect)
        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:],c[0].rect.center, deg=135, life=4))
            c[0].rdamage(self.type, self.dmg)
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(0, 4), 30, (245, 82, 27, 225)))
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(0, 4), 30, (247, 219, 26, 225)))
            self.kill()
            return
        if self.time <= 0:
            self.kill()
        self.time -= 1

class EnemyBullet_ch(Basic_sprite):
    def __init__(self, image, pos, speed, aim, sprite_groups:Groups, dmg=10, type=['hp'], time=90):
        super().__init__(image, pos)
        
        self.speed = 5
        self.a = 0.05
        self.d_a = random.uniform(0.03, 0.09)
        self.d_r_speed = 1
        self.aim = aim
        self.deg = random.randint(0,360)
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.exact_pos = list(pos)
        font6 = pygame.font.SysFont('宋体',self.dmg*10)
        self.image = font6.render('6', 1, (255,255,255))
        self.type = type
        self.r_speed = 2
        self.time = time
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.playergroup

    def update(self, surf: pygame.surface.Surface):
        if self.time >= 75:
            self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
            self.move_to_aim(self.aim)
        else:
            self.movef()
        self.update_a()

        surf.blit(self.image, self.rect)

        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:], c[0].rect.center, deg=135))
            c[0].rdamage(self.type, self.dmg)
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 15, random.uniform(0, 2), 10))
            self.kill()
            return

        if self.time <= 0:
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360),self.rect.center, 15, random.uniform(0, 2), 10))
            self.kill()

        self.time -= 1

class EnemyBullet_sxz(Basic_sprite):
    def __init__(self, image, pos, speed, aim, sprite_groups:Groups, dmg=10, type=['hp'], time=45):
        super().__init__(image, pos)
        
        self.speed = 5
        self.a = 0.1
        self.d_a = 0.3
        self.aim = aim
        self.deg = get_degree(pos, aim)
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.exact_pos = list(pos)
        self.image = image
        self.type = type
        self.time = time
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.playergroup

    def update(self, surf: pygame.surface.Surface):
        self.movef()
        self.update_a()

        if self.deg >= 90 or self.deg <= -90:
            surf.blit(pygame.transform.rotate(self.image, oppo_deg(self.deg)), self.rect)
        else:
            surf.blit(pygame.transform.rotate(self.image, self.deg), self.rect)

        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:], c[0].rect.center, deg=135))
            c[0].rdamage(self.type, self.dmg)
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 15, random.uniform(0, 2), 10))
            self.kill()
            return

        if self.time <= 0:
            self.kill()

        self.time -= 1

class EnemyBullet_lefthand(Basic_sprite):
    def __init__(self, pos, speed, deg, sprite_groups:Groups, dmg=10, type=['hp'], time=45):
        super().__init__(pygame.surface.Surface((1,1)), pos)
        
        self.speed = 7
        self.a = 0.1
        self.d_a = 0.1
        self.deg = deg
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.exact_pos = list(pos)
        self.type = type
        self.time = time
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.playergroup

    def update(self, surf: pygame.surface.Surface):
        self.movef()
        self.update_a()

        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(0, 3), 50, (0, 150, 0, 150)))
        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(0, 3), 30, (0, 150, 0, 215)))

        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:], c[0].rect.center, deg=135))
            c[0].rdamage(self.type, self.dmg)
            for i in range(20):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 15, random.uniform(10, 20), 200, (0,150,0,170)))
            self.kill()
            return

        if self.time <= 0:
            self.kill()

        self.time -= 1

class HealBullet(Basic_sprite):
    def __init__(self, image, pos, speed, aim, sprite_groups, dmg=10, type=['heal'], time=90):
        super().__init__(image, pos)
        self.speed = 5
        self.a = 0.01
        self.d_a = random.uniform(0.01, 0.02)
        self.d_r_speed = 0.3
        self.aim = aim
        self.deg = random.randint(0,360)
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.exact_pos = list(pos)
        self.image = pygame.surface.Surface((1,1))
        self.type = type
        self.r_speed = 1
        self.time = time
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.playergroup

    def update(self, surf: pygame.surface.Surface):

        self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
        self.move_to_aim(self.aim)
        self.update_a()

        surf.blit(self.image, self.rect)
        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 40, random.uniform(0, 0.5), 20, (0, 255, 0, 150)))
        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 40, random.uniform(0, 0.5), 10, (0, 255, 0, 215)))

        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            #self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:], c[0].rect.center, deg=135))
            c[0].rdamage(self.type, self.dmg)
            for i in range(100):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 20, random.uniform(0, 1), 20, (0, 255, 0, 150)))
            self.kill()
            return

        if self.time <= 0:
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 90, random.uniform(0, 0.5), 10, (0, 255, 0, 150)))
            self.kill()

        self.time -= 1

class Runes(Bullet):
    def __init__(self, image, pos, speed, aim, sprite_groups:Groups, dmg=10, type=['san'], time=45):
        super().__init__(image, pos, speed, aim, sprite_groups, dmg, type, time)
        self.deg = get_degree(pos, aim)
        self.a = 1
        font = pygame.font.SysFont('simhei', 50, True)
        surf = font.render(random.choice(LIST), 1, (0,0,0))
        self.image = surf
        self.dmg = random.randint(int(dmg-int(dmg*0.2)),int(dmg+int(dmg*0.2)))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.sprite_groups = sprite_groups
        self.enemyg = sprite_groups.enemygroup

    def update(self, surf: pygame.surface.Surface):
        #print(self.rect.center, self.exact_pos)
        self.movef()
        self.update_a()

        surf.blit(self.image,self.rect)
        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(10, 20), 20, (0, 1, 0, 100)))
    
        c = pygame.sprite.spritecollide(self, self.enemyg, 0)
        if c:
            self.sprite_groups.particlegroup.add(GIF(c[0].rect.size, EXPLOSIONIMGS[:],c[0].rect.center, deg=135, life=4))
            c[0].rdamage(self.type, self.dmg)
            for i in range(10):
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, 10, random.uniform(5, 10), 20, (0, 1, 0, 100)))
            self.kill()
            return
        if self.time <= 0:
            self.kill()
        self.time -= 1

class Enemy_SXZ(Basic_sprite):
    def __init__(self, image, pos, sprite_groups:Groups, hp=100, mp=100, san=100):
        super().__init__(image, (900, 950))

        # 数值初始化
        self.hp = hp
        self.maxhp = hp
        self.mp = 0
        self.maxmp = mp
        self.mprecovery = 0.4
        self.san = san
        self.maxsan = san
        self.sanrecovery = 0.5
        self.attack = 10
        self.overwhelmed = False
        self.attacking = False

        #重力常数
        self.v_y = 0

        # 被击中和冷却时间:用于呈现击中效果
        self.hit = False
        self.hittime = 15

        # 图层初始化
        self.image = image.copy()
        self.image.convert_alpha()

        # 击中效果初始化
        self.hitsurf = image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))

        # 位置初始化
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # 组初始化
        self.sprite_groups = sprite_groups

        #数值
        self.COMMONATT_MP = 2.25

    def rdamage(self, type, ammo):
        '''接受伤害'''

        ammo *= 1.2
        ammo = int(ammo)

        if self.hp > 0:

            # 扣除血量
            if 'hp' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

            # 扣除精神值
            if 'san' in type:
                self.san -= ammo
                if self.san <= 0:
                    self.san = 0
                    self.overwhelmed = True
                    self.sprite_groups.damagerender.add('破防了!', self.rect.center,(255, 255, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center,(255, 255, 0), 60, 20)

            if 'heal' in type:
                self.hp += ammo
                self.sprite_groups.damagerender.add('+'+str(ammo), self.rect.center,(0, 255, 0), 60, 50)

        self.hit = True

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''
        
        #调用AI
        self.AI()

        #数值判断
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp

        # 显示
        if self.hit or self.hp <= 0:
            # 死亡时翻转
            if self.hp <= 0:
                s = pygame.transform.rotate(self.hitsurf, 90)
                s.set_colorkey((255, 0, 0, 125))
                surf.blit(s, self.rect)
            else:
                surf.blit(self.hitsurf, self.rect)

            # 击中时间
            self.hittime -= 1
            if self.hittime == 0:
                self.hittime = 15
                self.hit = False

                # 死亡特效
                if self.hp <= 0:
                    self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                    for i in range(250):
                        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                    self.kill()
                    return
        # 正常时
        else:
            surf.blit(self.image, self.rect)

        self.mp += self.mprecovery

        self.v_y += GRAVITY
        if self.rect.bottom >= 950:
            self.rect.bottom = 950
            self.exact_pos[1] = 950 - self.rect.height/2
            self.v_y = 0
        if 950 - self.rect.bottom < self.v_y:
            self.rect.bottom = 950
            self.exact_pos[1] = 950 - self.rect.height/2
            self.v_y = 0
        else:
            self.rect.centery += self.v_y

        if self.rect.left <= 0:
            self.rect.left = 0
            self.exact_pos[0] = self.rect.width/2
        elif self.rect.right >= 1800:
            self.rect.right = 1800
            self.exact_pos[0] = 1800 - self.rect.width/2

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))

    def common_att(self):
        '''普通攻击'''
        if not self.overwhelmed:
            if (self.mp >= self.COMMONATT_MP) and self.attacking:
                self.mp -= self.COMMONATT_MP
                b = random.choice([
                    EnemyBullet_sxz(BULLETIMG, self.rect.center, 20, self.sprite_groups.playergroup.sprites()[0].rect.center, self.sprite_groups, dmg = self.attack/10),
                    EnemyBullet_sxz(BULLETIMG, self.rect.center, 20, self.sprite_groups.playergroup.sprites()[0].rect.center, self.sprite_groups, dmg = self.attack/10, type=['san'])
                ])
                self.sprite_groups.enemybulletgroup.add(b)
    
    def AI(self):
        '''自动判断攻击'''
        if self.hp >= self.maxhp * 0.4:
            if self.mp >= self.maxmp:
                self.attacking = True
            elif self.attacking and (self.mp < self.COMMONATT_MP):
                self.attacking = False
            self.common_att()
        else:
            self.attacking = True
            self.common_att()

    def boss(self):
        global screenhpbar_max

        self.maxmp = self.maxmp * 2
        self.mprecovery = 0.6
        self.image = pygame.transform.scale2x(self.image)
        self.hitsurf = self.image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))
        self.rect.size = (self.rect.width*2,self.rect.height*2)
        self.maxhp = int(math.sqrt(level)) * self.maxhp
        screenhpbar_max = self.maxhp
        self.hp = self.maxhp
        self.attack = int(self.attack * 1.5)
        self.update = self.boss_update

    def boss_update(self, surf: pygame.surface.Surface):
        '''更新函数'''
        global screenhpbar_hp

        #调用AI
        self.AI()

        #数值判断
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp

        # 显示
        if self.hit or self.hp <= 0:
            # 死亡时翻转
            if self.hp <= 0:
                s = pygame.transform.rotate(self.hitsurf, 90)
                s.set_colorkey((255, 0, 0, 125))
                surf.blit(s, self.rect)
            else:
                surf.blit(self.hitsurf, self.rect)

            # 击中时间
            self.hittime -= 1
            if self.hittime == 0:
                self.hittime = 15
                self.hit = False

                # 死亡特效
                if self.hp <= 0:
                    self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                    for i in range(250):
                        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                    self.kill()
                    return
        # 正常时
        else:
            surf.blit(self.image, self.rect)

        self.mp += self.mprecovery

        for i in range(3):
            r_pos = (random.randint(self.rect.left, self.rect.right), random.randint(self.rect.top, self.rect.bottom))
            self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), r_pos, random.randint(5, 75), 0, random.random()*50, colour=(100, 0, 170, 150)))

        self.v_y += GRAVITY
        if self.rect.bottom >= 950:
            self.rect.bottom = 950
            self.exact_pos[1] = 950 - self.rect.height/2
            self.v_y = 0
        if 950 - self.rect.bottom < self.v_y:
            self.rect.bottom = 950
            self.exact_pos[1] = 950 - self.rect.height/2
            self.v_y = 0
        else:
            self.rect.centery += self.v_y

        if self.rect.left <= 0:
            self.rect.left = 0
            self.exact_pos[0] = self.rect.width/2
        elif self.rect.right >= 1800:
            self.rect.right = 1800
            self.exact_pos[0] = 1800 - self.rect.width/2

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))

        screenhpbar_hp = self.hp

class Enemy_GOD_LEFTHAND(Basic_sprite):
    def __init__(self, image, pos, sprite_groups:Groups, hp=100, mp=100, san=100):
        super().__init__(image, pos)

        # 数值初始化
        self.hp = hp
        self.maxhp = hp
        self.mp = 0
        self.maxmp = mp
        self.mprecovery = 0.4
        self.san = san
        self.maxsan = san
        self.sanrecovery = 0.5
        self.attack = 30
        self.overwhelmed = False
        self.attacking = False

        self.speed = 20

        #重力常数
        self.v_y = 0

        # 被击中和冷却时间:用于呈现击中效果
        self.hit = False
        self.hittime = 15

        # 图层初始化
        self.image = image.copy()
        self.image.convert_alpha()

        # 击中效果初始化
        self.hitsurf = image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))

        # 位置初始化
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # 组初始化
        self.sprite_groups = sprite_groups

        #数值
        self.COMMONATT_MP = self.maxmp/36

    def rdamage(self, type, ammo):
        '''接受伤害'''

        if self.hp > 0:

            # 扣除血量
            if 'hp' in type:
                self.hp -= ammo
                if self.hp <= 0:
                    self.sprite_groups.damagerender.add('R.I.P', self.rect.center,(255, 0, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center, (255, 0, 0), 60, 30)

            # 扣除精神值
            if 'san' in type:
                self.san -= ammo
                if self.san <= 0:
                    self.san = 0
                    self.overwhelmed = True
                    self.sprite_groups.damagerender.add('破防了!', self.rect.center,(255, 255, 0), 60, 50)
                else:
                    self.sprite_groups.damagerender.add(ammo, self.rect.center,(255, 255, 0), 60, 20)

            if 'heal' in type:
                self.hp += ammo
                self.sprite_groups.damagerender.add('+'+str(ammo), self.rect.center,(0, 255, 0), 60, 50)

        self.hit = True

    def update(self, surf: pygame.surface.Surface):
        '''更新函数'''
        
        #调用AI
        self.AI()

        #数值判断
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if (self.san < self.maxsan) and self.overwhelmed:
            self.san += self.sanrecovery
        elif self.san >= self.maxsan:
            self.san = self.maxsan
            self.overwhelmed = False
        if self.mp > self.maxmp:
            self.mp = self.maxmp

        # 显示
        if self.hit or self.hp <= 0:
            # 死亡时翻转
            if self.hp <= 0:
                s = pygame.transform.rotate(self.hitsurf, 90)
                s.set_colorkey((255, 0, 0, 125))
                surf.blit(s, self.rect)
            else:
                surf.blit(self.hitsurf, self.rect)

            # 击中时间
            self.hittime -= 1
            if self.hittime == 0:
                self.hittime = 15
                self.hit = False

                # 死亡特效
                if self.hp <= 0:
                    self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                    for i in range(250):
                        self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                    self.kill()
                    return
        # 正常时
        else:
            surf.blit(self.image, self.rect)

        self.mp += self.mprecovery

        miny = self.sprite_groups.playergroup.sprites()[0].rect.top
        if self.rect.bottom >= miny:
            self.rect.bottom = miny
            self.exact_pos[1] = miny - self.rect.height/2

        if self.rect.left <= 0:
            self.rect.left = 0
            self.exact_pos[0] = self.rect.width/2
        elif self.rect.right >= 1800:
            self.rect.right = 1800
            self.exact_pos[0] = 1800 - self.rect.width/2

        # 状态条更新
        hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
        hpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
        pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

        mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
        mpbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
        pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

        sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
        sanbarsize = [self.image.get_width(), 7]
        pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
        pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))

    def common_att(self, deg):
        '''普通攻击'''
        if not self.overwhelmed:
            if (self.mp >= self.COMMONATT_MP) and self.attacking:
                self.mp -= self.COMMONATT_MP
                self.sprite_groups.enemybulletgroup.add(EnemyBullet_lefthand(self.rect.center, 20, deg, self.sprite_groups, self.attack, ['hp']))
    
    def AI(self):
        '''自动判断攻击'''
        if self.mp >= self.maxmp:
            self.attacking = True
        elif self.attacking and (self.mp < self.COMMONATT_MP):
            self.attacking = False
        for i in range(0, 360, 10):
            self.common_att(i)

        self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
        d = get_distance(self.rect.center, self.aim)
        if d >= 300:
            self.move_to_aim((self.aim[0], self.aim[1] - 100))
        else:
            self.deg = - get_degree(self.rect.center, self.aim)
            self.movef()
        
    def boss(self):
        global screenhpbar_max

        self.maxmp = self.maxmp * 2
        self.mprecovery = 2
        self.image = pygame.transform.scale2x(self.image)
        self.hitsurf = self.image.copy()
        self.hitsurf.convert_alpha()
        surf = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        surf.fill((255, 0, 0, 125))
        self.hitsurf.blit(surf, (0, 0))
        self.hitsurf.set_colorkey((255, 0, 0, 125))
        self.rect.size = (self.rect.width*2,self.rect.height*2)
        self.maxhp = int(math.sqrt(level)) * self.maxhp
        screenhpbar_max = self.maxhp
        self.hp = self.maxhp
        self.attack = int(self.attack * 1.5)
        self.attack_time = 0
        self.attacking = True
        self.speed = 40
        self.update = self.boss_update

    def boss_update(self, surf: pygame.surface.Surface):
            '''boss更新函数'''
            global screenhpbar_hp

            #调用AI
            self.boss_AI()

            #数值判断
            if self.hp > self.maxhp:
                self.hp = self.maxhp
            if (self.san < self.maxsan) and self.overwhelmed:
                self.san += self.sanrecovery
            elif self.san >= self.maxsan:
                self.san = self.maxsan
                self.overwhelmed = False
            if self.mp > self.maxmp:
                self.mp = self.maxmp

            # 显示
            if self.hit or self.hp <= 0:
                # 死亡时翻转
                if self.hp <= 0:
                    s = pygame.transform.rotate(self.hitsurf, 90)
                    s.set_colorkey((255, 0, 0, 125))
                    surf.blit(s, self.rect)
                else:
                    surf.blit(self.hitsurf, self.rect)

                # 击中时间
                self.hittime -= 1
                if self.hittime == 0:
                    self.hittime = 15
                    self.hit = False

                    # 死亡特效
                    if self.hp <= 0:
                        for i in range(int(level/5)):
                            self.sprite_groups.enemybulletgroup.add(HealBullet(self.image, self.rect.center, 10, player.rect.center, self.sprite_groups, int(self.maxhp*0.5)))
                        for i in range(250):
                            self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), self.rect.center, random.randint(5, 75), speed=random.random()*2, size=random.uniform(25, 50), colour=(255, 0, 0, 150)))
                        self.kill()
                        return
            # 正常时
            else:
                surf.blit(self.image, self.rect)
            
            for i in range(10):
                r_pos = (random.randint(self.rect.left, self.rect.right), random.randint(self.rect.top, self.rect.bottom))
                self.sprite_groups.particlegroup.add(Particle(random.randint(0, 360), r_pos, random.randint(5, 75), 0, random.random()*50, colour=(100, 0, 170, 150)))

            self.mp += self.mprecovery

            miny = self.sprite_groups.playergroup.sprites()[0].rect.top
            if self.rect.bottom >= miny:
                self.rect.bottom = miny
                self.exact_pos[1] = miny - self.rect.height/2

            if self.rect.left <= 0:
                self.rect.left = 0
                self.exact_pos[0] = self.rect.width/2
            elif self.rect.right >= 1800:
                self.rect.right = 1800
                self.exact_pos[0] = 1800 - self.rect.width/2

            # 状态条更新
            hpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-7]
            hpbarsize = [self.image.get_width(), 7]
            pygame.draw.rect(surf, (0, 0, 0), (hpbarpos, hpbarsize), 1)
            pygame.draw.rect(surf, (255, 0, 0), ((hpbarpos[0]+1, hpbarpos[1]+1), ((hpbarsize[0]-2)*self.hp/self.maxhp, hpbarsize[1]-2)))

            mpbarpos = [self.rect.topleft[0], self.rect.topleft[1]-14]
            mpbarsize = [self.image.get_width(), 7]
            pygame.draw.rect(surf, (0, 0, 0), (mpbarpos, mpbarsize), 1)
            pygame.draw.rect(surf, (0, 0, 255), ((mpbarpos[0]+1, mpbarpos[1]+1), ((mpbarsize[0]-2)*self.mp/self.maxmp, mpbarsize[1]-2)))

            sanbarpos = [self.rect.topleft[0], self.rect.topleft[1]-21]
            sanbarsize = [self.image.get_width(), 7]
            pygame.draw.rect(surf, (0, 0, 0), (sanbarpos, sanbarsize), 1)
            pygame.draw.rect(surf, (255, 255, 0), ((sanbarpos[0]+1, sanbarpos[1]+1), ((sanbarsize[0]-2)*self.san/self.maxsan, sanbarsize[1]-2)))
      
            screenhpbar_hp = self.hp

    def boss_AI(self):
        '''自动判断攻击(boss)'''
        self.attack_time += 1
        if self.attack_time > 36:
            self.attack_time = 0
        
        if self.mp >= self.maxmp:
            for i in range(0, 360, 10):
                self.common_att(i)
        if self.attack_time % 2 == 0:
            self.common_att(self.attack_time*10)

        self.aim = self.sprite_groups.playergroup.sprites()[0].rect.center
        d = get_distance(self.rect.center, self.aim)
        if d >= 300:
            self.move_to_aim((self.aim[0], self.aim[1] - 100))
        else:
            self.deg = - get_degree(self.rect.center, self.aim)
            self.movef()

# -------------------------------------

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('.\\images\\bg.png').convert()
screen = pygame.surface.Surface((1800,1000))

clock = pygame.time.Clock()

pclg = pygame.sprite.Group()
dmgr = Dmgrender(screen)
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bglines = pygame.sprite.Group()
playerg = pygame.sprite.Group()
enemybullets = pygame.sprite.Group()

#useableparticles = pygame.sprite.Group()

# ---常量定义---
level = 0

ENEMYIMG_CH = pygame.image.load(".\\images\\figure\\CH.png").convert_alpha()
ENEMYIMG_SXZ = pygame.image.load(".\\images\\figure\\SXZ.png").convert_alpha()
ENEMYIMG_LEFTHAND = pygame.image.load(".\\images\\figure\\lefthand.png").convert_alpha()
bfont = pygame.font.SysFont('simhei', 50)
BULLETIMG = bfont.render('啊对对对', 1, (255,255,255))
FIREIMG = pygame.surface.Surface((1, 1))
FIREIMG.fill((0,0,0))

LIST = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ','μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ']
GRAVITY = 4
EXPLOSIONIMGS = [pygame.image.load('.\\images\\sweep\\sweep0.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep1.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep2.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep3.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep4.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep5.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep6.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep7.png').convert_alpha(),
                 pygame.image.load('.\\images\\sweep\\sweep8.png').convert_alpha(),
                 ]

screenfont = pygame.font.SysFont('simhei', 25)
screenhpbar_hp = 0
screenhpbar_max = 999


groups = Groups()

#enemies.add(Enemy_CH(ENEMYIMG_CH, (17, 300), groups, hp=333))
#enemies.add(Enemy_CH(ENEMYIMG_CH, (170, 300), groups, hp=333), Enemy_CH(ENEMYIMG_CH, (220, 170), groups, hp=333), Enemy_CH(ENEMYIMG_CH, (220, 430), groups, hp=333))
player = Player(pygame.image.load('.\\images\\figure\\LZH.png').convert_alpha(),groups)

playerg.add(player)

running = True
pause = False
gameover = False

kleft = False
kright = False

rounds = {
    1 : [Enemy_GOD_LEFTHAND(ENEMYIMG_LEFTHAND, (0, 0), groups, 333)],
    2 : [Enemy_SXZ(ENEMYIMG_SXZ, (0, 0), groups, 333)],
    3 : [Enemy_CH(ENEMYIMG_CH, (17, 300), groups, 333)],
    4 : [Enemy_CH(ENEMYIMG_CH, (170, 300), groups, 333), Enemy_CH(ENEMYIMG_CH, (220, 170), groups, 333), Enemy_CH(ENEMYIMG_CH, (220, 430), groups, 333)]
}

while running:
    clock.tick(30)
    window.fill((0,0,0))
    #print(clock.get_fps(),end='\r')

    if len(enemies) == 0:
        enemies.add(Changer(groups))

    if pause:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    pause = not pause
        continue
    
    screen.blit(background, ((0,0), (1800,1000)))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                pause = not pause
            elif event.key == K_a:
                kleft = True
            elif event.key == K_d:
                kright = True
            elif event.key == K_w:
                player.move('up')

        elif event.type == KEYUP:
            if event.key == K_a:
                kleft = False
            elif event.key == K_d:
                kright = False

        elif event.type == MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[2]:
                player.parry()
            elif pygame.mouse.get_pressed()[0]:
                for i in range(10):
                    player.common_att()
            elif pygame.mouse.get_pressed()[1]:
                pass
            else:
                player.san_att()
            
    if kleft:
        player.move('left')
    if kright:
        player.move('right')

    enemies.update(screen)
    playerg.update(screen)
    bullets.update(screen)
    enemybullets.update(screen)
    pclg.update(screen)
    dmgr.update()

    #pygame.draw.circle(screen, (0,0,0), player.rect.center, 200, 1)

    x, y = get_mouse_pos()
    pygame.draw.arc(screen, (0,255,255), ((x-15,y-15), (30, 30)), math.pi/2-math.pi*(player.parry_cd/player.PARRY_CD)*2, math.pi/2, 10)

    x, y = player.rect.center
    x = SCREEN_WIDTH/2 - x
    y = SCREEN_HEIGHT/2 - y + 100
    window.blit(screen, (x, y))
    
    if (level + 1) % 5 == 0:
        window.blit(screenfont.render('当前等级:'+str(level), 1, (255,0,0)), (0,0))
    else:
        window.blit(screenfont.render('当前等级:'+str(level), 1, (255,255,255)), (0,0))


    pygame.draw.rect(window, (255, 0, 0), ((0, 0), (SCREEN_WIDTH*screenhpbar_hp/screenhpbar_max, 20)))

    pygame.display.flip()



font_gv = pygame.font.SysFont('宋体', 180)
surf = font_gv.render('GAME OVER', 1, (255,255,255))
time = 120

while gameover:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            gameover = False
    time -= 1
    if time <= 0:
        break
    if time <= 90:
        window.blit(surf, (400-surf.get_width()/2, 300-surf.get_height()/2))

    pygame.display.flip()
    
pygame.quit()
