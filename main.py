import pygame
import math
from os.path import join
from random import randint, uniform

meteors_destoryed = 0


########pygame sprite that contains our surface and rectangle
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.original_image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.math.Vector2(self.rect.center)  # float position, source of truth
        

        #player direction movement distance
        self.direction = pygame.Vector2()
        self.angle = 0
        self.max_angle = 20
        self.rotationspeed = 10
        self.speed = 300

        #cooldown for laser
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

       
    #if player has shot check the time since last shot, if past cooldown then shoot is set to true
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    #update the player based om input
    def update(self, dt):
        #stores the key pressed in keys
        keys = pygame.key.get_pressed()
        #SETS PLAYER X VALUE IN CENTRE OF RECT TO 1 IF KEY IS PRESSED (LEFT OR RIGHT) AND BACK TO 0 IF NOT THANKS TO BOOLEAN
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        #same for y
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        #ensure that speed of player is consistent when moving diagonally
        self.direction = self.direction.normalize() if self.direction else self.direction
        # self.angle = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])

        if keys[pygame.K_RIGHT]:
            target_angle = -self.max_angle
        elif keys[pygame.K_LEFT]:
            target_angle = self.max_angle
        else:
            target_angle = 0

        self.angle += (target_angle - self.angle) * min(self.rotationspeed * dt, 1)


        #change the coord for players centre of rectangle using delta time method
        self.rect.center += self.direction * self.speed * dt
        self.pos += self.direction * self.speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.angle)


        #if pace is pressed and timer if statement above checks to see if cooldiwn has passed then shoot laser and restart timer + set shoot to false
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            #call the laser class
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
            

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        #import star image background
        self.image = surf 
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        
class Laser(pygame.sprite.Sprite):

    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.player = player
        self.original_image = surf
        self.angle = -self.player.angle

        # Rotate image to face player's direction
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_frect(midbottom=pos)

        # Position
        self.pos = pygame.math.Vector2(self.rect.center)

        # Direction: from_polar uses 0° = right, so offset by -90 to match "0° = up"
        self.direction = pygame.math.Vector2()
        self.direction.from_polar((1, self.angle - 90))
        self.speed = 400

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        screen = pygame.display.get_surface()
        if not screen.get_rect().contains(self.rect):
            self.kill()   

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        #give metoer direction but ensure they always travel down by setting y a 1
        self.direction = pygame.Vector2(uniform(-0.3, 0.3), 1)
        #set random speed for metoers
        self.speed = randint(200, 300)
        self.rotation_speed = randint(40, 80)
        self.rotation = 0
      


    #create meteor at randim coordonate and have it travel down y axis destroying oitslef off screen after 3 seconds
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        #set rotation speed and then give meteor properties neede to spin using .transform
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    #update frames for explosion animation
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index <len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running
    global meteors_destoryed


    #kill player if they collide with meteor, mask ensures we hit the actual image and not the edge of the rectangle the image is on
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    #check if player has collided with meteor
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            # laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            meteors_destoryed += 1
            print(meteors_destoryed)


def display_score():
    #display the current remaning gametime as a string usinimg font.render
    current_time = pygame.time.get_ticks() // 100
    text_surface = font.render(str(current_time), True, (240, 240, 230))
    text_rect = text_surface.get_frect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surface, text_rect)
    #place rectangle around the score using inflate so buffer between score and sides
    pygame.draw.rect(display_surface, (240, 240, 230), text_rect.inflate(20, 10).move(0, -8), 5, 10)
    text_surface2 = font.render(f"Meteors: {str(meteors_destoryed)}", True, (240, 240, 230))
    text_rect2 = text_surface2.get_frect(midtop = (WINDOW_WIDTH/8, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surface2, text_rect2)





################### general setup 
base_color = (255, 0, 0)  # Red
pulse_speed = 0.1
pulse_strength = 100
pygame.init()
#display size and create window
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
#set window title
pygame.display.set_caption("Space Shooter")
#the standard state of our while loop for the game
running = True
#add clock
clock = pygame.time.Clock()

################ importing 

#import meteor image
meteor_surface = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
#import laser image
laser_surface = pygame.image.load(join('images', 'laser.png')).convert_alpha()
# import star surface once outside of class so not importing it 20 times
star_surf = pygame.image.load(join( 'images', 'star.png')).convert_alpha()
#import our font
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
text_surface = font.render('text', True, (240, 240, 230))
#explosion frames 
explosion_frames = [pygame.image.load(join('images', 'explosion',f'{i}.png')).convert_alpha() for i in range(21)]
#import laser sound and set volume
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav')) 
laser_sound.set_volume(0.15)
#import explosion sound
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav')) 
explosion_sound.set_volume(0.2)
#import game music sound
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav')) 
game_music.set_volume(0.1)
#plays music indefinetly
game_music.play(loops = -1)


################### sprites
#adds all our sprites into one object so we can call it later
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

#create the stars in 20 random locations
for i in range(20):
    Star(all_sprites, star_surf)
#create player in game 
player = Player(all_sprites)


#################### custom events

#meteor event
#create custom event stored in metoer event variable
meteor_event = pygame.event.custom_type()
#timer that lasts half a second
pygame.time.set_timer(meteor_event, 500)

fullscreen = False
##################### run game
while running:
    #set framrate to computer optimal framerate
    dt = clock.tick()/1000

    #event loop
    for event in pygame.event.get():
        #check for all user interactions
        if event.type == pygame.QUIT:
            running = False

        #on meteor event, get random spaw co-ordinates and call metero sprite to spawn it
        if event.type == meteor_event:
           #set x co-ordinate outside the window so cant see them spawn
           x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
           Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprites))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:  # Common toggle key
                fullscreen = not fullscreen
                if fullscreen:
                    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Windowed size

    #update the game
    all_sprites.update(dt)

    #call collisions function to update if laser has destroyed meteor
    collisions()
    ##############draw the game
    
    #fill the window with colour
    display_surface.fill("#35064c")

    #draw the sprites held in the class onto the display surface
    all_sprites.draw(display_surface)

    #text displaying timer
    display_score()

    #updates the window
    pygame.display.update()




pygame.quit()
