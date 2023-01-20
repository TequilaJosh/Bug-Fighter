from random import randint
import pygame
import sys
from settings import *


pygame.init()
main_window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bug Fighter')
clock = pygame.time.Clock()
BG = pygame.transform.scale(pygame.image.load('./Assets/BG.jpg').convert(), (WIDTH, HEIGHT))

def get_high():
    with open('./Assets/HS.txt', 'r') as HS:
        try:
            high_score = int(HS.readline())
        except ValueError:
            high_score = 0
    return high_score


def play():
    class Player(pygame.sprite.Sprite):
        def __init__(self, pos, groups):
            super().__init__(groups)
            self.image = pygame.transform.scale(pygame.image.load('./Assets//ship.png').convert_alpha(), (52, 52))
            self.rect = self.image.get_rect(center=pos)
            self.pos = pygame.math.Vector2(self.rect.center)
            self.direction = pygame.math.Vector2()
            self.speed = 200
            self.mask = pygame.mask.from_surface(self.image)
            self.can_shoot = True
            self.shoot_time = None
            self.score = 0
            self.health = 3
            self.cannons = 1
            self.cannon_offset = self.rect.width / (self.cannons + 1)

        def move(self, dt):
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            self.pos += self.direction * self.speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        def input(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.pos.x > 0 + self.rect.width / 2:
                self.image = pygame.transform.scale(pygame.image.load('./Assets//ship_left.png').convert_alpha(), (52, 52))
                self.direction.x = -1
            elif keys[pygame.K_RIGHT] and self.pos.x < WIDTH - + self.rect.width / 2:
                self.image = pygame.transform.scale(pygame.image.load('./Assets//ship_right.png').convert_alpha(), (52, 52))
                self.direction.x = 1
            else:
                self.image = pygame.transform.scale(pygame.image.load('./Assets//ship.png').convert_alpha(), (52, 52))
                self.direction.x = 0
            if keys[pygame.K_SPACE] and self.can_shoot:
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()
                # if self.cannons == 1:
                #     Lasers(self.rect.midtop, laser_group)
                # elif self.cannons == 2:
                #     Lasers(self.rect.midleft, laser_group)
                #     Lasers(self.rect.midright, laser_group)
                for cannon in range(self.cannons):
                    Lasers((self.rect.x + self.cannon_offset * (cannon + 1), self.rect.y), laser_group)

        def laser_timer(self):
            if not self.can_shoot:
                current_time = pygame.time.get_ticks()
                if current_time - self.shoot_time > 250:
                    self.can_shoot = True

        def take_collision(self):
            if pygame.sprite.spritecollide(self, bug_group, True, pygame.sprite.collide_mask):
                if self.health >= 1:
                    self.health -= 1
                if self.health == 0:
                    if self.score > get_high():
                        with open('./Assets/HS.txt', 'w') as newHS:
                            newHS.write(str(self.score))

                    main_menu()

        def update(self, dt):
            self.input()
            self.move(dt)
            self.laser_timer()
            self.take_collision()

    class Powerups(pygame.sprite.Sprite):
        def __init__(self, pos, type, groups):
            super().__init__(groups)
            self.image = pygame.image.load(f'./Assets/{type}.png').convert_alpha()
            self.rect = self.image.get_rect(center=pos)
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(0, 1)
            self.vel = 100
            self.mask = pygame.mask.from_surface(self.image)
            self.type = type

        def player_collision(self):
            if pygame.sprite.spritecollide(self, all_sprites, False, pygame.sprite.collide_mask):
                if self.type == 'heart':
                    player_one.health += 1
                elif self.type == 'attack_up':
                    player_one.cannons += 1
                    player_one.cannon_offset = player_one.rect.width / (player_one.cannons + 1)
                self.remove(health_group)

        def update(self, dt):
            self.pos += self.direction * self.vel * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            self.player_collision()

    class Lasers(pygame.sprite.Sprite):
        def __init__(self, pos, groups):
            super().__init__(groups)
            self.image = pygame.image.load('./Assets/shot_1.png').convert_alpha()
            self.rect = self.image.get_rect(midbottom=pos)
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(0, -1)
            self.vel = 600
            self.mask = pygame.mask.from_surface(self.image)

        def bug_collision(self, pos):
            if pygame.sprite.spritecollide(self, bug_group, True, pygame.sprite.collide_mask):
                player_one.score += 1
                # explode(self.pos)
                roll = randint(1, 100)
                if 10 > roll > 5:
                    Powerups(pos, 'heart', health_group)
                if 15 > roll > 11:
                    Powerups(pos, 'attack_up', health_group)
                self.remove(laser_group)

        def update(self, dt):
            self.pos += self.direction * self.vel * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            self.bug_collision(self.pos)

    class Bugs(pygame.sprite.Sprite):
        def __init__(self, pos, image, groups):
            super().__init__(groups)
            self.image = pygame.image.load(f'./Assets/{image}.png').convert_alpha()
            self.rect = self.image.get_rect(center=pos)
            self.pos = pygame.math.Vector2(self.rect.midbottom)
            self.vel = randint(100, 200)
            self.direction = pygame.math.Vector2(0, 1)
            self.mask = pygame.mask.from_surface(self.image)

        def update(self, dt):
            self.pos += self.direction * self.vel * dt
            self.rect.midbottom = (round(self.pos.x), round(self.pos.y))

            if self.rect.top > HEIGHT:
                self.kill()

    class Score:
        def __init__(self):
            self.font = pygame.font.Font('./Assets/subatomic.ttf', 30)

        def display(self, text, pos):
            display_text = text
            text_surf = self.font.render(display_text, True, 'white')
            text_rect = text_surf.get_rect(center=pos)
            main_window.blit(text_surf, text_rect)

    health_group = pygame.sprite.Group()
    bug_group = pygame.sprite.Group()
    laser_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    player_one = Player((200, 540), all_sprites)
    score = Score()

    bug_timer = pygame.event.custom_type()
    pygame.time.set_timer(bug_timer, randint(300, 1000))

    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == bug_timer:
                bug_x_pos, bug_y_pos = randint(-10, 0), randint(0, WIDTH)
                Bugs((bug_y_pos, bug_x_pos), 'Ladyb', bug_group)

        main_window.blit(BG, (0, 0))
        score.display(f'HP:{player_one.health}', (50, 20))
        score.display(f'score:{player_one.score}', (WIDTH - 90, 20))
        all_sprites.update(dt)
        all_sprites.draw(main_window)
        laser_group.update(dt)
        laser_group.draw(main_window)
        bug_group.update(dt)
        bug_group.draw(main_window)
        health_group.update(dt)
        health_group.draw(main_window)
        pygame.display.update()


def main_menu():

    menu_font = pygame.font.Font('./Assets/subatomic.ttf', 50)
    score_font = pygame.font.Font('./Assets/subatomic.ttf', 25)
    play_text = menu_font.render('PLAY', True, 'white')
    play_rect = play_text.get_rect(center=(WIDTH/2, HEIGHT/2))
    exit_text = menu_font.render('EXIT', True, ' white')
    exit_rect = exit_text.get_rect(topleft=(play_rect.x + 12, play_rect.y + 80))
    hs_text = score_font.render(f'High Score {get_high()}', True, ' white')
    hs_rect = hs_text.get_rect(topright=(WIDTH - 30, 20))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[0]:
                menu_mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(menu_mouse_pos):
                    play()
                if exit_rect.collidepoint(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        main_window.blit(BG, (0, 0))
        main_window.blit(play_text, play_rect)
        main_window.blit(exit_text, exit_rect)
        main_window.blit(hs_text, hs_rect)
        pygame.display.update()


main_menu()
