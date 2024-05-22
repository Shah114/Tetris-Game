# Modules
from settings import * 
from sys import exit
from os.path import join

from game import Game
from score import Score
from preview import Preview

from random import choice

# Classes
class Main:
    def __init__(self):
        '''This function is for creating window'''
        # General
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')

        # Shapes
        self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]
        print(self.next_shapes)

        # Components
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()

        # Audio
        self.music = pygame.mixer.Sound(join('Main', 'Tetris', 'sound', 'music.wav'))
        self.music.set_volume(0.05)
        self.music.play(-1)

    def update_score(self, lines, score, level):
        '''This function is for updating a score in game'''
        self.score.lines = lines
        self.score.score = score
        self.score.level = level
    
    def get_next_shape(self):
        '''This is function is for getting next shape from list.'''
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def run(self):
        '''This function is for making game loop'''
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # Exit everything
                    exit()


            # Display
            self.display_surface.fill(GRAY)

            # Components
            self.game.run()
            self.score.run()
            self.preview.run(self.next_shapes)
            
            # Updating the game
            pygame.display.update()
            self.clock.tick()


if __name__ == '__main__':
    main = Main()
    main.run()