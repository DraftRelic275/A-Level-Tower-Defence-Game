#####################library files########################
import math
import os
import time
import pygame

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
################this inistialises the pygame settings##########################

pygame.init()

#set up screen dimensions
display_width = 800
display_height = 600
FPS = 60

gameDisplay = pygame.display.set_mode((display_width,display_height))
clock = pygame.time.Clock()    ###  this enables us to set frame rate

#colour constants for button backgrounds and screen backgrounds
BLACK = (0,0,0)
WHITE = (255,255,255)

RED = (200,0,0)
GREEN = (0,200,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
BRIGHT_RED = (255,0,0)
BRIGHT_GREEN = (0,255,0)
LIGHT_YELLOW = (255,255,51)
BUTTON_HOVER = (220,220,220)

AQUA = (0, 128, 128)
AQUA1 = (0, 115, 115)
GRAY = (190, 190, 190)
SHOP = (180, 180, 180)

#  Game Variables
playerHealth = 100
Op1 = False
Op2 = False
Cl1 = False
Cl2 = False
Fate = None


Ts = "None selected" # text for which tower type is selected
TSx = 1000
TSy = 1000
TowerNum = 0

# X and Y coordinates for the buttons in the shop.
clicked1 = 0
Bx1, By1, Bw1, Bh1 = 1000, 1000, 200, 80
Bx2, By2, Bw2, Bh2 = 1000, 1000, 200, 80
B1P = 0

UBx1, UBy1, UBw1, UBh1 = 1000, 1000, 200, 80
UBx2, UBy2, UBw2, UBh2 = 1000, 1000, 200, 80
B1Cooldown = 10
B2Cooldown = 10


# Variables for the upgrade bar 

# Variables for clicking the 2nd tower button
clicked2 = 0
Cl21 = False
Cl22 = False

# 
Tclicked = 0
TCl1 = False
TCl2 = False

# determines what type of tower is placed --- can be 1 or 2
ActType = 0
SelRngLvl = 0
SelDmgLvl = 0

#this is for text boxes on the screens i.e. titles etc

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

#  this creates our buttons parameters text, x position, y position, width of button, height of button, colour, hover colour, function to run.

def button(msg,x,y,w,h,ic,ac,action=None):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    #  check position and draw the rectangle - takes the screen we set up gameDisplay. We will need to amend if using multiple screens

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
    smallText = pygame.font.SysFont("arial",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)

##################################################################################################################################################################
##################################################################################################################################################################

class bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, rel_x, rel_y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(pos_x+25, pos_y+25))
        self.x_move, self.y_move = rel_x, rel_y
 
    def update(self,):
        self.rect.x += self.x_move * 20    #due to rsin(theta) and rcos(theta)
        self.rect.y += self.y_move * 20
        

    def deleteB(self):
        if self.rect.x >= 800 or self.rect.x <= 0 or self.rect.y >= 600 or self.rect.y <= 0:
            self.kill()
##################################################################################################################################################################

class Tower(pygame.sprite.Sprite):
    def __init__(self, Type, x, y, name):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((60,60))
        self.rect = self.image.get_rect(center = (x,y))
        self.rect.x = x
        self.rect.y = y
        self.key_time = 10
        self.cooldown = 120
        self.range = 120
        self.type = Type
        self.visibility = 100
        self.Tselected = False
        self.TselectTime = 10
        self.name = "Tower" + name
        self.RangeLevel = 0
        self.DamageLevel = 0
        self.DmgBase = 5
        self.damage = 5 

        if self.type == 1:
            self.image = pygame.image.load(dname + "/tower-type-1.png")
            self.DmgBase = 5
        if self.type == 2:
            self.image = pygame.image.load(dname + "/tower-type-2.png")
            self.DmgBase = 7
            self.range = 90

        #range image
        self.range_image = pygame.Surface((self.range * 2, self.range*2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        pygame.draw.circle(self.range_image, "grey", (self.range, self.range), self.range)
        self.range_image.set_alpha(self.visibility)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.x = x
        self.range_rect.y = y
        self.range_rect.center = self.rect.center
    
    def UpgradeDamage(self):
        if Admin.getMoney() >= (30 + self.DamageLevel * 30):
            Admin.TakeMoney(30 + self.DamageLevel * 30)
            self.DamageLevel += 1
            self.damage = 7 + (self.DamageLevel * self.DmgBase)
    
    def UpgradeRange(self):
        if Admin.getMoney() >= (60 + self.RangeLevel * 60):
            Admin.TakeMoney(60 + self.RangeLevel * 60)
            self.RangeLevel += 1
            self.range = 120 + (10*self.RangeLevel)
            self.range_image = pygame.Surface((self.range * 2, self.range*2))
            self.range_image.fill((0,0,0))
            self.range_image.set_colorkey((0,0,0))
            pygame.draw.circle(self.range_image, "grey", (self.range, self.range), self.range)
            self.range_image.set_alpha(self.visibility)
            self.range_rect = self.range_image.get_rect()
            self.range_rect.x = self.rect.x
            self.range_rect.y = self.rect.y
            self.range_rect.center = self.rect.center

    def getRngLvl(self):
        return self.RangeLevel

    def getDmgLvl(self):
        return self.DamageLevel

    # functions for cooldown of shooting
    def getCooldown(self):
        return self.cooldown
    
    def setCooldown(self):
        self.cooldown = 120

    def ChangeCooldown(self):
        self.cooldown += 1

    # draws the range for the towers
    def drawR(self, surface):
        surface.blit(self.range_image, self.range_rect)

    # functions for selection of towers
    def getSelected(self):
        return self.Tselected
    
    def setSelectedT(self):
        self.Tselected = True
        self.range_image.set_alpha(100)
    
    def setSelectedF(self):
        self.Tselected = False
        self.range_image.set_alpha(0)

    # gets the coordinates of the towers
    def getX(self):
        return self.rect.x
    
    def getY(self):
        return self.rect.y
    
    # sets the colour for the type of tower
    def set(self):
        if self.type == 1:
            self.range_image.fill(RED)
        if self.type == 2:
            self.range_image.fill(BLUE)

    # functions for placemment time delay
    def GetTime(self):  # returns the value of the time delay
        return self.key_time
    
    def ChangeTime(self): # decrease by 1 per tick
        self.key_time -= 1
        
    def setTime(self):   # set back to original
        self.key_time = 10
    
    # for updating the tower
    def updateT(self, mob_group):
        if self.cooldown == 120:
            self.pick_target(mob_group)
            self.cooldown = 0 
            self.target = None

    # for picking a mob within range
    def pick_target(self, mob_group):
        # find a mob for the tower to target within range
        x_dist = 0
        y_dist = 0
        # check distance to each enemy to see if it is within range
        for mob in mob_group:
            x_dist = mob.getX() - self.rect.x
            y_dist = mob.getY() - self.rect.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = mob
                print("Target Picked:", mob)
                mob.TakeHealth(self.damage)
                bulletgroup.add(self.bullet(mob.getX(), mob.getY()))
                break

    def bullet(self, mobx, moby):
        # Ensure camera stays within the boundaries of the game world
        self.rel_x, self.rel_y = mobx - self.rect.x, moby - self.rect.y # self.relx/y will be cooridnates of mob on map
        distance=math.hypot(self.rel_x, self.rel_y)
        if distance==0:
            self.rel_x,self.rel_y =0 ,0
        else:
            self.rel_x , self.rel_y = self.rel_x/distance , self.rel_y/distance
        print("shot")
        return bullet(self.rect.x,self.rect.y,self.rel_x,self.rel_y)    

##################################################################################################################################################################
##################################################################################################################################################################

class Mob(pygame.sprite.Sprite):
    walkright = [pygame.image.load(dname + "/Goblin_run_right.gif")]   # Mob images for walking in different directions
   
   # constructor
    def __init__(self, Mtype, offset, WaveScale):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)  # calls constructor of parent class
        self.image = pygame.image.load(dname + "/Goblin_run_right.gif").convert_alpha()
        self.rect=self.image.get_rect(center =(16,331))
        self.rect.x= 0 - offset # set x position
        self.rect.y= 315   # set y position
        self.xholder = 0
        self.path = [self.rect.x, 125, 125, 296, 375, 520, 245, 805]
        self.pathT = [True, False, False, False, False, False, False, False]
        self.vel= 5 # sets x and y speeds for the mobs
        self.dmg = 0
        self.MobType = Mtype 
        self.health = 10
        self.healthLevel = 0

        if self.MobType == 1:
            self.health = 10 + (10 * WaveScale)
            self.vel = 2
            self.dmg = 10

   
    def drawP(self): # draws the mob on screen
        self.move()

    def move(self): # moves the mob along a set path
        if self.vel > 0:
            if self.pathT[0]:
                if self.rect.x + self.vel <self.path[1]:
                    self.rect.x += self.vel
                else:
                    self.pathT[1] = True
                    self.pathT[0] = False

            if self.pathT[1]:
                self.xholder = self.rect.x
                if self.rect.y - self.vel > self.path[2]:
                    self.rect.y -= self.vel
                else:
                    self.pathT[2] = True
                    self.pathT[1] = False

            if self.pathT[2]:
                self.xholder = self.rect.x
                if self.rect.x + self.vel < self.path[3]:
                    self.rect.x += self.vel 
                else:
                    self.pathT[3] = True
                    self.pathT[2] = False

            if self.pathT[3]:
                self.xholder = self.rect.x
                if self.rect.y + self.vel < self.path[4]:
                    self.rect.y += self.vel
                else:
                    self.pathT[4] = True
                    self.pathT[3] = False
            
            if self.pathT[4]:
                if self.rect.x + self.vel < self.path[5]:
                    self.rect.x += self.vel
                else:
                    self.pathT[5] = True
                    self.pathT[4] = False

            if self.pathT[5]:
                if self.rect.y - self.vel > self.path[6]:
                    self.rect.y -= self.vel
                else:
                    self.pathT[6] = True
                    self.pathT[5] = False
            if self.pathT[6]:
                if self.rect.x + self.vel < self.path[7]:
                    self.rect.x += self.vel
                else:
                    self.pathT[6] = False
    
    def checkHealth(self):
        if self.health <= 0:
            if self.MobType == 1:
                Admin.GiveMoney(30)
            self.kill()

    def TakeHealth(self, dmg):
        self.health -= dmg
        print(self.health)
    
    def getX(self):
        return self.rect.x
    
    def getY(self):
        return self.rect.y
    
    def End(self):
        if self.rect.x >= 800:
            Admin.take_health1(self.dmg)
            self.kill()

##################################################################################################################################################################

class PlacementBlock(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((60,59))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = 0
        self.key_time = 10 # time delay
        self.type = 0 # type of tower
        self.action = None # which tower type is selected
        self.lock = 0 # locks block so tower type cant be changed
        self.TowPlc = False # tower placed

    def getTowPlc(self):
        return self.TowPlc

    def setTowPlc(self):
        self.TowPlc = True

    def getClicked(self):
        return self.clicked
    
    def getX(self):
        return self.rect.x
    
    def getY(self):
        return self.rect.y
    
    def getType(self):
        return self.type

    def pressed(self, actionType): # will check if a placeable spot has been clicked 
        self.action = actionType
        Flag = ShopScreen.GetFlag()
        click = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        if Flag: # checks that the shop is open before a placement block can be selected
            if self.clicked == 0: # checks if it has been clicked on before
                if self.key_time != 0: # creates a time delay between processed clicks
                    self.key_time -= 1
                if self.key_time == 0:  # checks that the delay has ended before the box can be clicked
                    if pos[0] < self.rect.x and pos[1] < self.rect.y or pos[0] > (self.rect.x + 50) and pos[1] > (self.rect.y + 50): # if the mouse is outside the box
                        if click[0]: # if the left mouse button is clicked
                            click = False # sets the boolean value for left mouse click to false
                    if (pos[0] >= self.rect.x and pos[1] >= self.rect.y) and (pos[0] <= (self.rect.x + 50) and pos[1] <= (self.rect.y + 50)): # if the mouse is inside the box     
                        if (self.action == 1 and Admin.getMoney() >= 50) or (self.action == 2 and Admin.getMoney() >= 60):
                            if click[0]: # checks if the left mouse button has been clicked 
                                print("block clicked")
                                self.key_time = 20 #resets the time delay
                                self.clicked = 1 # sets clicked to 1 to show it has been clicked and used
                            else:
                                pass
                        else:
                            pass

        if self.lock == 0: # checks if the box has been locked to a type of tower
            if self.clicked == 1: # checks box has been clicked
                if self.action == 1: # if tower type is 1
                    self.image.fill(AQUA) # sets box colour to blue
                    self.lock = 1
                if self.action == 2: # if tower type is 2
                    self.image.fill(GREEN) # sets box colour to green
                    self.lock = 1

##################################################################################################################################################################

class ScreenBar(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width,height))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.UP = 0
        self.rect.x = x
        self.rect.y = y

##################################################################################################################################################################

class ShopBar(pygame.sprite.Sprite):
    global Bx1, By1, Bw1, Bh1, Op1, Op2
    global Bx2, By2, Bw2, Bh2, TSx, TSy, ActType
    def __init__(self):   # defines private attributes
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((800,100))
        self.image.fill(SHOP)
        self.rect = self.image.get_rect()
        self.Status = 0
        self.Ustatus = 0
        self.rect.x = 0
        self.rect.y = 1000
        self.key_time = 10
        self.Flag = False
    
    def GetTime(self):  # returns the value of the time delay
        return self.key_time
    
    def ChangeTime(self): # decrease by 1 per tick
        self.key_time -= 1
        
    def setTime(self):   # set back to original
        self.key_time = 10
    
    def GetStatus(self):  # returns whether shop is shown or hidden
        return self.Status
    
    def SetStatus(self, status):   # sets shop to shown or hidden
        self.Status = status
        
    def hideShop(self):   # hides the shop in game
        if self.Status == 1:
            print("Works to Hide")
            self.rect.y = 1000
            self.Status = 0 # shows the shop has been hiden

    def ShowShop(self):   # shows the shop in game
        if self.Status == 0:
            print("Works to show")
            self.rect.y = 450
            self.Status = 1 # shows the shop has been moved onto the screen

    def SetFlag1(self): # sets a flag variable true to say the shop has been used
        self.Flag = True

    def SetFlag2(self): # sets the flag variable to false to show the shop has been closed
        self.Flag = False

    def GetFlag(self):
        return self.Flag
    
    def ShowUpgrade(self):
        self.rect.y = 450

    def HideUpgrade(self):
        self.rect.y = 1000
           
##################################################################################################################################################################
##################################################################################################################################################################

class Player(pygame.sprite.Sprite):
    # constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # calls constructor of parent class
        self.health = 100
        self.money = 250
        self.key_time = 10
        self.PlacementTime = 1
        self.MobsInWave = [[1,6], [1,10], [1,10], [1,20], [1,25], [1,30], [1,35], [1,35], [1,45], [1,50]]
        self.WavesBool = [True,False,False,False,False,False,False,False,False,False] 
        self.MobSpawned = [False,False,False,False,False,False,False,False,False,False]
        self.WaveDelay = 900
        self.startDelay = 0
    
    def waves(self):
        if self.startDelay == 1200:
            if self.WavesBool[0] == True and self.WaveDelay == 900:
                if self.MobSpawned[0] == False:
                    for x in range(0, self.MobsInWave[0][1]):
                        mob = Mob(self.MobsInWave[0][0], x*300, 0)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[0] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[1] = True
                    self.WavesBool[0] = False

            if self.WavesBool[1] == True and self.WaveDelay == 900:
                if self.MobSpawned[1] == False:
                    for x in range(0,self.MobsInWave[1][1]):
                        mob = Mob(self.MobsInWave[1][0], x*300, 1)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[1] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[2] = True
                    self.WavesBool[1] = False

            if self.WavesBool[2] == True and self.WaveDelay == 900:
                if self.MobSpawned[2] == False:
                    for x in range(0,15):
                        mob = Mob(self.MobsInWave[2][0], x*300, 2)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[2] = True
                       
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[3] = True
                    self.WavesBool[2] = False

            if self.WavesBool[3] == True and self.WaveDelay == 900:
                if self.MobSpawned[3] == False:
                    for x in range(0,self.MobsInWave[3][1]):
                        mob = Mob(self.MobsInWave[3][0], x*300, 3)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[3] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[4] = True
                    self.WavesBool[3] = False

            if self.WavesBool[4] == True and self.WaveDelay == 900:
                if self.MobSpawned[4] == False:
                    for x in range(0,self.MobsInWave[4][1]):
                        mob = Mob(self.MobsInWave[4][0], x*300, 4)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[4] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[4] = False
            
            if self.WavesBool[5] == True and self.WaveDelay == 900:
                if self.MobSpawned[5] == False:
                    for x in range(0,self.MobsInWave[5][1]):
                        mob = Mob(self.MobsInWave[5][0], x*300, 5)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[5] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[5] = False
            
            if self.WavesBool[6] == True and self.WaveDelay == 900:
                if self.MobSpawned[6] == False:
                    for x in range(0,self.MobsInWave[6][1]):
                        mob = Mob(self.MobsInWave[6][0], x*300, 6)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[6] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[6] = False

            if self.WavesBool[7] == True and self.WaveDelay == 900:
                if self.MobSpawned[7] == False:
                    for x in range(0,self.MobsInWave[7][1]):
                        mob = Mob(self.MobsInWave[7][0], x*300, 7)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[7] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[7] = False
            
            if self.WavesBool[8] == True and self.WaveDelay == 900:
                if self.MobSpawned[8] == False:
                    for x in range(0,self.MobsInWave[8][1]):
                        mob = Mob(self.MobsInWave[8][0], x*300, 8)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[8] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[8] = False
            
            if self.WavesBool[9] == True and self.WaveDelay == 900:
                if self.MobSpawned[9] == False:
                    for x in range(0,self.MobsInWave[9][1]):
                        mob = Mob(self.MobsInWave[9][0], x*300, 9)
                        mob_group.add(mob)
                        all_sprites_group.add(mob)
                    self.MobSpawned[9] = True
                if len(mob_group) == 0:
                    self.setWaveDelay()
                    self.WavesBool[9] = False
    
    def GetMobSpawned(self):
        return self.MobSpawned

            
    def setWaveDelay(self):
        self.WaveDelay = 0
    
    def ChangeWaveDelay(self):
        self.WaveDelay += 1
    
    def getWaveDelay(self):
        return self.WaveDelay   
    
    def getStartDelay(self):
        return self.startDelay
    
    def changeStartDelay(self):
        self.startDelay += 1 
    
    def SetPT(self):
        self.PlacementTime = 0
    
    def GetPT(self):
        return self.PlacementTime 

    def ChangePT(self):
        self.PlacementTime += 1


    def take_health1(self, amount): # takes 5 health from player once mob reaches end of path
        self.health -= amount

    def get_health(self): # returns the value of the players health
        return self.health
    
    def getMoney(self): # returns the amount of money the player has
        return self.money

    def GiveMoney(self, amount): # gives money to the player
        self.money += amount

    def TakeMoney(self, amount): # takes money from the player
        self.money -= amount
    
    def GetTime(self):  # returns the value of the time delay
        return self.key_time
    
    def ChangeTime(self): # decrease by 1 per tick
        self.key_time -= 1
        
    def setTime(self):   # set back to original
        self.key_time = 10

    
#  creates the screen area - will need one for each screen when using background images to be done next
#  gamedisplay is the screen area where we draw things to from now on

############################################################################# --- This instanciates the blocks onscreen that represent where towers can be placed.
##################################################################################################################################################################



all_sprites_group = pygame.sprite.Group()  #  sprite group to hold everything


BlockPos = [[40,225],[10,365],[90,365],[193,270],[193,190],[40,140],[115,50],[193,50],[270,50],[345, 130],[345, 205],[345, 280],[425, 280],[193,350],
            [295, 425], [390,425], [485,425], [570,305], [570, 375], [650,305], [725, 305], [575, 175], [650, 175], [725, 175], [500, 175], [425, 205]]
block_group = pygame.sprite.Group()
for x in range(0, len(BlockPos)):
    block = PlacementBlock(BlockPos[x][0], BlockPos[x][1])
    block_group.add(block)
    all_sprites_group.add(block)

Admin = Player()



Bar = ScreenBar(800, 50, 0, 550) # grey bar at the bottom of the screen
ShopScreen = ShopBar() # grey bar that appears when the shop button is pressed
UpgradeScreen = ShopBar() # grey bar that apprears for tower upgrades 
Shop_group = pygame.sprite.Group()
all_sprites_group.add(Bar)
Shop_group.add(ShopScreen)
Shop_group.add(UpgradeScreen)



bulletgroup = pygame.sprite.Group() # 
towergroup = pygame.sprite.Group() # group containing all towers placed 



mob_group=pygame.sprite.Group()


##################################################################################################################################################################
##################################################################################################################################################################

# Brings up the Game shop

def UpgradeShop():
    global Bx1, By1, Bw1, Bh1, Op1, Op2
    global Bx2, By2, Bw2, Bh2, TSx, TSy, ActType
    global UBx1, UBy1, UBx2, UBy2
    status = ShopScreen.GetStatus()

    for tower in towergroup:

        if tower.getSelected() == True and status == 0:
            UpgradeScreen.ShowUpgrade()
            print("gets to here")
            UBx1 = 50
            UBy1 = 460
            UBx2 = 550
            UBy2 = 460
            break

        if tower.getSelected() == True and status == 1:
            ShopScreen.hideShop()
            UpgradeScreen.ShowUpgrade()
            Op2 = True
            Bx1 = 1000
            By1 = 1000
            Bx2 = 1000
            By2 = 1000
            TSx = 1000
            TSy = 1000
            UBx1 = 50
            UBy1 = 460
            UBx2 = 550
            UBy2 = 460
            ActType = 0
            ShopScreen.SetFlag2()
            break

        if tower.getSelected() == False:
            print("does this")
            for tower2 in towergroup:
                if tower2.getSelected() == True:
                    UpgradeScreen.HideUpgrade()
            UpgradeScreen.HideUpgrade()
            ShopScreen.hideShop()
            Op2 = True
            Bx1 = 1000
            By1 = 1000
            Bx2 = 1000
            By2 = 1000
            TSx = 1000
            TSy = 1000
            UBx1 = 1000
            UBy1 = 1000
            UBx2 = 1000
            UBy2 = 1000
            ActType = 0
            ShopScreen.SetFlag2()

def Shop():
    global Bx1, By1, Bw1, Bh1, Op1, Op2
    global Bx2, By2, Bw2, Bh2, TSx, TSy, ActType
    global UBx1, UBy1, UBx2, UBy2
    status = ShopScreen.GetStatus()
    time = ShopScreen.GetTime()

    if status == 0 and time == 10:

        ShopScreen.ShowShop()
        UpgradeScreen.HideUpgrade()
        Op1 = True 
        Bx1 = 50
        By1 = 460  
        Bx2 = 550
        By2 = 460
        TSx = 400
        TSy = 500
        UBx1 = 1000
        UBy1 = 1000
        UBx2 = 1000
        UBy2 = 1000
        ActType = 0
        ShopScreen.SetFlag1()

        for tower in towergroup:
            tower.setSelectedF()

    if status == 1 and Op1 == False and time == 10:

        ShopScreen.hideShop()
        UpgradeScreen.HideUpgrade()
        Op2 = True
        Bx1 = 1000
        By1 = 1000
        Bx2 = 1000
        By2 = 1000
        TSx = 1000
        TSy = 1000
        UBx1 = 1000
        UBy1 = 1000
        UBx2 = 1000
        UBy2 = 1000
        ActType = 0
        ShopScreen.SetFlag2()

        for tower in towergroup:

            tower.setSelectedF()

def Tw1():
    global clicked1, Cl1, Cl2, ActType, clicked2
    time = Admin.GetTime()
    if clicked1 == 1 and time == 10:

        clicked1 = 0
        Cl1 = True
        ActType = 0
        print(clicked1)

    else:

        if time == 10:

            clicked1 = 1
            clicked2 = 0
            Cl2 = True
            ActType = 1
            print(clicked1)
    
def Tw2():

    global clicked2, Cl21, Cl22, ActType, clicked1
    time = Admin.GetTime()

    if clicked2 == 2 and time == 10:

        clicked2 = 0
        Cl21 = True
        ActType = 0
        print(clicked2)

    else:

        if time == 10:

            clicked2 = 2
            clicked1 = 0
            Cl22 = True
            ActType = 2
            print(clicked2)

def UpgradeDmg():
    global B1Cooldown
    for tower in towergroup:
        if tower.getSelected() == True and B1Cooldown == 10:
            tower.UpgradeDamage()
            B1Cooldown = 0

def UpgradeRng():
    global B2Cooldown
    for tower in towergroup:
        if tower.getSelected() == True and B2Cooldown == 10:
            if tower.getRngLvl() < 5:                
                tower.UpgradeRange()
                B2Cooldown = 0
                

            

#  main menu screen

def main_menu():
    global intro, play, EndL
    time.sleep(0.2)
    intro = True    ####  will display until we set to false
    play = False
    EndL = False  
    Bg = pygame.image.load(dname + "/MMBG.jpg")
    Bg = pygame.transform.scale(Bg,(display_width,display_height))
    while intro:
        for event in pygame.event.get():
            #  checks that we havent hit the x in the window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        #set our screen background colour (change to image here)        
        #gameDisplay.fill(WHITE)
        gameDisplay.fill(GRAY)
        gameDisplay.blit(Bg,(0,0))
        #sets the text size and font for title -could be declared globally
        largeText = pygame.font.SysFont("tahoma",50)
        TextSurf, TextRect = text_objects("MAIN MENU", largeText)
         #sets the position of title text - i just changed the display_height divided by for vertical position
        TextRect.center = ((display_width/2),(display_height/5))
        gameDisplay.blit(TextSurf, TextRect)

        #call button function to create the buttons
        # these buttons trigger different game states
        button("Play",350,250,125,50,GRAY,BUTTON_HOVER,game_loop)
        button("Quit",350,450,125,50,GRAY,BUTTON_HOVER,quitgame)

        pygame.display.update()
        clock.tick(FPS)  ### set frame rate to 15
    
#main game loop - change your main game play loop to a procedure so that it runs from the button.

def game_loop():
    global Op1, Op2, Cl1, Cl2, Cl21, Cl22, TCl1, TCl2
    global Bx1, By1, Bw1, Bh1
    global Bx2, By2, Bw2, Bh2, TSx, TSy, Ts
    global ActType, TowerNum, SelDmgLvl, SelRngLvl
    global UBx1, UBx2, UBy1, UBy2, UBw1, UBh1, UBw2, UBh2, B1Cooldown, B2Cooldown
    global intro, Fate, play, EndL
    intro = False  

    play = True
    x = 0
    Bg = pygame.image.load(dname + "/TowerDefencePath.jpg")
    Bg = pygame.transform.scale(Bg,(display_width,display_height))

    while play:
        # Event Handler
        for event in pygame.event.get():
            # Quits the program when the window is closed.
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # checks if the left mouse button has been clicked.
                ### Loop which will check whether a placement block has been clicked and place a tower if one was selected in the shop. ###
                for block in block_group:
                    block.pressed(ActType)
                    if block.getClicked() == 1 and block.getTowPlc() == False: # checks that a tower type has been selected for placement, a block has been clicked and a tower hasn't already been placed in that spot.
                        if ActType == 1:   
                            Admin.TakeMoney(50)
                            Xco = block.getX() # gets the x coordinate of the placement block
                            Yco = block.getY() # gets the y coordinate of the placement block
                            print(Xco,Yco)
                            TowerNum += 1 #  adds 1 to a count variable for the no. of towers so a name can be assigned to each --> e.g. 'Tower1' 
                            # sets all towers already placed, to have a selected variable of False.
                            for tower1 in towergroup: # loops through all the towers in the tower group.
                                tower1.setSelectedF() # sets the selected variable to false
                    
                            tower = Tower(ActType, Xco, Yco, str(TowerNum))# instanciates an object of the tower class to be placed on a tower block.
                            towergroup.add(tower) # adds the placed tower to the tower group.
                            all_sprites_group.add(tower) # adds the placed tower to the group of all sprites.
                            block.setTowPlc() # sets it so that the block knows a tower has been placed there so another can't be.
                            Admin.SetPT() # resets the place time delay
                            break # breaks out of the loop.
                        if ActType == 2:
                            Admin.TakeMoney(60)
                            Xco = block.getX() # gets the x coordinate of the placement block
                            Yco = block.getY() # gets the y coordinate of the placement block
                            print(Xco,Yco)
                            TowerNum += 1 #  adds 1 to a count variable for the no. of towers so a name can be assigned to each --> e.g. 'Tower1' 
                            # sets all towers already placed, to have a selected variable of False.
                            for tower1 in towergroup: # loops through all the towers in the tower group.
                                tower1.setSelectedF() # sets the selected variable to false
                    
                            tower = Tower(ActType, Xco, Yco, str(TowerNum))# instanciates an object of the tower class to be placed on a tower block.
                            towergroup.add(tower) # adds the placed tower to the tower group.
                            all_sprites_group.add(tower) # adds the placed tower to the group of all sprites.
                            block.setTowPlc() # sets it so that the block knows a tower has been placed there so another can't be.
                            Admin.SetPT() # resets the place time delay
                            break # breaks out of the loop.
                        
                ### Checks whether a tower has been clicked to select/deselect it. ###
                for tower in towergroup: # loops through all the placed towers in the tower group
                    Tx = tower.getX() # gets the x coordiante of each tower
                    Ty = tower.getY() # gets the y coordinate of each tower
                    pos = pygame.mouse.get_pos() # gets the position of the mouse
                    ### code to deselect a tower onscreen. ###
                    if tower.getSelected() == True and Admin.GetPT() == 1: # checks if the tower has already been selected
                        if (pos[0] >= Tx and pos[1] >= Ty) and (pos[0] <= (Tx + 50) and pos[1] <= (Ty + 50)): # checks if the mouse position is within the boundaries of a placement block
                            tower.setSelectedF() # calls the false selected function to set the selected attribute to False
                            print(tower.getSelected())
                            UpgradeShop() # calls the function of the upgrade shop to appear when a tower is selected
                            break # breaks out of the if statement the code is in to avoid a constant loop of setting the value to false then true.

                    ### code to select a tower onscreen. ###
                    if tower.getSelected() == False and Admin.GetPT() == 1: # checks if the tower has not been selected already
                        if (pos[0] >= Tx and pos[1] >= Ty) and (pos[0] <= (Tx + 50) and pos[1] <= (Ty + 50)): # checks if the mouse position is within the boundaries of a placement block
                            ### sets the selected attribute to false for all towers before reselecting the clicked tower so an already selected tower will be deselected. ###
                            for tower2nd in towergroup: # loops through all the towers in the tower group
                                tower2nd.setSelectedF() # sets the towers selection attribute to false.
                            tower.setSelectedT() # calls the selected function to set the selected attribute to True
                            print(tower.getSelected())
                            UpgradeShop() # calls the function of the upgrade shop to appear when a tower is selected
                            break # isn't needed as this is the last statement the interpreter goes through but there just in case.
                       
        gameDisplay.fill(GRAY) # sets the colour of the background to grey
        gameDisplay.blit(Bg,(0,0)) # blits the background picture onto the window when the gameloop is in process.

        largeText = pygame.font.SysFont("tahoma",40)
        
        all_sprites_group.update() # calls an update on all sprites onscreen to keep up with any changes to their positions ect.
        all_sprites_group.draw(gameDisplay) # redraws all the sprites on the screen to show the changes made through the update.
        bulletgroup.draw(gameDisplay)

        if Admin.get_health() <= 0:
            Fate = "lose"
            pygame.draw.rect(gameDisplay, GRAY, (200,200,400,200), border_radius = 30)
            largeText = pygame.font.SysFont("tahoma",70)
            TextSurf, TextRect = text_objects("You Lose!", largeText)
            TextRect.center = ((400),(300))
            gameDisplay.blit(TextSurf, TextRect)
           

        Lmobs = Admin.GetMobSpawned()
        if Lmobs[9] == True:
            Fate = "win"
            pygame.draw.rect(gameDisplay, GRAY, (200,200,400,200), border_radius = 30)
            largeText = pygame.font.SysFont("tahoma",90)
            TextSurf, TextRect = text_objects("You Win!", largeText)
            TextRect.center = ((260),(572))
            gameDisplay.blit(TextSurf, TextRect)
        
        largeText = pygame.font.SysFont("tahoma",40)
            

        Admin.waves()

        for Mob in mob_group:
            Mob.End()
            Mob.checkHealth()
            Mob.drawP() # specific function to mobs which moves them along the set path.

        for tower in towergroup: # loops through all the towers in the tower group.
            tower.drawR(gameDisplay) # calls the public method in the tower class which draws the range of the towers onto the screen.
            tower.updateT(mob_group)
            if tower.getCooldown() < 300:
                tower.ChangeCooldown()

        Shop_group.draw(gameDisplay)

        for tower in towergroup:
            if tower.getSelected() == True:
                if tower.getRngLvl() == 5:
                    SelRngLvl = "lvl 5: Max"
                else:
                    SelRngLvl = "lvl " + str(tower.getRngLvl()) + ": $" + str(60 + (tower.getRngLvl() * 60))
                SelDmgLvl = " lvl " + str(tower.getDmgLvl()) + ": $" + str(30 + (tower.getDmgLvl() * 30))

        #button(msg,x,y,w,h,ic,ac,action=None)   ### format for creating a button ###
        button("Main Menu",0,550,100,50,GRAY,BUTTON_HOVER,main_menu) # main menu button on the screen.
        button("Quit",700,550,100,50,GRAY,BUTTON_HOVER,quitgame) # quit button on the screen.
        button("Shop",0,0,100,50,GRAY,BUTTON_HOVER,Shop) # show button on the screen.
        button("Tower 1: $50",Bx1,By1,Bw1,Bh1,GRAY,BUTTON_HOVER,Tw1) # tower 1 button which appears when the shop is opened.
        button("Tower 2: $60",Bx2,By2,Bw2,Bh2,GRAY,BUTTON_HOVER,Tw2) # tower 2 button which appears when the shop is opened.
        button("Upgrade Damage " + str(SelDmgLvl),UBx1, UBy1, UBw1, UBh1, GRAY, BUTTON_HOVER,UpgradeDmg)
        button("Tower Range " + str(SelRngLvl), UBx2, UBy2, UBw2, UBh2, GRAY, BUTTON_HOVER, UpgradeRng)
        TextSurf, TextRect = text_objects(str(Ts), largeText) # shows which type of tower is selected whilst the shop is open.
        TextRect.center = ((TSx),(TSy))
        gameDisplay.blit(TextSurf, TextRect)

        # Displays text showing the amount of health the player has.
        TextSurf, TextRect = text_objects("Health: " + str(Admin.get_health()), largeText)
        TextRect.center = ((260),(572))
        gameDisplay.blit(TextSurf, TextRect)

        # Displays text showing the amount of money the player has.
        TextSurf, TextRect = text_objects("Money: $" + str(Admin.getMoney()), largeText)
        TextRect.center = ((550),(572))
        gameDisplay.blit(TextSurf, TextRect)

        
        pygame.display.update() # updates the whole window.


        if Op1 or Op2: # controls a time delay between clicks on buttons.
            if ShopScreen.GetTime() > 0:
                ShopScreen.ChangeTime() # takes 1 from the time count for a delay when the shop button is clicked.
            if ShopScreen.GetTime() == 0:
                ShopScreen.setTime() # resets the count of the time delay between clicks on the shop button.
                Op1 = False # resets the operation flag variables to false
                Op2 = False

        if Cl1 or Cl2: # controls a time delay between clicks on buttons.
            if Admin.GetTime() > 0:
                Admin.ChangeTime() # takes 1 from the count button for time delays on button clicks.
            if Admin.GetTime() == 0:
                Admin.setTime() # resets the count for time delay between clicks.
                Cl1 = False
                Cl2 = False

        if Cl21 or Cl22: # controls a time delay between clicks on buttons.
            if Admin.GetTime() > 0:
                Admin.ChangeTime() # takes 1 from the count button for time delays on button clicks.
            if Admin.GetTime() == 0:
                Admin.setTime() # resets the count for time delay between clicks.
                Cl21 = False
                Cl22 = False
        
        if Admin.GetPT() < 1: # controls the time delay between placing towers.
            Admin.ChangePT()
            
        clock.tick(FPS) # sets the refresh rate of the program.
        if ActType == 0: # changes the text of tower selection in the shop based on what tower type has been selected.
            Ts = "None Selected" # no tower selected.
        if ActType == 1:
            Ts = "Tower 1" # tower 1 selected.
        if ActType == 2:
            Ts = "Tower 2" # tower 2 seletced.
        
        if B1Cooldown < 10:
            B1Cooldown +=1
        if B2Cooldown <10:
            B2Cooldown += 1
        
        if Admin.getStartDelay() < 1200:
            Admin.changeStartDelay()

        if Admin.getWaveDelay() < 900:
            Admin.ChangeWaveDelay()

        for bullet in bulletgroup: # loops through all the bullets in the bulet group.
            bullet.update() # calls the update method for bullets which moves them on screen.
            bullet.deleteB() # calls the delete method for bullets which 'kills' them when they go past the dimensions of the game window.
        
        bulletgroup.draw(gameDisplay) # draws all sprites in the bullet group onto the game window.

        if Admin.get_health() <= 0:
            EndGame()
        if Fate == "win":
            EndGame()



def EndGame():
    global intro, play, EndL, Fate
    play = False
    intro = False
    EndL = True
    while EndL:
        for event in pygame.event.get():
            # Quits the program when the window is closed.
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        largeText = pygame.font.SysFont("tahoma",40)        
        gameDisplay.fill(GRAY)
        if Fate == "win":
            TextSurf, TextRect = text_objects("You Win!", largeText)
        else:
            TextSurf, TextRect = text_objects("You Lose!", largeText)
        TextRect.center = ((260),(572))
        gameDisplay.blit(TextSurf, TextRect)
        pygame.display.update()
        button("Quit",700,550,100,50,GRAY,BUTTON_HOVER,quitgame) # quit button on the screen.
            
# Stops the code running when the quit button is clicked.

def quitgame():
    pygame.quit()
    quit()

main_menu()
game_loop()
EndGame()
