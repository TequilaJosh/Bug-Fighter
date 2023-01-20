import pygame
import sys
from random import randint, uniform


class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)  # init sprite class of pygame
        self.image = pygame.image.load('./graphics/ship.png').convert_alpha()  # sprite class always requires a surface
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))  # sprite also requires a rect

        # add a mask
        self.mask = pygame.mask.from_surface(self.image)

        # Timer
        self.can_shoot = True
        self.shoot_time = None

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 250:
                self.can_shoot = True

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Lasers(self.rect.midtop, laser_group)

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask):
            explode_sound.play()
            pygame.quit()
            sys.exit()

    def update(self):
        self.input_position()
        self.laser_timer()
        self.laser_shoot()
        self.meteor_collision()


class Lasers(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.vel = 600
        self.mask = pygame.mask.from_surface(self.image)

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            self.remove(laser_group)
            explode_sound.play()

    def update(self):
        self.pos += self.direction * self.vel * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.meteor_collision()
        if self.rect.bottom < 0:
            self.kill()


class Meteors(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(pygame.image.load('./graphics/meteor.png'),
                                            (randint(32, 96), randint(32, 96)))
        self.scaled_surf = self.image
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.math.Vector2(self.rect.midbottom)
        self.vel = randint(100, 400)
        self.direction = pygame.math.Vector2(uniform(-1, 1), 1)
        self.rotation = 0
        self.rotation_speed = randint(20, 80)
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotate_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotate_surf
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.direction * self.vel * dt
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.rotate()

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score:
    def __init__(self):
        self.font = pygame.font.Font('./graphics/subatomic.ttf', 50)

    def display(self):
        score_text = f'Score: {pygame.time.get_ticks() // 1000}'
        text_surf = self.font.render(score_text, True, 'white')
        text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 30), width=8, border_radius=5)


pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 120
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Asteroid Blaster')
clock = pygame.time.Clock()

# sounds
laser_sound = pygame.mixer.Sound('./sounds/laser.ogg')
explode_sound = pygame.mixer.Sound('./sounds/explosion.wav')

# background
background_surf = pygame.image.load('./graphics/background.png')

# sprite groups
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# sprite creation
ship = Ship(spaceship_group)
score = Score()

# timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, randint(300, 500))

while True:
    dt = clock.tick(FPS) / 1000 # Delta time
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # close if player clicks X button
            pygame.quit()
            sys.exit()
        if event.type == meteor_timer:
            meteor_y_pos, meteor_x_pos = randint(-150, -50), randint(-100, WINDOW_WIDTH + 100)
            Meteors((meteor_x_pos, meteor_y_pos), meteor_group)

    # background
    display_surface.blit(background_surf, (0, 0))

    # update method
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()

    # draw graphics
    score.display()
    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    pygame.display.flip()
