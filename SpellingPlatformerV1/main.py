# Arush_Lal 21069 Spelling Platformer

# Importing essential libraries (pygame, random, string)
import pygame
import random
import string
from sys import exit

pygame.init()

WIDTH, HEIGHT = 1200, 900
tile_size = WIDTH / 12

# Specifying window dimensions & name 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spelling Platformer")
clock = pygame.time.Clock()

# Font info
title_font = pygame.font.Font("fonts/vhs_gothic.ttf", 54)
info_font = pygame.font.Font("fonts/Daydream.ttf", 20)
coins_font = pygame.font.Font("fonts/04B_30__.ttf", 40)
words_spelt_font = pygame.font.Font("fonts/Daydream.ttf", 26)
letter_font = pygame.font.Font("fonts/vhs_gothic.ttf", int(tile_size // 2))

# Loading images & converting them (making them more performant)
duck = pygame.image.load("images/duck.png").convert_alpha()
coin = pygame.image.load("images/coin.png").convert_alpha()
sky = pygame.image.load("images/sky.jpg").convert()
grass = pygame.image.load("images/grass.png").convert()
dirt = pygame.image.load("images/dirt.png").convert()
platform = pygame.image.load("images/platform.png").convert_alpha()
spikes = pygame.image.load("images/spikes.png").convert_alpha()

# Loading sound effects
jump_sfx = pygame.mixer.Sound("sounds/jump.mp3")
coin_sfx = pygame.mixer.Sound("sounds/coin-collected.wav")
letter_sfx = pygame.mixer.Sound("sounds/letter-collected.wav")
incorrect_sfx = pygame.mixer.Sound("sounds/incorrect.mp3")
bruh_sfx = pygame.mixer.Sound("sounds/dead.mp3")
word_spelt_sfx = pygame.mixer.Sound("sounds/word-spelled.mp3")

# Player surface and rect
player_surf = pygame.transform.scale(duck, (60, 90))
player_rect = player_surf.get_rect()

# Applying a transformation to scale each image appropriately
new_sky = pygame.transform.scale(sky, (WIDTH, HEIGHT))
new_grass = pygame.transform.scale(grass, (tile_size, tile_size))
new_dirt = pygame.transform.scale(dirt, (tile_size, tile_size))
new_platform = pygame.transform.scale(platform, (tile_size, platform.get_height() * (tile_size / platform.get_width())))
new_coin = pygame.transform.scale(coin, (tile_size / 2, tile_size / 2))
new_spikes = pygame.transform.scale(spikes, (tile_size, 68))

# Game map (This is editable)

game_map = [
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    ["0", "0", "0", "3", "0", "0", "0", "4", "0", "0", "0", "0"],
    ["2", "0", "0", "0", "0", "0", "2", "2", "2", "0", "0", "0"],
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "3"],
    ["2", "0", "3", "0", "0", "0", "2", "2", "0", "0", "0", "0"],
    ["0", "0", "0", "0", "0", "2", "0", "0", "0", "3", "0", "0"],
    ["2", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "2"],
    ["1", "2", "0", "0", "0", "0", "0", "2", "2", "2", "2", "1"],
    ["1", "1", "2", "0", "3", "0", "2", "1", "1", "1", "1", "1"],
]

# - All tiles - #
# 0 = Air
# 1 = Dirt
# 2 = Grass
# 3 = Platform
# 4 = Spikes
# 5 = Coin
# a-z = Letters

# GAME VARIABLES
FPS = 60
ground_level = HEIGHT - WIDTH / 10
word = None
correct_letter = None
character_num = 0
valid_positions = []
coin_counter = 0
words_spelt = 0

running = True

# JUMPING VARIABLES
jump_power = 20 # Editable
gravity = 1     # Editable
y_velocity = 0
air_timer = 0

# PLAYER VARIABLES
speed = 6 # Editable

default_location = [tile_size * 1.5, ground_level - tile_size] # Editable
player_location = [WIDTH, 0]

moving_right = False
moving_left = False
y_velocity = 0
direction = "right"

lines = open('common-words.txt').read().splitlines()

coin_rects = []
letter_rects = []
spikes_rects = []
spelling_dict = {}

def collision_test(rect, tiles):
    hit_list = []
    
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)

    return hit_list

def move(rect, movement, tiles):
    collision_types = {"top": False, "bottom": False, "right": False, "left": False}

    rect.x += movement[0]

    # x movement

    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]

    # y movement

    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True
    return rect, collision_types

def spawn_coin(x, y):
    if game_map[y][x] == "0":
        game_map[y][x] = "5"

def spawn_letter(letter, x, y):
    if game_map[y][x] == "0":
        game_map[y][x] = letter

def pick_word():
    global word
    global correct_letter
    global character_num

    word = random.choice(lines)
    print(word)

    spelling_dict.clear()

    for i in range(len(word)):
        spelling_dict[str(i)] = {"letter": word[i], "errors": 0, "collected": False}

    correct_letter = word[0]
    character_num = 0

    random.shuffle(valid_positions)

    for i in range(len(valid_positions)):
        if len(valid_positions) > 5:
            valid_positions.pop()

    for tuple in valid_positions:
        spawn_coin(tuple[1], tuple[0])

def despawn_letters():
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile.isalpha():
                game_map[y][x] = "0"
            x += 1
        y += 1

def spawn_letters():
    global valid_positions
        
    valid_positions.clear()

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == "1" or tile == "2" or tile == "3":
                if game_map[y - 1][x] == "0":
                    valid_positions.append((y - 1, x))

            x += 1
        y += 1

    valid_positions.remove((1, 0))
    valid_positions.remove((5, 0))

    standing_tuple = (round(player_rect.y / tile_size + 1) - 1, round(player_rect.x / tile_size))

    # remove tuple where player is standing
    if standing_tuple in valid_positions:
        valid_positions.remove(standing_tuple)

    tuple = random.choice(valid_positions)
    valid_positions.remove(tuple)

    spawn_letter(correct_letter, tuple[1], tuple[0])

    for i in range(random.randint(1, 2)):
        tuple = random.choice(valid_positions)
        valid_positions.remove(tuple)

        random_letter = random.choice(string.ascii_lowercase)

        if random_letter != correct_letter:
            spawn_letter(random_letter, tuple[1], tuple[0])

y = 0
for row in game_map:
    x = 0
    for tile in row:
        if tile == "1" or tile == "2" or tile == "3":
            if game_map[y - 1][x] == "0":
                valid_positions.append((y - 1, x))
        x += 1
    y += 1

valid_positions.remove((1, 0))
valid_positions.remove((5, 0))

pick_word()
spawn_letters()

while True: # Game loop
    # Background
    screen.blit(new_sky, (0, 0))

    # Rendering all tiles using a tile map
    tile_rects = []

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            normal_tile_pos = (x * tile_size, y * tile_size)
            middle_pos = (x * tile_size + tile_size / 2, y * tile_size + tile_size)

            if tile == "1":
                # Dirt
                screen.blit(new_dirt, normal_tile_pos)
            if tile == "2":
                # Grass
                screen.blit(new_grass, normal_tile_pos)
            if tile == "3":
                # Platform
                screen.blit(new_platform, normal_tile_pos)
            if tile == "4":
                # Spikes
                spikes_rect = new_spikes.get_rect(midbottom = middle_pos)

                if not spikes_rect in spikes_rects:
                    spikes_rects.append(spikes_rect)

                if spikes_rect.colliderect(player_rect):
                    bruh_sfx.play()
                    player_rect.midbottom = (default_location[0], default_location[1])

                screen.blit(new_spikes, spikes_rect)
            if tile == "5":
                # Coins
                coin_rect = new_coin.get_rect(midbottom = middle_pos)
                if not coin_rect in coin_rects:
                    coin_rects.append(coin_rect)

                if coin_rect.colliderect(player_rect):
                    coin_counter += 1
                    coin_sfx.play()
                    coin_rects.remove(coin_rect)
                    game_map[y][x] = "0"

                screen.blit(new_coin, coin_rect)
            if tile != "0":
                if tile == "3":
                    tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, platform.get_height() * (tile_size / platform.get_width())))
                elif tile.isalpha():
                    # Letters
                    letter_text = letter_font.render(tile, False, (68, 74, 84))
                    letter_rect = letter_text.get_rect(midbottom = middle_pos)

                    pygame.draw.rect(screen, "grey95", letter_rect, 0, 8)

                    if not letter_rect in letter_rects:
                        letter_rects.append(letter_rect)

                    if letter_rect.colliderect(player_rect):
                        letter_rects.remove(letter_rect)
                        game_map[y][x] = "0"
                        if tile == correct_letter:
                            letter_sfx.play()

                            if character_num == len(word) - 1:
                                word_spelt_sfx.play()
                                words_spelt += 1
                                pick_word()
                                spawn_letters()
                            else:
                                character_num += 1
                                spelling_dict[str(character_num - 1)]["collected"] = True
                                correct_letter = word[character_num]
                                despawn_letters()
                                spawn_letters()
                        else:
                            spelling_dict[str(character_num)]["errors"] += 1
                            incorrect_sfx.play()

                    screen.blit(letter_text, letter_rect)
                elif tile != "5" and tile != "4":
                    tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
            x += 1
        y += 1

    # Player movement & applying collision
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += speed
    if moving_left:
        player_movement[0] -= speed

    # Player gravity
    player_movement[1] += y_velocity
    y_velocity += gravity
    if y_velocity > 18:
        y_velocity = 18

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    # If player falls out of map, place them at a default location
    if player_rect.y > HEIGHT:
        player_rect.midbottom = (default_location[0], default_location[1])
        bruh_sfx.play()

    # When top and bottom collisions are detected, set y_velocity
    if collisions["bottom"]:
        y_velocity = 1
        air_timer = 0
    else:
        air_timer += 1

    if collisions["top"]:
        y_velocity = 0

    # Checking for inputs
    for event in pygame.event.get():
        # If user requests to close window, exit pygame & quit program
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                moving_right = True
                direction = "right"
            if event.key in (pygame.K_LEFT, pygame.K_a):
                moving_left = True
                direction = "left"
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                # Jumping
                if air_timer < 4:
                    y_velocity = -jump_power
                    jump_sfx.play()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                moving_right = False
            if event.key in (pygame.K_LEFT, pygame.K_a):
                moving_left = False

    # Rendering the character (left and right)
    if direction == "right":
        screen.blit(player_surf, player_rect)
    elif direction == "left":
        screen.blit(pygame.transform.flip(player_surf, True, False), player_rect)

    # Text and font information
    fps_str = "FPS: {fps:.2f}"

    coordinate_text = info_font.render(f"X: {str(player_rect.x // 1)} Y: {str(int(player_rect.y))}", False, "white")
    coordinate_rect = coordinate_text.get_rect()
    coordinate_rect.bottomleft = (0, HEIGHT)

    framerate_text = info_font.render(fps_str.format(fps = clock.get_fps()), False, "white")
    framerate_rect = framerate_text.get_rect()
    framerate_rect.bottomleft = (0, HEIGHT - coordinate_rect.height)

    coins_text = coins_font.render(f"COINS: {coin_counter}", False, "Yellow")
    words_text = words_spelt_font.render(f"WORDS SPELT: {words_spelt}", False, "White")
    words_rect = words_text.get_rect(center = (WIDTH / 2, 100))

    # Rendering the word to spell
    for i in range(len(word)):
        letter = spelling_dict[str(i)]["letter"]
        errors = spelling_dict[str(i)]["errors"]
        collected = spelling_dict[str(i)]["collected"]
        colour = None
        background = None

        if errors == 0:
            colour = "green"
        elif errors == 1:
            colour = "yellow"
        elif errors > 1:
            colour = "red"

        if not collected:
            colour = (68, 74, 84)

        letter_text = title_font.render(letter, False, colour)
        letter_rect = letter_text.get_rect(center = (i * 42 + WIDTH / 2 - (len(word) * 21 ), 50))
  
        if i == character_num:
            pygame.draw.rect(screen, "grey95", letter_rect, 0, 8)

        screen.blit(letter_text, letter_rect)

    # Rendering text (info & currency)
    screen.blit(coordinate_text, coordinate_rect)
    screen.blit(framerate_text, framerate_rect)
    screen.blit(coins_text, (0, 0))
    screen.blit(words_text, (0, 45))

    # Updating the display
    pygame.display.update()
    clock.tick(FPS)
