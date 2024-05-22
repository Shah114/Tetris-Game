from settings import *
from os.path import join

class Score:
    ''''''
    def __init__(self):
        '''Initialize a score surface'''
        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING))
        self.rect = self.surface.get_rect(bottomright = (WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING))
        self.display_surface =  pygame.display.get_surface()

        # Font
        self.font = pygame.font.Font(join('Main', 'Tetris', 'graphics', 'Russo_One.ttf'), 30)

        # Increment
        self.increment_height = self.surface.get_height() / 3

        # Data
        self.score = 0
        self.level = 1
        self.lines = 0

    def display_text(self, pos, text):
        '''This function is for displaying text'''
        text_surface = self.font.render(f'{text[0]}: {text[1]}', True, 'white')
        text_rext = text_surface.get_rect(center=pos)
        self.surface.blit(text_surface, text_rext)

    def run(self):
        '''This function is for displaying surface'''
        self.surface.fill(GRAY)
        for i, text in enumerate([('Score', self.score), ('Level', self.level), ('Lines', self.lines)]):
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            self.display_text((x, y), text)

        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)