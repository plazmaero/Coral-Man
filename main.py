import pygame, random, sys
from pygame.locals import *
from timers import Timer
from map import *

RESOLUTION = WIDTH, HEIGHT = 350, 350
FPS = 30

sys.setrecursionlimit(2000)

print("Initializing Pygame...")

pygame.init()
pygame.mixer.init(44100, -16, 1, 2048)
pygame.mixer.Sound
screen = pygame.display.set_mode(RESOLUTION, flags = pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption('Coral Man')
clock = pygame.time.Clock()

land_sfx = pygame.mixer.Sound("Sounds/sfx/land.wav")
jump_sfx = pygame.mixer.Sound("Sounds/sfx/jump.wav")
fly_sfx = pygame.mixer.Sound("Sounds/sfx/fly.wav")
coin_sfx = pygame.mixer.Sound("Sounds/sfx/coin.wav")
bigcoin_sfx = pygame.mixer.Sound("Sounds/sfx/bigcoin.wav")
pickup_sfx = pygame.mixer.Sound("Sounds/sfx/pickup.wav")
fanblow_sfx = pygame.mixer.Sound("Sounds/sfx/fanblow.wav")
fanoff_sfx = pygame.mixer.Sound("Sounds/sfx/fanoff.wav")
hurt_sfx = pygame.mixer.Sound("Sounds/sfx/hurt.wav")
explosion_sfx = pygame.mixer.Sound("Sounds/sfx/explosion.wav")
door_sfx = pygame.mixer.Sound("Sounds/sfx/door.wav")
tumble_sfx = pygame.mixer.Sound("Sounds/sfx/tumble.wav")
blip_sfx = pygame.mixer.Sound("Sounds/sfx/blip.wav")
click_sfx = pygame.mixer.Sound("Sounds/sfx/click.wav")
select_sfx = pygame.mixer.Sound("Sounds/sfx/select.wav")

retrofont = pygame.font.Font('Fonts/retroville.ttf', 20)
retrofontmedium = pygame.font.Font('Fonts/retroville.ttf', 16)
retrofontsmall = pygame.font.Font('Fonts/retroville.ttf', 12)

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

logo = pygame.image.load("Assets/logo.png")

monsters = ["lumber", "wasper", "golden lumber"]
power_ups = ["fan/1", "rail/1", "shell/1"]

monsters_properties = {
  "lumber": {"hearts": 1, "speed": 2, "reward": 2},
  "wasper": {"hearts": 1, "speed": 3, "reward": 1},
  "golden lumber": {"hearts": 2, "speed": 1, "reward": 3},
}

collectibles = {
  "coin": {"message": "+ 1", "sound": coin_sfx, "colors": ["White"], "value": 1, "item": " "},
  "cm coin": {"message": "+ 3", "sound": bigcoin_sfx, "colors": ["White", "Blue"], "value": 3, "item": " "},
  "fan": {"message": "FAN", "sound": pickup_sfx, "colors": ["White", "Red"], "value": 0, "item": "fan"},
  "rail": {"message": "RAIL", "sound": pickup_sfx, "colors": ["Cyan", "Blue"], "value": 0, "item": "rail"},
  "shell": {"message": "SHELL", "sound": pickup_sfx, "colors": ["Green", "Lime"], "value": 0, "item": "shell"},
}

def maxint(int, max):
  if int > max: return max
  else: return int

game_over_controller_delay = Timer()

class Main:
  def __init__(self):
    print("Running Game...")
    self.reset()
  
  def reset(self):
    pygame.mixer_music.load("Sounds/tracks/Coral Bros.mp3")
    pygame.mixer_music.play(-1, 0.0)
    self.selected_item = 0
    self.items = ["Game A 1P - Jumbo Smash", "Game A 2P - Jumbo Smash", "Game B 1P - Coral Cruise", "Game B 2P - Coral Cruise"]
    self.started = False
    self.gamestate = 0
    self.score = 0
    self.round = 1
    self.tiles = []
    self.coins = []
    self.actors = []
    self.players = []
    self.timer = Timer()
    self.coin_regen_timer = Timer()
    self.item_regen_timer = Timer()
    self.winner_flash_text_timer = Timer()
    self.rounds_flash_text_timer = Timer()
    self.map = None
    #pygame.mixer_music.set_volume(0)
    self.players_alive = len(self.players)
    self.highest_point = 0
    self.furthest_player = 0
    self.switching = False
    self.scrollx = 0
    self.total_score = 0
    self.total_score_decoy = 0
    self.selected_map = 1

  def clear_game(self, second=False):
    self.selected_item = 0
    self.round = 1
    self.highest_point = 0
    self.furthest_player = 0
    self.switching = False
    self.scrollx = 0
    if self.gamestate == 1: self.load_map(f"level{self.selected_map}")
    elif self.gamestate == 3: self.load_map(f"cruise{self.selected_map}")
    self.players.append(Player(self))
    if second: self.players.append(Player(self, True))
    self.total_score = 0
    self.total_score_decoy = 0
    self.winner_flash_text_timer.reset()
    self.rounds_flash_text_timer.reset()
    self.selected_map = 1
  
  def update(self):
    if self.gamestate == 0: self.menu()
    if self.gamestate == 1: self.gameplay()
    if self.gamestate == 2: self.gameover()
    if self.gamestate == 3: self.gameplay()
    run()
  
  def menu(self):
    screen.blit(logo, ((WIDTH / 2) - (logo.get_width() / 2), 40))
    for index, game in enumerate(self.items):
      if index == self.selected_item:
        text = retrofontmedium.render(game, True, 'Blue')
        screen.blit(text, (((WIDTH / 2) - (text.get_width() / 2)), 200 + (index * 25)))
        if "1P" in game: screen.blit(pygame.image.load(f"Assets/coral man/walk{self.rounds_flash_text_timer.keep_count(3, 5, 1)}.png").convert_alpha(), (((WIDTH / 2) - (text.get_width() / 2)) - 32, 196 + (index * 25)))
        else: screen.blit(pygame.image.load(f"Assets/coral man junior/walk{self.rounds_flash_text_timer.keep_count(2, 5, 1)}.png").convert_alpha(), (((WIDTH / 2) - (text.get_width() / 2)) - 32, 196 + (index * 25)))
      else:
        text = retrofontmedium.render(game, True, 'White')
        screen.blit(text, ((WIDTH / 2) - (text.get_width() / 2), 200 + (index * 25)))
    screen.blit(retrofontsmall.render('TunaGames, No rights reserved!', True, 'White'), (3, HEIGHT-15))
    screen.blit(retrofontsmall.render(f'Press SELECT to switch the map: Map {self.selected_map}', True, 'White'), (3, HEIGHT-30))
    if k_select: self.selected_map += 1
    if self.selected_map >= 5: self.selected_map = 1
    self.controls()

    screen.blit(retrofontsmall.render('Player 1 plays with WASD or arrow keys,\nPlayer 2 plays with IJKL\nSelect = I key', False, 'White'), (0, -5))
  
  def controls(self):
    global remember_gs

    if k_up: self.selected_item -= 1; click_sfx.play()
    if k_down: self.selected_item += 1; click_sfx.play()
    if self.selected_item >= len(self.items): self.selected_item = 0
    if self.selected_item == -1: self.selected_item = len(self.items) - 1

    if self.gamestate == 0:
      if (k_use or k_start) and self.selected_item == 0: self.gamestate = 1; self.clear_game(); remember_gs = (self.gamestate, False); select_sfx.play()
      if (k_use or k_start) and self.selected_item == 1: self.gamestate = 1; self.clear_game(True); remember_gs = (self.gamestate, True); select_sfx.play()
      if (k_use or k_start) and self.selected_item == 2: self.gamestate = 3; self.clear_game(); remember_gs = (self.gamestate, False); select_sfx.play()
      if (k_use or k_start) and self.selected_item == 3: self.gamestate = 3; self.clear_game(True); remember_gs = (self.gamestate, True); select_sfx.play()
    
    elif self.gamestate == 2:
      if (k_use or k_start) and self.selected_item == 0: self.reset(); self.gamestate = remember_gs[0]; self.clear_game(remember_gs[1]); select_sfx.play()
      if (k_use or k_start) and self.selected_item == 1: self.gamestate = 0; self.clear_game(); self.reset(); self.selected_item = 0
  
  def gameplay(self):
    try: second_player_score = self.players[1].score
    except: second_player_score = 0
    self.highest_point = 0
    for player in self.players:
      if self.highest_point < player.score: self.highest_point = player.score
    for tile in self.tiles: tile.update()
    self.furthest_player = 0
    for player in self.players:
      if self.furthest_player < player.rect.x: self.furthest_player = player.rect.x
    for tile in self.tiles: tile.update()

    if not pygame.mixer_music.get_busy():
      if not self.switching: pygame.mixer_music.load("Sounds/tracks/Strivers.mp3"); pygame.mixer_music.play(-1, 0.0)
      else:
        for player in self.players:
          if self.gamestate == 1 and player.score == self.highest_point: player.wins += 1
          if self.gamestate == 3 and player.rect.x == self.furthest_player: player.wins += 1
        self.switching = False; self.highest_point = 0; self.furthest_player = 0; self.scrollx = 0; self.winner_flash_text_timer.reset(); self.rounds_flash_text_timer.reset()
        self.load_map(maps[self.map]["next_map"]); self.round += 1
        for player in self.players: player.__init__(self, player.second, player.wins, player.deaths)
        if self.round >= 6: self.gamestate = 2

    #for tile in self.footholds:
    #  pygame.draw.rect(screen, "Green", ((tile.rect.x, tile.rect.y - main.scrolly), (tile.rect.width, tile.rect.height)), 1)

    if self.highest_point >= 50 and not self.switching: self.switching = True; pygame.mixer_music.load("Sounds/tracks/Complete.mp3"); pygame.mixer_music.play(1, 0.0); self.total_score += self.players[0].score + second_player_score

    if self.gamestate == 1 and len(self.actors) < 9 and self.timer.timer(FPS * (2 - maxint((self.highest_point / 50), 1.75))) and self.rounds_flash_text_timer.tally >= (FPS / 1.75) - 1 and not self.switching: self.actors.append(Monster(monsters[random.randrange(0, maxint(round(self.highest_point / 25), len(monsters) - 1) + 1)], self))
    if self.gamestate == 3 and len(self.actors) < 9 and self.timer.timer(random.randrange(round(FPS * 1.5), round(FPS * 2.75))) and self.rounds_flash_text_timer.tally >= (FPS / 1.75) - 1 and not self.switching: self.actors.append(Monster(monsters[random.randrange(0, maxint(round(self.highest_point / 5), len(monsters) - 1) + 1)], self))

    for actor in self.actors:
      actor.update()
      if actor.delete: self.actors.remove(actor)

    for coin in self.coins:
      coin.update()
      for tile in self.tiles:
        if coin.rect.colliderect(tile.rect): coin.on_ground = True
      if not coin.on_ground and coin.coin: coin.rect.y += 5
      if coin.despawn_timer.time >= FPS * 20: self.coins.remove(coin)

    self.players_alive = len(self.players)

    for index, player in enumerate(self.players):
      player.update()
      if not (self.switching and self.winner_flash_text_timer.wait(FPS) and ((self.highest_point == player.score and self.gamestate == 1) or (self.furthest_player == player.rect.x and self.gamestate == 3))): screen.blit(retrofontmedium.render(f"P{index + 1}: {player.score}", False, "White"), (2, 2 + (index * 20)))
      if player.dead_animation_timer.tally == len(player.dead_animation) - 1: self.players_alive -= 1
      for wins in range(player.wins): screen.blit(pygame.image.load("Assets/crown.png").convert_alpha(), (75 + (wins * 20), 4 + (index * 20)))
    if round(self.rounds_flash_text_timer.tally * 1.75) % 2 == 0: screen.blit(retrofontmedium.render(f"Round {self.round} / 5", False, "White"), (220, 2))
    self.rounds_flash_text_timer.count(1, FPS / 1.75, 0)

    if self.switching:
      if self.total_score_decoy < self.total_score - 25 and pygame.mixer_music.get_pos() > 1000: self.total_score_decoy += 9
      if self.total_score_decoy < self.total_score and pygame.mixer_music.get_pos() > 1000: self.total_score_decoy += 1; blip_sfx.play()
      screen.blit(retrofontmedium.render(f"TOTAL SCORE: {self.total_score_decoy}", False, "White"), (90, 50))

    if self.gamestate == 1 and self.coin_regen_timer.timer(FPS * 2) and not self.switching: self.coins.append(Tile(["coin/1", "coin/1", "coin/1", "coin/1", "coin/1", "cm coin/1"][random.randrange(0, 6)], False, random.randrange(0, 26), random.randrange(0, 5), False, self))
    if self.gamestate == 1 and self.item_regen_timer.timer(FPS * 10) and not self.switching: self.coins.append(Tile(power_ups[random.randrange(0, len(power_ups))], False, random.randrange(0, 26), random.randrange(0, 5), False, self))
    if self.gamestate == 3 and self.coin_regen_timer.timer(FPS / 1.5) and not self.switching: self.coins.append(Tile(["coin/1", "coin/1", "coin/1", "coin/1", "cm coin/1"][random.randrange(0, 5)], False, 30 + self.scrollx, 0, False, self))
    if self.gamestate == 3 and self.item_regen_timer.timer(FPS * 2) and not self.switching: self.coins.append(Tile(power_ups[random.randrange(0, len(power_ups))], False, 30 + self.scrollx, 0, False, self))

    if self.gamestate == 3 and not self.switching and self.scrollx <= (len(maps[self.map]["layout"][0]) * 12.5) - WIDTH: self.scrollx += 1.5
    if self.gamestate == 3 and self.furthest_player >= (len(maps[self.map]["layout"][0]) * 12.5) - WIDTH / 6 and not self.switching: self.switching = True; pygame.mixer_music.load("Sounds/tracks/Complete.mp3"); pygame.mixer_music.play(1, 0.0); self.total_score += self.players[0].score + second_player_score

    if not self.players_alive: self.gamestate = 2

  def gameover(self):
    self.items = ["Retry Game", "Return to Menu"]
    if self.round <= 5: text = retrofont.render("Game Over!", True, 'White')
    else: text = retrofont.render("Game End!", True, 'White')
    screen.blit(text, (((WIDTH / 2) - (text.get_width() / 2)), 50))
    for index, game in enumerate(self.items):
      if index == self.selected_item:
        text = retrofontmedium.render(game, True, 'Blue')
        screen.blit(text, (((WIDTH / 2) - (text.get_width() / 2)), 150 + (index * 35)))
      else:
        text = retrofontmedium.render(game, True, 'White')
        screen.blit(text, ((WIDTH / 2) - (text.get_width() / 2), 150 + (index * 35)))

    if len(self.players) == 1: screen.blit(retrofontmedium.render(f"   At Round {self.round}\nYour Score: {self.players[0].score}", False, "White"), (105, 85))
    else:
      screen.blit(retrofontmedium.render(f"   At Round {self.round}", False, "White"), (105, 85))
      for index, player in enumerate(self.players):
        screen.blit(retrofont.render(f"Player {index + 1}", False, "White"), (40 + (index * 140), 225))
        screen.blit(retrofontmedium.render(f"SCORE {player.score}\nWINS {player.wins}\nDEATHS {player.deaths}", False, "White"), (45 + (index * 140), 250))
    
    self.controls()

  def load_map(self, map, play_music=True):
    self.tiles.clear()
    self.coins.clear()
    self.actors.clear()
    self.scrollx = 0
    for y, mapx in enumerate(maps[map]["layout"]):
      for x, tile in enumerate(mapx):
        if tile != " ":
          try: floor = map[y - 1][x] == " " and map[y - 2][x] == " "
          except: floor = False
          self.tiles.append(Tile(tiles[tile]["name"], tiles[tile]["solid"], x, y, floor, self))
          if x == len(mapx) - 1 and mapx[0] != " ": self.tiles.append(Tile(tiles[tile]["name"], tiles[tile]["solid"], x + 1, y, floor, self))
          if x == 0: self.tiles.append(Tile(tiles[tile]["name"], tiles[tile]["solid"], x - 1, y, floor, self))

    self.footholds = [tile for tile in self.tiles if tile.floor]
    #if spawn_door: self.tiles.append(Tile(tiles["1"]["name"], tiles[tile]["solid"], (foothold.rect.x / foothold.size), (foothold.rect.y / foothold.size) - foothold.size, False, left_ledge, right_ledge, self))
    self.map = maps[map]["string_form"]
    self.switching = False
    self.highest_point = 0

    if self.gamestate == 1: pygame.mixer_music.load("Sounds/tracks/Game Start.mp3")
    if self.gamestate == 3: pygame.mixer_music.load("Sounds/tracks/The Cruise.mp3")
    if play_music: pygame.mixer_music.play(1, 0.0)
    else: pygame.mixer_music.stop()

  def spawn_entities(self, list=None):
    if list == None:
      for tile in self.tiles:
        if tile.floor and not tile.left_ledge and not tile.right_ledge and not random.randrange(-2, 3) and tile.rect.y > 250 and tile.rect.y < 1800:
          self.actors.append(Monster(tile.rect.x, tile.rect.y, monsters[random.randrange(0, len(monsters))], self))
    else: self.actors = list

class Player:
  def __init__(self, main, second=False, wins=0, deaths=0):
    self.main = main
    self.second = second
    self.character = "coral man"
    if second: self.character = "coral man junior"
    self.rect = pygame.Rect(((256 - (int(second) * (184 - (int(main.gamestate == 3) * 120))) - (int(main.gamestate == 3 and main.map == "cruise4") * 35)), 96), (12, 30))
    self.movement = [0, 0]
    self.speed = 2
    self.timer = Timer()
    self.flipped = False
    self.state = "idle"
    self.frame = 1
    self.deceive_x = 0
    self.y_vel = 0
    self.terminal_velocity = 10
    self.jumping_vel = 0
    self.airtimer = 0
    self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
    self.enemy_collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
    self.image = pygame.image.load(f"Assets/{self.character}/{self.state}{self.frame}.png").convert_alpha()
    self.protection = Timer()
    self.hit = False
    
    self.score = 0
    self.item = " "
    self.lives = 3
    self.numbers = []
    self.dead_animation = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, -10, -15, -20, -23, -20, -13, -7, -2, 2, 8, 15, 19, 28, 40, 55, 70, 90, 110, 125, 150, 175, 200, 230, 260, 300, 350, 400]
    self.alive = True
    self.splashed = False
    self.dead_animation_timer = Timer()
    self.item_timer = Timer()
    self.item_animate_timer = Timer()
    self.wins = wins
    self.deaths = deaths

  def update(self):
    #pygame.draw.rect(screen, "Red", ((self.rect.x - main.scrollx, self.rect.y), (self.rect.width, self.rect.height)), 2)
    try: self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load(f"Assets/{self.character}/{self.state}{self.frame}.png").convert_alpha(), self.flipped, False), (30, 30))
    except: self.frame = 1
    screen.blit(self.image, (self.deceive_x - 6, self.rect.y + self.dead_animation[self.dead_animation_timer.tally]))
    
    if self.alive:
      if not main.switching:
        if self.rect.x < main.scrollx - 46 or self.rect.x > main.scrollx + WIDTH + 10: self.alive = False
        if self.rect.y > HEIGHT + 5: self.alive = False
        if main.gamestate != 3:
          if self.rect.x > WIDTH - 6: self.rect.x = -6
          if self.rect.x < -6: self.rect.x = WIDTH - 6
        self.deceive_x = round(self.rect.x - main.scrollx)
        self.rect, self.enemy_collision = self.get_hit(self.rect, self.movement, main.actors)
        if self.item != "fan": self.rect, self.collision = self.move(self.rect, self.movement, [tile for tile in main.tiles if not tile.coin])
        self.pickup(self.rect, [tile for tile in main.tiles + main.coins if tile.coin])
        self.frame = self.timer.keep_count(FPS / 8, 3, 1)
        self.controls()
        if self.item == "fan":
          screen.blit(pygame.transform.scale(pygame.image.load(f"Assets/tiles/fan/{self.item_animate_timer.keep_count(2, 3, 1)}.png").convert_alpha(), (16, 16)), (self.deceive_x, self.rect.y))
          self.rect.x += self.movement[0]
          if self.item_animate_timer.tally == 1: fanblow_sfx.play()
          if self.rect.y > 20: self.rect.y -= 1
          else: self.item = " "; fanoff_sfx.play()
        if self.item == "rail":
          self.state = "slide"; self.frame = self.timer.keep_count(2, 3, 1)
          if not self.flipped: self.movement[0] = 5
          if self.flipped: self.movement[0] = -5
        if self.item != " " and self.item_timer.timer(FPS * 15): self.item = " "
        if self.item == "shell": pygame.draw.rect(screen, "Cyan", ((self.deceive_x - 8, self.rect.y), (32, 32)), 1 + int(self.item_animate_timer.tally % 2 == 0), 16); self.hit = False; self.alive = True
    else:
      self.dead_animation_timer.count(1, len(self.dead_animation) - 1, 0)
      if self.state != "defeat": tumble_sfx.play(); self.deaths += 1
      self.state, self.frame = "defeat", 1
      if self.rect.y + self.dead_animation[self.dead_animation_timer.tally] >= HEIGHT and not self.splashed: self.splashed = True; main.coins.append(Tile("splash/1", False, ((self.deceive_x + main.scrollx) - 6) / 12.5, 0, False, main))

    #if self.dead_animation_timer.tally == 25: fly_sfx.play()
    if self.dead_animation_timer.tally == len(self.dead_animation) - 1: self.delete = True
    
    self.y_vel += 2
    if self.y_vel > 10: self.y_vel = 10
    self.movement[1] = self.y_vel
    if self.collision["bottom"]: self.y_vel, self.airtimer = 0, 0
    elif self.collision['top']: self.y_vel, self.airtimer = 0, 10
    else: self.airtimer += 1

    for number in self.numbers:
      if number.alive: number.update()
      else: self.numbers.remove(number)

  def controls(self):
    if not self.second:
      if k_right:
        if self.item != "rail": self.movement[0] = self.speed; self.state = "walk"; self.frame = self.timer.keep_count(3, 5, 1)
        self.flipped = False
      elif k_left:
        if self.item != "rail": self.movement[0] = -self.speed; self.state = "walk"; self.frame = self.timer.keep_count(3, 5, 1)
        self.flipped = True
      elif self.item != "rail": self.state = "idle"; self.movement[0] = 0; self.timer.reset(); self.frame = 1
      if k_up:
        if self.y_vel == 0 and self.collision['bottom'] and self.item != "fan": jump_sfx.play()
        self.state = "jump"; self.timer.reset(); self.frame = 1; self.jumping_vel = -10
        if self.airtimer < 10: self.y_vel = self.jumping_vel
    else:
      if k_right2:
        if self.item != "rail": self.movement[0] = self.speed; self.state = "walk"; self.frame = self.timer.keep_count(3, 5, 1)
        self.flipped = False
      elif k_left2:
        if self.item != "rail": self.movement[0] = -self.speed; self.state = "walk"; self.frame = self.timer.keep_count(3, 5, 1)
        self.flipped = True
      elif self.item != "rail": self.state = "idle"; self.movement[0] = 0; self.timer.reset(); self.frame = 1
      if k_up2:
        if self.y_vel == 0 and self.collision['bottom'] and self.item != "fan": jump_sfx.play()
        self.state = "jump"; self.timer.reset(); self.frame = 1; self.jumping_vel = -10
        if self.airtimer < 10: self.y_vel = self.jumping_vel

  def move(self, rect, movement, tiles):
    collision_type = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]

    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
      if tile.solid:
        if movement[0] > 0:
          rect.right = tile.rect.left
          collision_type['right'] = True
        elif movement[0] < 0:
          rect.left = tile.rect.right
          collision_type['left'] = True
      
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
      if tile.solid:
        if movement[1] > 0:
          if self.y_vel != 0: land_sfx.play()
          rect.bottom = tile.rect.top
          collision_type['bottom'] = True
        elif movement[1] < 0:
          rect.top = tile.rect.bottom
          collision_type['top'] = True
    return rect, collision_type
  
  def pickup(self, rect, tiles):
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
      self.frame = 1
      self.item_animate_timer.reset()
      try: main.coins.remove(tile)
      except: main.tiles.remove(tile)
      collectibles[tile.type]["sound"].play()
      self.numbers.append(Number(collectibles[tile.type]["message"], self.rect.x, self.rect.y, collectibles[tile.type]["colors"]))
      self.score += collectibles[tile.type]["value"]
      if collectibles[tile.type]["item"] != " ": self.item = collectibles[tile.type]["item"]; self.item_timer.reset()
      
  def get_hit(self, rect, movement, dangers):
    collision_type = {'top': False, 'bottom': False, 'right': False, 'left': False}

    hit_list = [enemy for enemy in collision_test(rect, dangers) if enemy.alive]

    for enemy in hit_list:
      if self.item == "fan":
        enemy.alive = False
        self.score += 1
        self.numbers.append(Number(f"That's a HIT!", self.rect.x, self.rect.y, colors=["Red", "Orange", "Yellow", "Green", "Cyan", "Blue"]))
      if not self.hit:
        if self.item != "rail" and self.item != "shell":
          if movement[0] > 0:
            collision_type['right'] = True
            enemy.direction = "right"
            hurt_sfx.play()
            self.lives -= 1
            self.hit = True
          elif movement[0] < 0:
            collision_type['left'] = True
            enemy.direction = "left"
            hurt_sfx.play()
            self.lives -= 1
            self.hit = True
        if self.item == "shell":
          self.item_animate_timer.count(1, FPS / 3, 0)
          if self.rect.x < enemy.rect.x and self.item_animate_timer.tally >= (FPS / 3) - 1: collision_type['right'] = True; enemy.direction = "right"; hurt_sfx.play(); self.item_animate_timer.reset()
          elif self.rect.x > enemy.rect.x and self.item_animate_timer.tally >= (FPS / 3) - 1: collision_type['left'] = True; enemy.direction = "left"; hurt_sfx.play(); self.item_animate_timer.reset()
      else:
        if self.protection.tally == FPS * 2: self.hit == False
        self.protection.count(1, FPS * 2, 0)

    hit_list = [enemy for enemy in collision_test(rect, dangers) if enemy.alive]
    
    for enemy in hit_list:
      if movement[1] > 0 and not collision_type["left"] and not collision_type["right"] and rect.bottom >= enemy.rect.top:
        if self.rect.y < enemy.rect.y:
          if self.y_vel != 0: land_sfx.play()
          rect.bottom = enemy.rect.top
          collision_type['bottom'] = True
          if self.movement[1] > 0: self.state = "jump"; self.timer.reset(); self.frame = 1; self.y_vel = -15
          enemy.lives -= 1
          if enemy.lives == 0: self.score += enemy.reward; self.numbers.append(Number(f"{enemy.reward} +", self.rect.x, self.rect.y))
        else:
          if self.item != "fan" and self.item != "rail": self.alive = False
      elif movement[1] < 0:
        #rect.top = enemy.rect.bottom
        collision_type['top'] = True
    return rect, collision_type
    

class Tile:
  def __init__(self, tile, solid, x, y, floor, main):
    self.size = 12.5
    self.main = main
    def load_img(tile): return pygame.transform.scale(pygame.image.load("Assets/tiles/" + tile + ".png").convert_alpha(), (self.size, self.size))
    self.type = tile
    self.solid = solid
    self.floor = floor
    self.image = load_img(tile)
    self.rect = pygame.Rect(x * self.size, y * self.size, self.size, self.size)
    self.coin = False
    self.timer = Timer()
    if self.type == "grass": self.rect = pygame.Rect(x * self.size, y * self.size, self.size, self.size / 2)
    if self.type == "water/1": self.type = "water"
    if self.type == "coin/1": self.coin = True; self.type = "coin"
    if self.type == "cm coin/1": self.coin = True; self.type = "cm coin"
    if self.type == "fan/1": self.coin = True; self.type = "fan"
    if self.type == "rail/1": self.coin = True; self.type = "rail"
    if self.type == "shell/1": self.coin = True; self.type = "shell"
    if self.type == "splash/1": self.type = "splash"; self.rect.y = HEIGHT - 32; self.coin = False
    self.on_ground = False
    self.despawn_timer = Timer()

  def update(self):
    #self.rect.x += main.scrolls[0]; self.rect.y += main.scrolls[1]
    screen.blit(self.image, (self.rect.x - main.scrollx, self.rect.y - (int(self.coin) * 7.5)))
    #if self.floor: pygame.draw.rect(screen, "Green", ((self.rect.x, self.rect.y - main.scrolly), (self.rect.width, self.rect.height)), 1)

    if self.type == "coin": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/coin/{self.timer.keep_count(3, 4, 1)}.png").convert_alpha(), (self.size, self.size)); self.despawn_timer.timer(FPS * 60)
    if self.type == "cm coin": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/cm coin/{self.timer.oscillate(3, 4, 2)}.png").convert_alpha(), (self.size, self.size)); self.despawn_timer.timer(FPS * 60)
    if self.type == "fan": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/fan/{self.timer.keep_count(3, 3, 1)}.png").convert_alpha(), (20, 20)); self.despawn_timer.timer(FPS * 60)
    if self.type == "rail": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/rail/1.png").convert_alpha(), (25, 25)); self.despawn_timer.timer(FPS * 60)
    if self.type == "shell": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/shell/1.png").convert_alpha(), (18, 18)); self.despawn_timer.timer(FPS * 60)
    if self.type == "splash": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/splash/{self.timer.count(2, 6, 1)}.png").convert_alpha(), (32, 32))
    if self.timer.tally >= 6 and self.type == "splash": main.coins.remove(self)
    if self.type == "water": self.image = pygame.transform.scale(pygame.image.load(f"Assets/tiles/water/{self.timer.keep_count(FPS / 1.75, 3, 1)}.png").convert_alpha(), (self.size, self.size))


class Monster:
  def __init__(self, type, main):
    self.main = main
    if main.gamestate != 3: self.rect = pygame.Rect((1 * (random.randrange(0, 2) * 350, 128)), (18, 32 - (int(type == "wasper") * 20)))
    else: self.rect = pygame.Rect((WIDTH + (main.scrollx - 2), -16), (18, 32 - (int(type == "wasper") * 20)))
    if type == "wasper": self.rect.y = random.randrange(25, HEIGHT - 50)
    if main.gamestate == 3 and main.map == "cruise4":
      if type == "wasper": self.rect.y = random.randrange(200, HEIGHT - 100)
      else:self.rect = pygame.Rect((WIDTH + (main.scrollx - 2), 200), (18, 32 - (int(type == "wasper") * 20)))
    self.movement = [0, 0]
    self.speed = monsters_properties[type]["speed"]
    self.lives = monsters_properties[type]["hearts"]
    self.timer = Timer()
    self.flipped = False
    self.state = "idle"
    self.frame = 1
    self.y_vel = 0
    self.jumping_vel = 0
    self.airtimer = 0
    self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
    self.type = type
    if self.rect.x < WIDTH / 2: self.direction = "right"
    if self.rect.x > WIDTH / 2: self.direction = "left"
    self.image = pygame.image.load(f"Assets/{self.type}/{self.state}{self.frame}.png").convert_alpha()
    self.alive = True
    self.dead_animation_timer = Timer()
    self.dead_animation = [0, -5, -10, -15, -20, -23, -20, -13, -7, -2, 2, 8, 15, 19, 28, 40, 55, 70, 90, 110, 125, 150, 175, 200, 230, 260, 300, 350, 400]
    self.delete = False
    self.splashed = False
    self.reward = monsters_properties[type]["reward"]

    hit_list = collision_test(self.rect, main.tiles)
    if hit_list != []: self.delete = True

  def update(self):
    self.image = pygame.transform.flip(pygame.image.load(f"Assets/{self.type}/{self.state}{self.frame}.png").convert_alpha(), self.flipped, False)
    #pygame.draw.rect(screen, "Red", ((self.rect.x - main.scrollx, self.rect.y), (self.rect.width, self.rect.height)), 2)
    screen.blit(self.image, ((self.rect.x - 8) - main.scrollx, self.rect.y + self.dead_animation[self.dead_animation_timer.tally]))

    if self.alive:
      if not main.switching:
        self.rect, self.collision = self.move(self.rect, self.movement, [tile for tile in main.tiles if tile.solid])
        if self.direction == "left": self.movement[0] = -self.speed; self.flipped = True
        if self.direction == "right": self.movement[0] = self.speed; self.flipped = False
        if self.collision['right']: self.direction = "left"
        if self.collision["left"]: self.direction = "right"
        self.frame = self.timer.keep_count(FPS / 8, 3, 1)
    else:
      self.dead_animation_timer.count(1, len(self.dead_animation) - 1, 0)
      if self.rect.y + self.dead_animation[self.dead_animation_timer.tally] >= HEIGHT and not self.splashed: self.splashed = True; main.coins.append(Tile("splash/1", False, (((self.rect.x - main.scrollx) + main.scrollx) - 6) / 12.5, 0, False, main))

    if self.dead_animation_timer.tally == 6: fly_sfx.play()
    if self.dead_animation_timer.tally == len(self.dead_animation) - 1: self.delete = True
    if self.lives <= 0: self.alive = False

    if main.gamestate != 3: 
      if self.rect.x > WIDTH + (self.rect.width * 2): self.delete = True
      if self.rect.x < -(self.rect.width * 2): self.delete = True
    else:
      if self.rect.x > WIDTH + main.scrollx: self.delete = True
      if self.rect.x < main.scrollx - 32: self.delete = True

    if self.type != "wasper":
      self.y_vel += 2
      if self.y_vel > 10 - int(main.gamestate == 3): self.y_vel = 10 - int(main.gamestate)
      self.movement[1] = self.y_vel
      if self.collision["bottom"]: self.y_vel, self.airtimer = 0, 0
      elif self.collision['top']: self.y_vel, self.airtimer = 0, 10
      else: self.airtimer += 1


  def move(self, rect, movement, tiles):
    collision_type = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]

    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
      if movement[0] > 0: rect.right = tile.rect.left; collision_type['right'] = True
      elif movement[0] < 0: rect.left = tile.rect.right; collision_type['left'] = True
      
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
      if movement[1] > 0:
        rect.bottom = tile.rect.top
        collision_type['bottom'] = True

        #if tile.left_ledge and random.randrange(-1, 1): self.direction = "right"
        #if tile.right_ledge and random.randrange(-1, 1): self.direction = "left"

      elif movement[1] < 0: rect.top = tile.rect.bottom; collision_type['top'] = True

    hit_list = collision_test(rect, [player for player in main.players])

    #for tile in hit_list:
    #  if movement[0] > 0: rect.right = main.player.rect.left; collision_type['right'] = True
    #  elif movement[0] < 0: rect.left = main.player.rect.right; collision_type['left'] = True

    return rect, collision_type
  

class Number:
  def __init__(self, text, x, y, colors=["White"]):
    self.text = text
    self.x = x
    self.y = y
    self.timer = Timer()
    self.flash_timer = Timer()
    self.alive = True
    self.colors = colors

  def update(self):
    screen.blit(retrofontsmall.render(f"{self.text}", True, self.colors[self.flash_timer.keep_count(2, len(self.colors), 0)]), (self.x - main.scrollx, self.y))
    if self.timer.timer(FPS * 2): self.alive = False


def collision_test(rect, tiles):
  hit_list = []
  for tile in tiles:
    if rect.colliderect(tile):
      hit_list.append(tile)
      
  return hit_list


k_right, k_left, k_down, k_up, k_use, k_start, k_select, k_right2, k_left2, k_up2 = False, False, False, False, False, False, False, False, False, False

def run():
  global k_down, k_up, k_right, k_left, k_use, k_start, k_select, k_right2, k_left2, k_up2
  k_use, k_start, k_select = False, False, False
  if main.gamestate != 1 and main.gamestate != 3: k_left, k_right, k_up, k_down = False, False, False, False
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      exit()
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN: k_start = True
      if event.key == pygame.K_SPACE or event.key == pygame.K_e: k_use = True
      if event.key == pygame.K_RIGHT or event.key == pygame.K_d: k_right = True
      if event.key == pygame.K_LEFT or event.key == pygame.K_a: k_left = True
      if event.key == pygame.K_UP or event.key == pygame.K_w: k_up = True
      if event.key == pygame.K_DOWN or event.key == pygame.K_s: k_down = True
      if event.key == pygame.K_i: k_select = True
      if event.key == pygame.K_ESCAPE:
        if main.gamestate == 0:
          pygame.quit()
          exit()
        elif main.gamestate > 0: main.gamestate = 0; main.reset()
      if event.key == pygame.K_l: k_right2 = True
      if event.key == pygame.K_j: k_left2 = True
      if event.key == pygame.K_i: k_up2 = True
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_RETURN: k_start = False
      if event.key == pygame.K_SPACE or event.key == pygame.K_e: k_use = False
      if event.key == pygame.K_RIGHT or event.key == pygame.K_d: k_right = False
      if event.key == pygame.K_LEFT or event.key == pygame.K_a: k_left = False
      if event.key == pygame.K_UP or event.key == pygame.K_w: k_up = False
      if event.key == pygame.K_DOWN or event.key == pygame.K_s: k_down = False
      if event.key == pygame.K_l: k_right2 = False
      if event.key == pygame.K_j: k_left2 = False
      if event.key == pygame.K_i: k_up2 = False
      
    if event.type == JOYBUTTONDOWN:
      if event.button == 0:
        if main.gamestate == 0: k_use = True
        else: k_up = True #x A
      if event.button == 1:
        if main.gamestate > 0: main.gamestate = 0; main.reset() #menu
      if event.button == 2: k_use = True #□ X
      if event.button == 3: k_select = True #△ Y
      if event.button == 4: pygame.image.save(screen, "screenshot.png"); #share
      if event.button == 5: pass #PS
      if event.button == 6:
        if main.gamestate == 0: k_select = True
        elif main.gamestate > 0: main.gamestate = 0; main.reset() #menu
      if event.button == 7:
        if main.gamestate == 0: k_start = True #L3
      if event.button == 8: pass #R3
      if event.button == 9: pass #L1 LB
      if event.button == 10: pass #R1 RB
      if event.button == 11: k_up = True #up
      if event.button == 12: k_down = True #down
      if event.button == 13: k_left = True #left
      if event.button == 14: k_right = True #right
      if event.button == 15: pygame.image.save(screen, "screenshot.png"); #pad
    if event.type == JOYAXISMOTION:
      if abs(event.value) > 0.1:
        k_up, k_down = False, False
        if event.axis == 0:
          if event.value < -0.5: k_left = True #go left
          else: k_left = False
          if event.value > 0.5: k_right = True #go right
          else: k_right = False
        if event.axis == 1:
          if event.value < -0.5 + (main.gamestate == 0) / 5: k_up = True #go up
          else: k_up = False
          if event.value > 0.4 + (main.gamestate == 0) / 5: k_down = True #go down
          else: k_down = False
        if event.axis == 2:
          if event.value < -0.6: pass #look left
          if event.value > 0.6: pass #look right
        if event.axis == 3:
          if event.value < -0.6: pass #look up
          if event.value > 0.6: pass #look down
    if event.type == JOYBUTTONUP:
      if event.button == 0: k_use = False #x A
      if event.button == 1: k_up = False #o B
      if event.button == 2: k_use = False #□ X
      if event.button == 3: k_up = False #△ Y
      if event.button == 4: pass #share
      if event.button == 5: pass #PS
      if event.button == 6: pass #menu
      if event.button == 7: pass #L3
      if event.button == 8: pass #R3
      if event.button == 9: pass #L1 LB
      if event.button == 10: pass #R1 RB
      if event.button == 11: k_up = False #up
      if event.button == 12: k_down = False #down
      if event.button == 13: k_left = False #left
      if event.button == 14: k_right = False #right
      if event.button == 15: pass #pad
    if event.type == JOYDEVICEADDED:
      joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
      print("Current Controller Devices:", joysticks)
      for joystick in joysticks:
        print(joystick.get_name())
    if event.type == JOYDEVICEREMOVED:
      joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
      print("Current Controller Devices:", joysticks)
      for joystick in joysticks:
        print(joystick.get_name())
  if k_down and k_up and pygame.mouse.get_pressed(): pygame.image.save(screen, "screenshot.png")
  pygame.display.update()
  screen.fill("Black")
  clock.tick(FPS)

main = Main()

while True:
  main.update()