from typing import Any
from settings import *
from random import choice
from sys import exit
from os.path import join

from timer import Timer


class Game:
    def __init__(self, get_next_shape, update_score):

        # General
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft = (PADDING, PADDING))
        self.sprites = pygame.sprite.Group()

        # Game connection
        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # Lines
        self.line_surface = self.surface.copy()
        self.line_surface.fill((0 ,255, 0))
        self.line_surface.set_colorkey((0, 255, 0))
        self.line_surface.set_alpha(120)

        # Tetromino
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())), 
            self.sprites, 
            self.create_new_tetromino,
            self.field_data)

        # Timer
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.down_pressed = False
        self.timers = {
            'vertical move': Timer(UPDATE_START_SPEED, True, self.move_down),
            'horizontal move': Timer(MOVE_WAIT_TIME),
            'rotate': Timer(ROTATE_WAIT_TIME)
        }
        self.timers['vertical move'].activate()

        # Score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        # Audio
        self.landing_sound = pygame.mixer.Sound(join('Main','Tetris', 'sound', 'landing.wav'))
        
        self.landing_sound.set_volume(0.1)

    def calculate_score(self, num_lines):
        '''This function is calculating the score for us'''
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.3
            self.timers['vertical move'].duration = self.down_speed
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def check_game_over(self):
        '''This function is checking  game is over or not'''
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                exit()

    def create_new_tetromino(self):
        '''This function is for creating new tetrominos'''
        self.landing_sound.play()
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(), 
            self.sprites, 
            self.create_new_tetromino,
            self.field_data)

    def timer_update(self):
        '''This function is for updating the time.'''
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        '''This function is for making downward movement.'''
        self.tetromino.move_down()

    def draw_grid(self):
        '''This function is for creating a grid'''
        for col in range(1 ,COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (x, 0), (x, self.surface.get_height()), 1)

        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (0, y), (self.surface.get_width(), y), 1)

        self.surface.blit(self.line_surface, (0, 0))

    def input(self):
        '''This function is for getting input from user'''
        keys = pygame.key.get_pressed()

        # Checking horizontal movement
        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizantal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizantal(1)
                self.timers['horizontal move'].activate()

        # Check for rotation
        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

        # Down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed

    def check_finished_rows(self):
        '''This function is for checking finished rows'''
        # Get the full row indexes
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:
                # Delete full rows
                for block in self.field_data[delete_row]:
                    block.kill()

                # Move down the blocks
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # Rebuild the field data
            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # Update score
            self.calculate_score(len(delete_rows))

    def run(self):
        '''This function is for showing surfaces in the game window.'''

        # Update
        self.input()
        self.timer_update()
        self.sprites.update()

        # Drawing
        self.surface.fill(GRAY)
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Tetromino:
    '''Organizes multiples blocks in certain shape.'''
    def __init__(self, shape, group, create_new_tetromino, field_data):
        '''Initialize some elements'''
        # Setup
        self.shape = shape
        self.block_positions =  TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        # Creating blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # Collisons
    def next_move_horizontal_collide(self, blocks, amount):
        '''This function is for making collison from horizontal.'''
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, blocks, amount):
        '''This function is for making collision from vertical'''
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    # Movement
    def move_horizantal(self, amount):
        '''This function for making horizontal movement.'''
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def move_down(self):
        '''This function is for making downward movement.'''
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_new_tetromino()

    # Rotate
    def rotate(self):
        '''This function is for rotating figures'''
        if self.shape != 'O':
            #1. Pivot point
            pivot_pos = self.blocks[0].pos

            #2. New block position
            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            #3. Collision check
            for pos in new_block_positions:
                # Horizontal check
                if pos.x < 0 or pos.x >= COLUMNS:
                    return

                # Field chceck/ collision with other pieces
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

                # Vertical/floor check
                if pos.y > ROWS:
                    return

            #4. Implement new positions
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

class Block(pygame.sprite.Sprite):
    '''This is for blocks''' 
    def __init__(self, group, pos, color):
        '''Initiate simple elements''' 
        # General
        super().__init__(group)     
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        # Position
        self.pos = pygame.Vector2(pos) +BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.pos * CELL_SIZE)

    def rotate(self, pivot_pos):
        '''This function is for rotating'''
        # distance = self.pos - pivot_pos
        # rotated = distance.rotate(90)
        # new_pos = pivot_pos + rotated
        # return new_pos
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def horizontal_collide(self, x, field_data):
        '''This function is for checking collides'''
        if not 0 <= x < COLUMNS:
            return True
        
        if field_data[int(self.pos.y)][x]:
            return True
        
    def vertical_collide(self, y, field_data):
        '''This function is for checking collides'''
        if y >= ROWS:
            return True
        
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True
    
    def update(self):
        '''This function is for updating'''
        self.rect.topleft = self.pos * CELL_SIZE       