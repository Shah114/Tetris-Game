from pygame.time import get_ticks

class Timer:
    def __init__(self, duration, repeated=False, func=None):
        '''Initialize main elements'''
        self.repeated = repeated
        self.func = func
        self.duration = duration

        self.start_time = 0
        self.active = False 
    
    def activate(self):
        '''This function is for activating the time'''
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        '''This function is for deactivating the time'''
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration and self.active:
            
            # Call a function
            if self.func and self.start_time != 0:
                self.func()

            # Reset timer
            self.deactivate()

            # Repeat the timer
            if self.repeated:
                self.activate()