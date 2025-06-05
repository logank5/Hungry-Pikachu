import pygame, sys
from pygame.locals import *
import random, time
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
import asyncio

# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

HIGH_SCORE = 0
LAST_SCORE = 0
random.seed(time.time())

def create_surface_with_text(text, font_size, text_rgb, bg_rgb, bold=False):
    font = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf", int(font_size))
    font.set_bold(bold)
    surface = font.render(text,True, text_rgb, bg_rgb)
    return surface.convert_alpha()

class UIElement(Sprite):
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        self.mouse_over = False

        self.click_sound = pygame.mixer.Sound("assets/sounds/pokeselect.wav")
        self.click_sound.set_volume(0.1)

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb, bold=False
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=int(font_size * 1.4), text_rgb=pygame.Color("#fffca7"), bg_rgb=bg_rgb, bold=True
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # calls the init method of the parent sprite class
        super().__init__()
        self.action = action

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                self.click_sound.play()
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    HOWTO = 2

class Apricorn(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.randomize()

    def randomize(self):
        apricorn = random.choice([
            "redapricorn", "blueapricorn", "pinkapricorn", "whiteapricorn", "yellowapricorn"
        ])
        image = pygame.image.load(f"assets/objects/{apricorn}.png")
        self.image = pygame.transform.scale(image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = (
            random.randint(32, self.screen_width - 32),
            random.randint(32, self.screen_height - 32)
        )
            
    def draw(self, surface):
        surface.blit(self.image, self.rect) 


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, velocity):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity = velocity
        self.images_right = []
        self.images_left = []
        self.images_up = []
        self.images_down = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img_right = pygame.image.load(f'assets/avatars/pikachuright{num}.png')
            img_right = pygame.transform.scale(img_right, (64, 64))
            img_left = pygame.image.load(f'assets/avatars/pikachuleft{num}.png')
            img_left = pygame.transform.scale(img_left, (64, 64))
            img_up = pygame.image.load(f'assets/avatars/pikachuback{num}.png')
            img_up = pygame.transform.scale(img_up, (64, 64))
            img_down = pygame.image.load(f'assets/avatars/pikachuforward{num}.png')
            img_down = pygame.transform.scale(img_down, (64, 64))
            self.images_right.append(img_right)
            self.images_left.append(img_left)
            self.images_up.append(img_up)
            self.images_down.append(img_down)

        self.image = pygame.image.load('assets/avatars/pikachuidle.png')
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(100, self.screen_width - 100), random.randint(100, self.screen_height - 100))
        self.direction = 0

    def update(self):
        walk_cooldown = 12

        pressed_keys = pygame.key.get_pressed()
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.counter += 1
                self.rect.move_ip(0, -self.velocity)
                self.direction = 3
        if self.rect.bottom < self.screen_height:
            if pressed_keys[K_DOWN]:
                self.counter += 1
                self.rect.move_ip(0,self.velocity)
                self.direction = 4
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                self.counter += 1
                self.rect.move_ip(-self.velocity, 0)
                self.direction = 2
        if self.rect.right < self.screen_width:        
              if pressed_keys[K_RIGHT]:
                self.counter += 1
                self.rect.move_ip(self.velocity, 0)
                self.direction = 1

        
        if pressed_keys[K_LEFT] == False and pressed_keys[K_RIGHT] == False and pressed_keys[K_UP] == False and pressed_keys[K_DOWN] == False:
            self.counter = 0
            self.index = 0
            self.image = pygame.image.load('assets/avatars/pikachuidle.png')
            self.image = pygame.transform.scale(self.image, (64, 64))


        #handle animation
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == 2:
                self.image = self.images_left[self.index]
            if self.direction == 3:
                self.image = self.images_up[self.index]
            if self.direction == 4:
                self.image = self.images_down[self.index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)     

class Pokeball(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, speed):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = speed
        self.randomize()
        self.rect = self.image.get_rect()
        self.reset_pos()

    def reset_pos(self):
        throw_sound = pygame.mixer.Sound('assets/sounds/pokeballthrow.wav')
        throw_sound.set_volume(0.05)
        throw_sound.play()

        self.randomize()
        self.random_pos = random.randint(1, 4)
        if (self.random_pos == 1):
            self.rect.center = (random.randint(32, self.screen_width - 32), 0)
        if (self.random_pos == 2):
            self.rect.center = (self.screen_width, random.randint(32, self.screen_height - 32))
        if (self.random_pos == 3):
            self.rect.center = (random.randint(32, self.screen_width - 32), self.screen_height)
        if (self.random_pos == 4):
            self.rect.center = (0, random.randint(32, self.screen_height - 32))
    
    def move(self):
        global SCORE
        if (self.random_pos == 1):
            self.rect.move_ip(0,self.speed)
        if (self.random_pos == 2):
            self.rect.move_ip(-self.speed,0)
        if (self.random_pos == 3):
            self.rect.move_ip(0,-self.speed)
        if (self.random_pos == 4):
            self.rect.move_ip(self.speed,0)

        if (self.random_pos == 1 and self.rect.top > self.screen_height):
            self.reset_pos()
        if (self.random_pos == 2 and self.rect.right < 0):
            self.reset_pos()
        if (self.random_pos == 3 and self.rect.bottom < 0):
            self.reset_pos()
        if (self.random_pos == 4 and self.rect.left > self.screen_width):
            self.reset_pos()

    def randomize(self):
        pokeball_options = random.choice([
            "pokeball", "greatball", "ultraball", "quickball", "timerball", "loveball", "masterball", "netball", "premierball", "moonball"
        ])
        image = pygame.image.load(f"assets/objects/{pokeball_options}.png")
        self.image = pygame.transform.scale(image, (60, 60))
            
    def draw(self, surface):
        surface.blit(self.image, self.rect) 

async def title_screen(screen):
    font = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",30)
    # font = pygame.font.SysFont("Courier", 30)
    # font_small = pygame.font.SysFont("Courier", 30, bold=True)
    font_small = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",30)

    background = pygame.image.load("assets/environment/titlescreen.png")
    background = pygame.transform.scale(background, screen.get_size())

    screen_width, screen_height = screen.get_size()

    title = pygame.image.load("assets/environment/title.png")
    title = pygame.transform.scale_by(title, 0.6)


    start_btn = UIElement(
        center_position=(screen_width/2, 450),
        font_size=40,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Start",
        action=GameState.NEWGAME,
    )
    how_to_btn = UIElement(
        center_position=(screen_width/2, 550),
        font_size=40,
        bg_rgb=None,
        text_rgb=WHITE,
        text="How To Play",
        action=GameState.HOWTO,
    )
    quit_btn = UIElement(
        center_position=(screen_width/2, 650),
        font_size=40,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = [start_btn, how_to_btn, quit_btn]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
        screen.blit(background, (0, 0))
        title_rect = title.get_rect(center=(screen_width/2, 150))
        screen.blit(title, title_rect)

        hs_text = font_small.render(f"High Score: {HIGH_SCORE}", True, WHITE)
        hs_rect = hs_text.get_rect(center=(screen_width / 2, 300))
        screen.blit(hs_text, hs_rect)

        ls_text = font_small.render(f"Last Score: {LAST_SCORE}", True, WHITE)
        ls_rect = ls_text.get_rect(center=(screen_width / 2, 350))
        screen.blit(ls_text, ls_rect)

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()
        await asyncio.sleep(0)

async def how_to_screen(screen):
    font = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",30)
    # font = pygame.font.SysFont("Courier", 30, bold=True)
    font_small = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",25)
    # font_small = pygame.font.SysFont("Courier", 30, bold=False)

    background = pygame.image.load("assets/environment/titlescreen.png")
    background = pygame.transform.scale(background, screen.get_size())

    header = pygame.image.load("assets/environment/howtoplay.png")
    header = pygame.transform.scale_by(header, 0.5)

    screen_width, screen_height = screen.get_size()

    instructions = [
        "Welcome to Hungry Pikachu!",
        "The goal is to eat as many apricorns as you can.",
        "As you collect apricorns, ",
        "Pokéballs will be thrown at you.",
        "Avoid being caught.",
        "The longer you survive, the faster they come.",
        "Use the arrow keys to move.",
        "Have fun!"
    ]

    return_btn = UIElement(
        center_position=(screen_width / 2, 650),
        font_size=40,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Return to main menu",
        action=GameState.TITLE,
    )

    buttons = [return_btn]
    while True:
        screen.blit(background, (0, 0))
        header_rect = header.get_rect(center=(screen_width/2, 150))
        screen.blit(header, header_rect)
        for i, line in enumerate(instructions):
            rendered_line = font_small.render(line, True, WHITE)
            line_rect = rendered_line.get_rect(center=(screen_width / 2, 300 + i * 40))
            screen.blit(rendered_line, line_rect)
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()
        await asyncio.sleep(0)

async def run_game(WIN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, FPS):
    VELOCITY = 7
    SPEED = 7
    SCORE = 0
    
    font = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",30)
    # font = pygame.font.SysFont("Courier", 70)
    font_small = pygame.font.Font("assets/fonts/CourierPrime-Bold.ttf",40)
    # font_small = pygame.font.SysFont("Courier", 60, bold=True)
    game_over = font.render("You were caught!", True, BLACK)

    background = pygame.image.load("assets/environment/backgroundmap.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    P1 = Player(SCREEN_WIDTH, SCREEN_HEIGHT, VELOCITY)
    A1 = Apricorn(SCREEN_WIDTH, SCREEN_HEIGHT)
    B1 = Pokeball(SCREEN_WIDTH, SCREEN_HEIGHT, SPEED)

    pokeballs = pygame.sprite.Group(B1)
    apricorns = pygame.sprite.Group(A1)
    all_sprites = pygame.sprite.Group(P1, A1, B1)

    INC_SPEED = pygame.USEREVENT + 1
    pygame.time.set_timer(INC_SPEED, 1000)

    while True:
        WIN.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT
            elif event.type == INC_SPEED:
                SPEED += 0.5

        P1.update()

        collected = pygame.sprite.spritecollide(P1, apricorns, dokill=True)
        for apricorn in collected:
            eat_sound = pygame.mixer.Sound('assets/sounds/eating.wav')
            eat_sound.set_volume(0.2)
            eat_sound.play()
            SCORE += 1
            new_apricorn = Apricorn(SCREEN_WIDTH, SCREEN_HEIGHT)
            apricorns.add(new_apricorn)
            all_sprites.add(new_apricorn)

        P1.draw(WIN)
        for apricorn in apricorns:
            apricorn.draw(WIN)
        for pokeball in pokeballs:
            pokeball.draw(WIN)
            pokeball.speed = SPEED
            pokeball.move()

        scores = font_small.render(str(SCORE), True, BLACK)
        scores_rect = scores.get_rect(center=(30, 30))
        WIN.blit(scores, scores_rect)

        if pygame.sprite.spritecollideany(P1, pokeballs):
            catch_sound = pygame.mixer.Sound('assets/sounds/pokeballcatch.wav')
            catch_sound.set_volume(0.1)
            catch_sound.play()
            await asyncio.sleep(1)
            P1.image = pygame.transform.scale(
                pygame.image.load('assets/avatars/caughtpikachu.png'), (64, 64)
            )
            P1.draw(WIN)
            game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            WIN.blit(game_over, game_over_rect)
            global LAST_SCORE, HIGH_SCORE
            LAST_SCORE = SCORE
            if SCORE > HIGH_SCORE:
                HIGH_SCORE = SCORE

            pygame.display.update()
            await asyncio.sleep(3)
            return GameState.TITLE
        await asyncio.sleep(0)
        pygame.display.update()
        clock.tick(FPS)

async def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("assets/sounds/bgmusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
    WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    FPS = 60

    game_state = GameState.TITLE

    while True:

        if game_state == GameState.TITLE:
            game_state = await title_screen(WIN)
        elif game_state == GameState.NEWGAME:
            game_state = await run_game(WIN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, FPS)
        elif game_state == GameState.QUIT:
            pygame.quit()
            sys.exit()
        elif game_state == GameState.HOWTO:
            game_state = await how_to_screen(WIN)
        
        await asyncio.sleep(0)
        clock.tick(FPS)

asyncio.run(main())