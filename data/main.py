from data.spritesheet import Spritesheet
import pygame as pg
import random
import sys
import os


# Pygame initialization
pg.init()

# Paths to the game's resources
gfx_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'graphics'))
sfx_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds'))
music_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'music'))


class Card(pg.sprite.Sprite):
    """Class representing a card"""

    frames = [(0, 0, 1, 284),
              (1, 0, 30, 284),
              (31, 0, 60, 284),
              (91, 0, 90, 284),
              (181, 0, 120, 284),
              (301, 0, 151, 284),
              (452, 0, 182, 284)]

    # Load the sound to be played when the card is flipped.
    sfx = pg.mixer.Sound(os.path.join(sfx_folder, 'cardflip.mp3'))
    sfx.set_volume(0.6)  # Set the SFX volume (values 0.0 to 1.0)

    def __init__(self, symbol, rank, pos):
        pg.sprite.Sprite.__init__(self)
        self.symbol = symbol
        self.rank = rank
        self.pos = pos
        self.face_up = False
        self.animated = False
        self.rotation = 0
        self.last_flipped = 0
        self.current_frame = 0
        self.sprites = self.get_sprites()
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect(topleft=self.pos)

    def get_sprites(self):
        front_spritesheet = Spritesheet(os.path.join(gfx_folder, f'{self.symbol.lower()}_{self.rank}.png'))
        back_spritesheet = Spritesheet(os.path.join(gfx_folder, 'card_back.png'))
        return back_spritesheet.sprites_at(Card.frames, -1)[::-1] + front_spritesheet.sprites_at(Card.frames, -1)

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.last_flipped == 0 or pg.time.get_ticks() - self.last_flipped > 1800:
                self.flip_up()
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if self.last_flipped == 0 or pg.time.get_ticks() - self.last_flipped > 1800:
                self.flip_up()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.center[0] - self.image.get_width()/2,
                                  self.rect.center[1] - self.image.get_height()/2))
        self.play_animation(self.rotation)

    def flip_up(self):
        self.animated = True
        Card.sfx.play()
        # Keep track of the last time the card was flipped.
        # This is used to allow the animation to finish playing before comparing cards.
        self.last_flipped = pg.time.get_ticks()

    def flip_down(self):
        self.face_up = False
        self.current_frame = 0
        self.image = self.sprites[self.current_frame]

    def rotate(self, degrees):
        self.rotation = degrees
        self.image = pg.transform.rotate(self.sprites[self.current_frame], degrees)
        self.rect = self.image.get_rect(topleft=self.pos)

    def play_animation(self, rotation):
        if self.animated and not self.face_up:
            if self.current_frame < len(self.sprites) - 1:
                self.current_frame += 1
                if self.current_frame == len(self.sprites) - 1:
                    self.animated = False
                    self.face_up = True
                    self.image = pg.transform.rotate(self.sprites[self.current_frame], rotation)
                self.image = pg.transform.rotate(self.sprites[self.current_frame], rotation)
        elif self.animated and self.face_up:
            if self.face_up >= 0:
                self.current_frame -= 1
                if self.current_frame == 0:
                    self.animated = False
                    self.face_up = False
                    self.image = pg.transform.rotate(self.sprites[self.current_frame], rotation)
                self.image = pg.transform.rotate(self.sprites[self.current_frame], rotation)
                
    def __str__(self):
        if self.rank == 11:
            return f'Jack of {self.symbol}'
        elif self.rank == 12:
            return f'Queen of {self.symbol}'
        elif self.rank == 13:
            return f'King of {self.symbol}'
        elif self.rank == 14:
            return f'Ace of {self.symbol}'
        else:
            return f'{self.rank} of {self.symbol}'


class Deck:
    """Class representing a deck of cards"""

    symbols = ('Clubs', 'Cups', 'Stars', 'Swords')

    def __init__(self):
        self.cards = []
        self.build_deck()

    def build_deck(self):
        for symbol in Deck.symbols:
            for rank in range(2, 14):
                self.cards.append(Card(symbol, rank, (0, 0)))

    def shuffle(self):
        # shuffle the deck. shuffle doesn't create a new list; it rearranges the existing one.
        random.shuffle(self.cards)


class Stack(pg.sprite.Sprite):
    """Class representing a stack of cards when there is a draw"""
    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.cards = []
        self.pos = pos
        self.image = pg.image.load(os.path.join(gfx_folder, 'card_draw_stacks_low.png')).convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)
        self.card_counter = Text(f'Cards in stack: {len(self.cards)}', 24, (self.rect.centerx, 400))

    def draw(self, surface):
        if self.cards:
            surface.blit(self.image, (self.rect.center[0] - self.image.get_width()/2,
                                      self.rect.center[1] - self.image.get_height()/2))
            self.card_counter.draw(surface)

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return f'Cards in stack: {len(self.cards)}'


class Player:
    """Class representing a player"""
    def __init__(self, name, holding):
        self.name = name
        # A list of the cards the player is holding.
        self.holding = holding

    # Used for debugging
    def card_report(self):
        print([card.current_frame for card in self.holding])

    def __str__(self):
        return f'{self.name} currently holds {len(self.holding)} cards'


class Text:
    """Class representing a basic UI text element.
    Used to create and update the various counters (round, cards, stack)"""
    def __init__(self, text, size, pos):
        self.font = pg.font.Font(None, size)
        self.text = text
        self.pos = pos

    def update(self, text):
        self.text = text

    def draw(self, surface):
        text_srf = self.font.render(self.text, True, 'white')
        rect = text_srf.get_rect(center=self.pos)
        surface.blit(text_srf, rect)


class Gameover:
    """Class representing an end game overlay"""
    def __init__(self, winner):
        self.surface = pg.Surface((600, 70))
        self.rect = self.surface.get_rect(center=(300, 400))
        self.text = Text(f'The game is over! {winner.name} won!', 40, (self.rect.centerx, self.rect.centery - 10))
        self.subtext = Text(f"Press 'Enter' to start a new game.", 24, (self.rect.centerx, self.rect.centery + 15))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        self.text.draw(surface)
        self.subtext.draw(surface)


class Game:
    """Class representing a game of war"""
    def __init__(self, screen):
        # Reference to the main window
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        # Round counter
        self.round = 1
        # Game end boolean
        self.game_over = False
        self.game_over_overlay = None
        # Create a Stack
        self.stack = Stack((490, screen.get_rect().centery))
        # Build the deck
        self.deck = Deck()
        # Shuffle the deck
        self.deck.shuffle()
        # Create the players and deal the cards
        self.player_1 = Player('Player 1', self.deck.cards[:24])
        self.player_2 = Player('Player 2', self.deck.cards[24:])
        random.shuffle(self.player_1.holding)
        random.shuffle(self.player_2.holding)
        # Cards
        self.card_1 = None
        self.card_2 = None

        # Set up the background image
        self.background = pg.image.load(os.path.join(gfx_folder, 'background.jpg')).convert()

        # UI text elements
        self.round_counter = Text(f'Round: {self.round}', 36, (self.screen_rect.centerx, 30))
        self.player_1_counter = Text(f'{self.player_1.name}: {len(self.player_1.holding)} cards',
                                     24, (100, 600))
        self.player_2_counter = Text(f'{self.player_2.name}: {len(self.player_2.holding)} cards',
                                     24, (100, 200))

        # Prepare the first two cards
        self.prepare_new_cards()

    def reset(self):
        # Round counter
        self.round = 1
        # Game end boolean
        self.game_over = False
        self.game_over_overlay = None
        # Build the deck
        self.deck = Deck()
        # Shuffle the deck
        self.deck.shuffle()
        # Create the players and deal the cards
        self.player_1 = Player('Player 1', self.deck.cards[:24])
        self.player_2 = Player('Player 2', self.deck.cards[24:])
        random.shuffle(self.player_1.holding)
        random.shuffle(self.player_2.holding)
        # Cards
        self.card_1 = None
        self.card_2 = None

        # UI text elements
        self.round_counter = Text(f'Round: {self.round}', 36, (self.screen_rect.centerx, 30))
        self.player_1_counter = Text(f'{self.player_1.name}: {len(self.player_1.holding)} cards',
                                     24, (100, 600))
        self.player_2_counter = Text(f'{self.player_2.name}: {len(self.player_2.holding)} cards',
                                     24, (100, 200))

        # Prepare the first two cards
        self.prepare_new_cards()

    def prepare_new_cards(self):
        print("Preparing cards...")

        # Force war for debugging purposes
        # self.player_1.holding[0] = Card('swords', 8, (0, 0))
        # self.player_2.holding[0] = Card('clubs', 8, (0, 0))

        if len(self.player_1.holding) > 0 and len(self.player_2.holding) > 0:
            self.card_1 = self.player_1.holding.pop(0)
            if self.card_1.rotation == 180:
                self.card_1.rotate(0)
            self.card_1.rect.center = (self.screen_rect.centerx, 600)

            self.card_2 = self.player_2.holding.pop(0)
            if self.card_2.rotation == 0:
                self.card_2.rotate(180)
            self.card_2.rect.center = (self.screen_rect.centerx, 200)

    def compare_cards(self):
        """Function that compares the ranks of the two cards being played.
           It updates the list of cards being held by each player, transfer
           them to the stack when needed, and keeps count of the game rounds."""
        print(f'Round {self.round}')
        print(f'{self.card_1} VS {self.card_2}')
        print("-"*30)
        if self.card_1.rank > self.card_2.rank:
            self.card_1.flip_down()
            self.card_2.flip_down()
            self.player_1.holding.extend([self.card_1, self.card_2])
            self.player_1.holding += self.stack.cards
            self.stack.cards = []  # Empty the stack
            print('Player 1 won this round')
            print(self.player_1)
            print(self.player_2)
            self.round += 1
            self.round_counter.update(f'Round: {self.round}')
            self.player_1_counter.update(f'{self.player_1.name}: {len(self.player_1.holding)} cards')
            self.player_2_counter.update(f'{self.player_2.name}: {len(self.player_2.holding)} cards')
        elif self.card_1.rank < self.card_2.rank:
            self.card_1.flip_down()
            self.card_2.flip_down()
            self.player_2.holding.extend([self.card_1, self.card_2])
            self.player_2.holding += self.stack.cards
            self.stack.cards = []  # Empty the stack
            print('Player 2 won this round')
            print(self.player_1)
            print(self.player_2)
            self.round += 1
            self.round_counter.update(f'Round: {self.round}')
            self.player_1_counter.update(f'{self.player_1.name}: {len(self.player_1.holding)} cards')
            self.player_2_counter.update(f'{self.player_2.name}: {len(self.player_2.holding)} cards')
        elif self.card_1.rank == self.card_2.rank:
            self.card_1.flip_down()
            self.card_2.flip_down()
            print('War. Adding cards to the stack...')
            self.stack.cards.extend([self.card_1, self.card_2])
            if len(self.player_1.holding) > 0 and len(self.player_2.holding) > 0:
                self.stack.cards.extend([self.player_1.holding.pop(0), self.player_2.holding.pop(0)])
            self.stack.shuffle()
            print(self.player_1)
            print(self.player_2)
            print(self.stack)
            self.round += 1
            self.round_counter.update(f'Round: {self.round}')
            self.player_1_counter.update(f'{self.player_1.name}: {len(self.player_1.holding)} cards')
            self.player_2_counter.update(f'{self.player_2.name}: {len(self.player_2.holding)} cards')
            self.stack.card_counter.update(f'Cards in stack: {len(self.stack.cards)}')
        print("="*30)

    def check_endgame(self):
        if len(self.player_1.holding) == 0:
            self.game_over = True
            print(f'The game is over! {self.player_2.name} won!')
            self.game_over_overlay = Gameover(self.player_2)
        elif len(self.player_2.holding) == 0:
            self.game_over = True
            print(f'The game is over! {self.player_1.name} won!')
            self.game_over_overlay = Gameover(self.player_1)

    def draw(self, surface):
        # Draw the cards and the UI elements
        self.card_1.draw(surface)
        self.card_2.draw(surface)
        self.stack.draw(surface)
        self.round_counter.draw(surface)
        self.player_1_counter.draw(surface)
        self.player_2_counter.draw(surface)
        if self.game_over:
            self.game_over_overlay.draw(surface)

    def update(self, surface):
        self.draw(surface)
        if self.card_1.face_up and self.card_2.face_up:
            if pg.time.get_ticks() - self.card_1.last_flipped > 1700:
                self.compare_cards()
                self.check_endgame()
                self.prepare_new_cards()


def main():
    # Basic settings and main game loop
    clock = pg.time.Clock()

    os.environ['SDL_VIDEO_CENTERED'] = "TRUE"  # Center the pygame window to the monitor
    pg.display.set_caption("WARpy")
    screen = pg.display.set_mode((600, 800))  # Create the main window

    # FPS setting. The card animation speed is bound to the game's FPS
    fps = 60

    # Create an instance of Game
    wargame = Game(screen)

    def event_loop():
        # Event handling loop
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if not wargame.game_over:
                wargame.card_1.get_event(event)
                wargame.card_2.get_event(event)
            if wargame.game_over:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        wargame.reset()

    def update():
        # Updates the game and draws everything on screen
        screen.blit(wargame.background, (0, 0))  # Draws the game background
        wargame.update(screen)

    # The main game loop
    while True:
        clock.tick(fps)/1000.0
        event_loop()
        update()
        pg.display.update()


if __name__ == '__main__':
    main()
