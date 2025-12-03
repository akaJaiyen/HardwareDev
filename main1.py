import pygame, sys
from button import Button
import datetime
import os
import random
import threading
import paho.mqtt.client as mqtt
from queue import Queue
import time
mqtt_message_queue = Queue()

# MQTT server details
mqtt_server = "iot.cpe.ku.ac.th"
mqtt_port = 1883
mqtt_username = "b6610502161"
mqtt_password = "phichak.l@ku.th"

# Callback when the client connects to the brokers
state = True

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("b6610502161/ldr")
        client.subscribe("b6610502161/sw")
        client.subscribe("b6610502161/switch18")
        client.subscribe("b6610502161/switch38")
    


# Callback when a message is received
def on_message(client, userdata, msg):
    try:
        global ldr_value, sw_value, switch18_value, switch38_value
        if msg.topic == 'b6610502161/ldr' :
            ldr_value = msg.payload.decode()
#             print(f"Received message on topic {msg.topic}: {ldr_value}")
        if msg.topic == 'b6610502161/sw' :
            sw_value = msg.payload.decode()
            print(f"Received message on topic {msg.topic}: {sw_value}")
        if msg.topic == "b6610502161/switch18":
            switch18_value = msg.payload.decode()
            print(f"Received message on topic 18.topic: {switch18_value}")
        if msg.topic == "b6610502161/switch38":
            switch38_value = msg.payload.decode()
            print(f"Received message on topic 38.topic: {switch38_value}")
#         print(f"Received message on topic {msg.topic}: {switch_value}")
        mqtt_message_queue.put(msg.payload.decode())
        # Add your message processing logic here
    except Exception as e:
        print(f"Exception in on_message: {e}")


# Create MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Set username and password
client.username_pw_set(mqtt_username, mqtt_password)

# Assign callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect_async(mqtt_server, mqtt_port)
client.loop_start()
pygame.init()

SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG2 = pygame.image.load("assets/Background.png")

#PICTURES INPUT
RUNNING = [pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),]
JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),]
SMALL_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),]
LARGE_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),]
BIRD = [pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),]
CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))
CREAM_COLOR=(255,255,255)

class Dinosaur:

    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if 40 <= ldr_value <= 69 and not self.dino_jump :  # jump
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True

        elif 91 <= ldr_value <= 100 and not self.dino_jump :  # duck
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
            
        elif 70 <= ldr_value <= 90 and not self.dino_jump :  # run
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [250, 290, 320]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def play(): #PLAY
    while True:
#         PLAY_MOUSE_POS = pygame.mouse.get_pos()
# 
#         SCREEN.fill("white")
# 
#         PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "Black")
#         PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
#         SCREEN.blit(PLAY_TEXT, PLAY_RECT)
# 
#         PLAY_BACK = Button(image=None, pos=(640, 460), 
#                             text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
# 
#         PLAY_BACK.changeColor(PLAY_MOUSE_POS)
#         PLAY_BACK.update(SCREEN)
# 
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
#                     main_menu()
        t1 = threading.Thread(target=menu(death_count=0), daemon=True)
        t1.start()

        pygame.display.update()
    
def options(): #SELECT CHARACTERS
    global RUNNING, JUMPING, DUCKING, SMALL_CACTUS, LARGE_CACTUS, BIRD, switch18_value, switch38_value, state
    switch18_value = 0
    switch38_value = 0
    x=0

    while True:
        SCREEN.blit(BG2, (0, 0))
        OPTIONS_MOUSE_POS_CHOOSE = pygame.mouse.get_pos()
        MENU_MOUSE_POS_CHOOSE = pygame.mouse.get_pos()
        MENU_TEXT = get_font(75).render("CHOOSE YOUR DINO", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        OPTION1_BUTTON = Button(image=None, pos=(320, 400), text_input="BLACK", font=get_font(50), base_color="#b68f40", hovering_color="Green")
        OPTION2_BUTTON = Button(image=None, pos=(640, 400), text_input="BLUE", font=get_font(50), base_color="#b68f40", hovering_color="Green")
        OPTION3_BUTTON = Button(image=None, pos=(960, 400), text_input="PINK", font=get_font(50), base_color="#b68f40", hovering_color="Green")
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        
        if switch38_value == '1' and state :
            x += 1
            state = False
        elif switch38_value == '0':
            state = True

        if (x+4)%4 ==0:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(320,400) #BLACK
        elif (x+4)%4 ==1:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(640,400) #BLUE
        elif (x+4)%4 ==2:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(960,400) #PINK
        elif (x+4)%4 ==3:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(640,600) #BACK
        
        OPTIONS_BACK = Button(image=None, pos=(640, 600), text_input="BACK", font=get_font(50), base_color="White", hovering_color="Green")
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS_CHOOSE)
        OPTIONS_BACK.update(SCREEN)
        
        for button in [OPTION1_BUTTON,OPTION2_BUTTON,OPTION3_BUTTON]:
            button.changeColor(MENU_MOUSE_POS_CHOOSE)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            #print(event.type, pygame.MOUSEBUTTONDOWN)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            yee = 1024
            if switch18_value == '1' and state :
                yee += 1
                state = False
            elif switch38_value == '0':
                state = True
            
            if yee == pygame.MOUSEBUTTONDOWN:
                
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS_CHOOSE):
                    main_menu()
                if OPTION1_BUTTON.checkForInput(OPTIONS_MOUSE_POS_CHOOSE): #BLACK
                    RUNNING = [pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),]
                    JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
                    DUCKING = [pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),]
                    SMALL_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),]
                    LARGE_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),]
                    main_menu()
                if OPTION2_BUTTON.checkForInput(OPTIONS_MOUSE_POS_CHOOSE): #BLUE
                    RUNNING = [pygame.image.load(os.path.join("assets/DinoBlue", "DinoRun1.png")),pygame.image.load(os.path.join("assets/DinoBlue", "DinoRun2.png")),]
                    JUMPING = pygame.image.load(os.path.join("assets/DinoBlue", "DinoJump.png"))
                    DUCKING = [pygame.image.load(os.path.join("assets/DinoBlue", "DinoDuck1.png")),pygame.image.load(os.path.join("assets/DinoBlue", "DinoDuck2.png")),]
                    main_menu()
                if OPTION3_BUTTON.checkForInput(OPTIONS_MOUSE_POS_CHOOSE): #PINK
                    RUNNING = [pygame.image.load(os.path.join("assets/DinoPink", "DinoRun1.png")),pygame.image.load(os.path.join("assets/DinoPink", "DinoRun2.png")),]
                    JUMPING = pygame.image.load(os.path.join("assets/DinoPink", "DinoJump.png"))
                    DUCKING = [pygame.image.load(os.path.join("assets/DinoPink", "DinoDuck1.png")),pygame.image.load(os.path.join("assets/DinoPink", "DinoDuck2.png")),]
                    main_menu()

        pygame.display.update()

def main_menu(): #MAIN MENU
    global switch18_value, switch38_value, state
    switch18_value=0
    switch38_value=0
    x=0
    while True:
        SCREEN.blit(BG2, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("DINOJAO", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), 
                            text_input="PLAY", font=get_font(66), base_color="#d7fcd4", hovering_color="Green")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
                            text_input="SELECT CHARACTERS", font=get_font(33), base_color="#d7fcd4", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUIT", font=get_font(66), base_color="#d7fcd4", hovering_color="Green")

        SCREEN.blit(MENU_TEXT, MENU_RECT)
        
        if switch38_value == '1' and state :
            x += 1
            print(x)
            state = False
        elif switch38_value == '0':
            state = True
        
        if (x+3)%3 ==0:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(640, 250) #PLAY
        elif (x+3)%3 ==1:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(640, 400) #SELECT
        elif (x+3)%3 ==2:
            SELECT_MOUSE_POS = pygame.mouse.set_pos(640, 550) #QUIT


        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            #print(event.type, pygame.MOUSEBUTTONDOWN)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            yee = 1024
            if switch18_value == '1' and state :
                yee += 1
                state = False
            elif switch38_value == '0':
                state = True
            
            if yee == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def main(): #PLAY GAME
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = get_font(25)
    obstacles = []
    death_count = 0
    pause = False

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        current_time = datetime.datetime.now().hour
        with open("score.txt", "r") as f:
            score_ints = [int(x) for x in f.read().split()]  
            highscore = max(score_ints)
            if points > highscore:
                highscore=points 
            text = font.render("High Score: "+ str(highscore) + "  Points: " + str(points), True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Game Paused, Press 'u' to Unpause", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                run = False
                paused()

        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                SCREEN.fill(CREAM_COLOR)
                gameover_over_font = get_font(100)
                game_over_text = gameover_over_font.render("GAME OVER", True, (182, 143, 64))
                game_over_rect = game_over_text.get_rect()
                game_over_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

                SCREEN.blit(game_over_text, game_over_rect)                
                

                
                pygame.display.update()
                
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()



def menu(death_count):
    global points, switch18_value, switch38_value, state, sw_value
    switch18_value = 0
    switch38_value = 0
    sw_value = 0
    x = 0
    run = True
    state = True
    while run:
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            FONT_COLOR = (0, 0, 0)
            SCREEN.fill(CREAM_COLOR)
        else:
            FONT_COLOR = (255, 255, 255)
            SCREEN.fill((128, 128, 128))
        font = get_font(30)

        if death_count == 0:
            text = font.render("PRESS ANY KEY TO START", True, (0, 0, 0))
        elif death_count >= 0:
            text = font.render("PRESS ANY KEY TO RESTART", False, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
            f = open("score.txt", "a")
            f.write(str(points) + "\n")
            f.close()
            with open("score.txt", "r") as f:
                score = (
                    f.read()
                )  # Read all file in case values are not on a single line
                score_ints = [int(x) for x in score.split()]  # Convert strings to ints
            highscore = max(score_ints)  # sum all elements of the list
            hs_score_text = font.render(
                "High Score : " + str(highscore), True, FONT_COLOR
            )
            hs_score_rect = hs_score_text.get_rect()
            hs_score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            SCREEN.blit(hs_score_text, hs_score_rect)
            MENU_MOUSE_POS2 = pygame.mouse.get_pos()

            MENU_BUTTON2 = Button(
                image=pygame.image.load("assets/Options Rect.png"),
                pos=(640, 550),
                text_input="BACK TO MENU",
                font=get_font(45),
                base_color="White",
                hovering_color="Green",
            )
            MENU_TEXT = get_font(100).render("GAME OVER", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
            SCREEN.blit(MENU_TEXT, MENU_RECT)

            SELECT_MOUSE_POS = pygame.mouse.set_pos(640, 550)  # QUIT
            for button in [MENU_BUTTON2]:
                button.changeColor(MENU_MOUSE_POS2)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                    pygame.quit()
                    exit()
                yee = 1024
                if switch18_value == "1" and state:
                    yee += 1
                    state = False
                elif switch38_value == "0":
                    state = True
                if yee == pygame.MOUSEBUTTONDOWN:
                    if MENU_BUTTON2.checkForInput(MENU_MOUSE_POS2):
                        main()

        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if sw_value == 1:
                    main()


def main():  # PLAY GAME
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, sw_value
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = get_font(25)
    obstacles = []
    death_count = 0
    pause = False

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        current_time = datetime.datetime.now().hour
        with open("score.txt", "r") as f:
            score_ints = [int(x) for x in f.read().split()]
            highscore = max(score_ints)
            if points > highscore:
                highscore = points
            text = font.render(
                "High Score: " + str(highscore) + "  Points: " + str(points),
                True,
                FONT_COLOR,
            )
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render(
            "Game Paused, Press 'u' to Unpause", True, FONT_COLOR
        )
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                run = False
                paused()

        current_time = datetime.datetime.now().hour

main_menu()