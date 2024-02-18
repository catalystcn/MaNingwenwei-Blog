import sys

import pygame
import random

# 初始化Pygame
pygame.init()

# 设置窗口大小
size = (700, 500)
screen = pygame.display.set_mode(size)

# 设置窗口标题
pygame.display.set_caption("My Game")

# 设置矩形位置和大小
rect_x = 0
rect_y = 400
rect_width = 700
rect_height = 50

# 设置颜色
red = (0, 0, 0)
init_x=random.randint(0,650)
init_x2=random.randint(0,650)
init_x3=random.randint(0,650)
init_x4=random.randint(0,650)

# 创建精灵
class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 350

class BadSprite(pygame.sprite.Sprite):
    def __init__(self,init_x,init_y):
        super().__init__()
        self.image = pygame.Surface([50, 80])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y


# 添加精灵到组中
my_group = pygame.sprite.Group()
my_sprite = MySprite()
bad_sprite = BadSprite(init_x,-80)
bad_sprite2 = BadSprite(init_x,-80)
my_group.add(my_sprite,bad_sprite)

# 创建时钟对象
clock = pygame.time.Clock()

green=0,255,0
gameover = pygame.font.Font(None, 60)
textImage = gameover.render('GAME OVER', True, green)

# 游戏循环
done = False
while True:

    # 处理事件
    for event in pygame.event.get():
        pygame.key.set_repeat(1, 1)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                my_sprite.rect.x -= 1
            elif event.key == pygame.K_RIGHT:
                my_sprite.rect.x += 1

        if  my_sprite.rect.x <= 0:
            my_sprite.rect.x += 1
        elif my_sprite.rect.x >= 650:
            my_sprite.rect.x -= 1

    bad_sprite.rect.y += 10
    if bad_sprite.rect.y == 500:
        init_x = random.randint(0, 650)
        bad_sprite = BadSprite(init_x, -80)
        my_group.add(my_sprite, bad_sprite)

    crash_result = pygame.sprite.collide_rect(my_sprite, bad_sprite)
    if crash_result:
        done = True

    if done == False:
        # 填充窗口颜色
        screen.fill((255, 255, 255))
        # 绘制矩形
        pygame.draw.rect(screen, red, [rect_x, rect_y, rect_width, rect_height])
        # 绘制精灵
        my_group.draw(screen)
    else:
        screen.blit(textImage, (100, 100))

    # 更新窗口
    pygame.display.update()

    # 控制游戏帧率
    clock.tick(60)


# 退出Pygame
pygame.quit()


# 退出Pygame