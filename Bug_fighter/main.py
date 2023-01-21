from random import randint
import pygame
import sys
from settings import *


pygame.init()
main_window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bug Fighter')
clock = pygame.time.Clock()
BG = pygame.transform.scale(pygame.image.load('./Assets/BG.jpg').convert(), (WIDTH, HEIGHT))
# laser_sound = pygame.mixer.Sound('./Assets/Music/laser.wav')
def get_high():
    with open('./Assets/HS.txt', 'r') as HS:
        try:
            high_score = int(HS.readline())
        except ValueError:
            high_score = 0
    return high_score


def play():
    # pygame.mixer.music.load('./Assets/Music/play_music.wav')
    # pygame.mixer.music.set_volume(0.5)
    # pygame.mixer.music.play()
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
            self.max_hp = 10
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
                # pygame.mixer.Sound.play(laser_sound)
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
                if self.type == 'heart' and player_one.health < player_one.max_hp:
                    player_one.health += 1
                elif self.type == 'attack_up' and player_one.cannons < 5:
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


def controls_menu():
    menu_font = pygame.font.Font('./Assets/subatomic.ttf', 20)
    move_left_descript_text = menu_font.render('Move left', True, 'white')
    move_left_descript_rect = move_left_descript_text.get_rect(topleft=(20, 80))
    move_left_img = menu_font.render('Left arrow', True, 'white')
    move_left_img_rect = move_left_img.get_rect(topright=(WIDTH - 20, move_left_descript_rect.y))
    move_right_descript_text = menu_font.render('Move right', True, 'white')
    move_right_descript_rect = move_right_descript_text.get_rect(topleft=(20, move_left_img_rect.y + 50))
    move_right_img = menu_font.render('Right arrow', True, 'white')
    move_right_img_rect = move_right_img.get_rect(topright=(WIDTH - 20, move_right_descript_rect.y))
    shoot_descript_text = menu_font.render('Shoot', True, 'white')
    shoot_descript_rect = shoot_descript_text.get_rect(topleft=(20, move_right_img_rect.y + 50))
    shoot_img = menu_font.render('Space', True, 'white')
    shoot_img_rect = shoot_img.get_rect(topright=(WIDTH - 20, shoot_descript_rect.y))
    powerup_title_text = menu_font.render('Power ups', True, 'white')
    powerup_title_rect = powerup_title_text.get_rect(center=(WIDTH / 2, shoot_img_rect.y + 50))
    heart_img = pygame.image.load('./Assets/heart.png').convert_alpha()
    heart_rect = heart_img.get_rect(topleft=(20, powerup_title_rect.y + 50))
    heart_descript_text = menu_font.render('Restore 1 Health', True, 'white')
    heart_descript_rect = heart_descript_text.get_rect(topright=(WIDTH - 20, heart_rect.y))
    attack_up_img = pygame.image.load('./Assets/attack_up.png').convert_alpha()
    attack_up_rect = attack_up_img.get_rect(topleft=(20, heart_rect.y + 50))
    attack_up_descript_text = menu_font.render('Restore 1 Health', True, 'white')
    attack_up_descript_rect = attack_up_descript_text.get_rect(topright=(WIDTH - 20, attack_up_rect.y))
    exit_descript_text = menu_font.render('EXIT', True, 'white')
    exit_descript_rect = exit_descript_text.get_rect(center=(WIDTH / 2, attack_up_descript_rect.y + 50))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[0]:
                menu_mouse_pos = pygame.mouse.get_pos()
                if exit_descript_rect.collidepoint(menu_mouse_pos):
                    main_menu()

        main_window.blit(BG, (0, 0))
        main_window.blit(move_left_descript_text, move_left_descript_rect)
        main_window.blit(move_left_img, move_left_img_rect)
        main_window.blit(move_right_descript_text, move_right_descript_rect)
        main_window.blit(move_right_img, move_right_img_rect)
        main_window.blit(shoot_descript_text, shoot_descript_rect)
        main_window.blit(shoot_img, shoot_img_rect)
        main_window.blit(exit_descript_text, exit_descript_rect)
        main_window.blit(powerup_title_text, powerup_title_rect)
        main_window.blit(heart_img, heart_rect)
        main_window.blit(heart_descript_text, heart_descript_rect)
        main_window.blit(attack_up_descript_text, attack_up_descript_rect)
        main_window.blit(attack_up_img, attack_up_rect)
        pygame.display.update()


def credits():
    menu_font = pygame.font.Font('./Assets/subatomic.ttf', 20)
    move_left_descript_text = menu_font.render('Music by', True, 'white')
    move_left_descript_rect = move_left_descript_text.get_rect(topleft=(20, 80))
    move_left_img = menu_font.render('BloodPixelHero', True, 'white')
    move_left_img_rect = move_left_img.get_rect(topright=(WIDTH - 20, move_left_descript_rect.y))
    move_right_descript_text = menu_font.render('Sound Effects by', True, 'white')
    move_right_descript_rect = move_right_descript_text.get_rect(topleft=(20, move_left_img_rect.y + 50))
    move_right_img = menu_font.render('Jobro', True, 'white')
    move_right_img_rect = move_right_img.get_rect(topright=(WIDTH - 20, move_right_descript_rect.y))
    shoot_descript_text = menu_font.render('Graphics by', True, 'white')
    shoot_descript_rect = shoot_descript_text.get_rect(topleft=(20, move_right_img_rect.y + 50))
    shoot_img = menu_font.render('TequilaJosh', True, 'white')
    shoot_img_rect = shoot_img.get_rect(topright=(WIDTH - 20, shoot_descript_rect.y))
    exit_descript_text = menu_font.render('EXIT', True, 'white')
    exit_descript_rect = exit_descript_text.get_rect(center=(WIDTH / 2, shoot_img_rect.y + 50))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[0]:
                menu_mouse_pos = pygame.mouse.get_pos()
                if exit_descript_rect.collidepoint(menu_mouse_pos):
                    main_menu()

        main_window.blit(BG, (0, 0))
        main_window.blit(move_left_descript_text, move_left_descript_rect)
        main_window.blit(move_left_img, move_left_img_rect)
        main_window.blit(move_right_descript_text, move_right_descript_rect)
        main_window.blit(move_right_img, move_right_img_rect)
        main_window.blit(shoot_descript_text, shoot_descript_rect)
        main_window.blit(shoot_img, shoot_img_rect)
        main_window.blit(exit_descript_text, exit_descript_rect)
        pygame.display.update()

def main_menu():
    # pygame.mixer.music.load('./Assets/Music/menu_music.wav')
    # pygame.mixer.music.set_volume(0.5)
    # pygame.mixer.music.play()
    menu_font = pygame.font.Font('./Assets/subatomic.ttf', 50)
    score_font = pygame.font.Font('./Assets/subatomic.ttf', 25)
    play_text = menu_font.render('PLAY', True, 'white')
    play_rect = play_text.get_rect(center=(WIDTH/2 , HEIGHT/2 - 50))
    options_text = menu_font.render('CONTROLS', True, 'white')
    options_rect = options_text.get_rect(center=(WIDTH / 2, play_rect.y + 90))
    exit_text = menu_font.render('EXIT', True, ' white')
    exit_rect = exit_text.get_rect(center=(WIDTH / 2, options_rect.y + 90))
    hs_text = score_font.render(f'High Score {get_high()}', True, ' white')
    hs_rect = hs_text.get_rect(topright=(WIDTH - 30, 20))
    credit_text = score_font.render('Credits', True, ' white')
    credit_rect = credit_text.get_rect(topleft=(30, hs_rect.y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[0]:
                menu_mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(menu_mouse_pos):
                    pygame.mixer.music.unload()
                    play()
                if options_rect.collidepoint(menu_mouse_pos):
                    controls_menu()
                if credit_rect.collidepoint(menu_mouse_pos):
                    credits()
                if exit_rect.collidepoint(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        main_window.blit(BG, (0, 0))
        main_window.blit(play_text, play_rect)
        main_window.blit(exit_text, exit_rect)
        main_window.blit(options_text, options_rect)
        main_window.blit(hs_text, hs_rect)
        main_window.blit(credit_text, credit_rect)
        pygame.display.update()


main_menu()
