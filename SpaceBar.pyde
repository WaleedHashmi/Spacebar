add_library('sound')
import os,random
path = os.getcwd()

class Game:
    def __init__(self, w, h):
        self.state = "start"
        self.w = w
        self.h = h
        self.apollo = Ship("/red0.png", "/red1.png")
        self.apolloDisplayCount = 0
        self.fireList = []
        self.laserList = []
        self.f1 = Fire(self.apollo.x + self.apollo.r, self.apollo.y)
        self.l1 = Laser(self.apollo.x + self.apollo.r, self.apollo.y)
        self.laserPadding = 20  # distance between 2 consecutive lasers
        self.firePadding = 50  # distance between 2 consecutive fire balls
        # size = 1208 x 6301
        self.bg0 = BackgroundLayer(loadImage(path + "/bg0.png"), 1, 6301)
        # size = 1280 x 3333
        self.bg1 = BackgroundLayer(loadImage(path + "/bg0.png"), 1, 3333)
        self.randBG = 25
        self.BG_animate = "up"
        self.frameImage = loadImage(path + "/frame.png")
        self.scoreBoardImage = loadImage(path + "/scoreboard.png")
        self.killedImage = loadImage(path + "/killed.png")
        self.howToImage = loadImage(path + "/howto.png")
        self.winImage = loadImage(path + "/win.png")
        ##sounds
        self.sound_collision = SoundFile(this,path+'/Collision.wav')
        self.sound_fire = SoundFile(this,path+'/Fire.wav')
        self.sound_laser = SoundFile(this,path+'/Laser.wav')
        self.sound_defeat = SoundFile(this,path+'/GameLost.wav')
        self.sound_destroy  = SoundFile(this,path+'/DestroyingShip.wav')
        self.sound_bg = SoundFile(this,path+'/Soundtrack.mp3')
        
                
        self.staticEnemyList = []
        for i in range(15):  # max negative element = -40*300 -200 = -11800
            self.staticEnemyList.append(
                staticEnemy("stone", random.randint(100, 1200), -i * 300))
            self.staticEnemyList.append(
                staticEnemy("stone", random.randint(100, 1200), -i * 300 - 200))
            self.staticEnemyList.append(
                staticEnemy("rock", random.randint(100, 1200), -i * 300 - 100))
            
        self.collectibleList = []
        for i in range(2):  # max negative element = -10*3000 + 500 = -14500
            self.collectibleList.append(
                Collectible("shield", random.randint(100, 1200), -i * 3000 - 500))
            self.collectibleList.append(
                Collectible("life", random.randint(100, 1200), -i * 3000 - 1500))
            self.collectibleList.append(
                Collectible("fire", random.randint(100, 1200), -i * 3000 - 2500))

        self.spaceBar = Destination(
            loadImage(path + "/spacebar.png"), Width / 2 - 300, -5500)
    
    def backgroundDisplay(self):
        if self.bg0.y <= Height:
            self.bg0.y = 6301 - Height
            image(self.bg0.img, 0, Height - self.bg0.y)
        else:
            image(self.bg0.img, 0, Height - self.bg0.y)
            self.bg0.y -= self.bg0.v
       
    def display(self):
        
        self.scoreBoard()
        
        self.bombDisposal()  # to remove off-screen bombs
        
        self.collectingPowerUps()
        
        # print (len(self.collectibleList))
    
        self.spaceBar.update()
        self.spaceBar.display()
        
        for enemy in self.staticEnemyList:
            enemy.update()
            enemy.display()
        
        for collectible in self.collectibleList:
            collectible.update()
            collectible.display()
            
        for fireInstance in self.fireList:
            fireInstance.update()
            fireInstance.display()
            
        for laserInstance in self.laserList:
            laserInstance.update()
            laserInstance.display()
        
        self.apolloDisplayCount += 0.25
        print self.apolloDisplayCount
        if (self.apolloDisplayCount // 1) % 2 == 1:
            self.apollo.display(0)
        else:
            self.apollo.display(1)
        
        if self.apollo.health <= 0:
            self.state = "killed"            
            self.sound_defeat.play()
        if self.apollo.y < self.spaceBar.y + 300:
            self.state = "win"

    def scoreBoard(self):
        health = str(self.apollo.health / 10) + "%"
        image(self.scoreBoardImage, 0, Height - 200)
        textSize(40)
        textAlign(CENTER, TOP)
        text(health, 110, 577)
        text(self.apollo.ammo, 110, 577 + 74)

    # reduces health of enemy objects when they are hit by laser or fire
    def healthUpdate(self):
        for enemy in self.staticEnemyList:
            for fireInstance in self.fireList:
                if (fireInstance.y - fireInstance.r <= enemy.y + enemy.r / 2) and (enemy.x - enemy.r / 2 <= fireInstance.x <= enemy.x + enemy.r / 2):
                    self.fireList.remove(fireInstance)
                    enemy.health -= fireInstance.power
            for laserInstance in self.laserList:
                if (laserInstance.y - laserInstance.r / 2 <= enemy.y + enemy.r / 2) and (enemy.x - enemy.r / 2 <= laserInstance.x <= enemy.x + enemy.r / 2):
                    self.laserList.remove(laserInstance)
                    enemy.health -= laserInstance.power
            if enemy.y >= Height:
                self.apollo.health -= 200
                self.staticEnemyList.remove(enemy)
            if enemy.health <= 0:
                self.staticEnemyList.remove(enemy)
                self.sound_destroy.play()

    def collectingPowerUps(self):
        for collectible in self.collectibleList:
            if ((collectible.x - (self.apollo.x + self.apollo.r)) ** 2 + (collectible.y - (self.apollo.y + self.apollo.r)) ** 2) ** 0.5 < (self.apollo.r + collectible.r / 2):
                if collectible.type == "fire":
                    self.apollo.ammo += 1
                elif collectible.type == "life":
                    self.apollo.health += 100
                elif collectible.type == "shield":
                    self.apollo.shield = True
                self.collectibleList.remove(collectible)
                
    def collisionUpdate(self):
        for enemy in self.staticEnemyList:
            if ((enemy.x - (self.apollo.x + self.apollo.r)) ** 2 + (enemy.y - (self.apollo.y + self.apollo.r)) ** 2) ** 0.5 < (self.apollo.r + enemy.r / 2):
                if not self.apollo.shield:
                    self.apollo.health -= enemy.health
                else:
                    self.apollo.shield = False
                self.staticEnemyList.remove(enemy)
                self.sound_collision.play()

        
    def update(self):
        self.healthUpdate()
        self.collisionUpdate()
        
        if self.apollo.keyHandler[LEFT] == True and self.apollo.x > 0:
            self.apollo.x -=15
             
        if self.apollo.keyHandler[RIGHT] == True and self.apollo.x < 1080:
            self.apollo.x +=15
            
        if self.apollo.keyHandler["SPACE"] == True and self.laserClearance() :
            self.laserList.append(Laser(self.apollo.x + self.apollo.r - 23, self.apollo.y))
            self.laserList.append(Laser(self.apollo.x + self.apollo.r + 23, self.apollo.y))
            self.sound_laser.play()

            
        if self.apollo.keyHandler[UP] == True and self.fireClearance() and self.apollo.ammo > 0:
            self.fireList.append(Fire(self.apollo.x + self.apollo.r, self.apollo.y))
            self.apollo.ammo -=1
            self.sound_fire.play()
            
    def laserClearance(self): 
        for laser in self.laserList:
            if (self.apollo.y + laser.negativePadding - 7*laser.r)  - self.laserPadding <= laser.y <= (self.apollo.y + laser.negativePadding) :
                return False 
        return True 
    
    def fireClearance(self): 
        for fire in self.fireList:
            if self.apollo.y - 2*fire .r - self.firePadding <= fire.y <= self.apollo.y :
                return False 
        return True 
    
    def bombDisposal(self): #when a lazer or bomb goes off screen this function will delete it. 
        for laser in self.laserList:
            if laser.y + 7*laser.r < 0:
                newGame.laserList.remove(laser) 

    def mainMenu(self):
        background (self.randBG,self.randBG,self.randBG)
        
        if self.BG_animate == "up":
            self.randBG += .5
        elif self.BG_animate == "down":
            self.randBG -= .5
            
        if self.randBG == 65:
           self.BG_animate = "down"
        elif self.randBG == 25:
           self.BG_animate = "up" 
           
        image (self.frameImage,(Width - 400)/2, (Height - 400)/2,400,400)
        
        image (self.frameImage,(Width - 700)/2, (Height - 700)/2,700,700, 1000,1000,0,0)

        textSize (25)
        textAlign(CENTER)
        fill (255,255,255)
        text ("S  P  A  C  E  B  A  R",Width/2 ,Height/2)
        textSize (20)

        if Width/2 -40 <= mouseX <= Width/2 -40 + 80 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 20:
            fill (255,255,255,80)
        else:
            fill (255,255,255)
        text ("Play Now",Width/2 ,Height/2 + 110)
        if Width/2 -50 <= mouseX <= Width/2 -50 + 100 and Height/2 + 92 + 35 <= mouseY<= Height/2 + 92 + 35 + 20:
            fill (255,255,255,80)
        else:
            fill (255,255,255)
        text ("How to play",Width/2 ,Height/2 + 145)
        
    def killScreen(self):
        image (newGame.killedImage,0,0)
        textSize (20)
        textAlign(CENTER)
        if Width/2 -40 - 60<= mouseX <= Width/2 -40 + 80 + 60 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 20:
            fill (255,255,255,80)
        else:
            fill (255,255,255)
        text ("Back to Main Menu",Width/2 ,Height/2 + 110)
        fill (255,255,255)
        
    def winScreen(self):
        image (newGame.winImage,0,0)
        textSize (20)
        textAlign(CENTER)
        if Width/2 -40 - 60<= mouseX <= Width/2 -40 + 80 + 60 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 20:
            fill (255,255,255,80)
        else:
            fill (255,255,255)
        text ("Back to Main Menu",Width/2 ,Height/2 + 110)
        fill (255,255,255)
        
    def howToScreen(self):
        image (newGame.howToImage,0,0)
        textSize (25)
        textAlign(CENTER)
        if 200 -40 - 60<= mouseX <= 200 -40 + 80 + 60 and Height/1.25 + 92 <= mouseY<= Height/1.25 + 92 + 20:
            fill (255,255,255,80)
        else:
            fill (255,255,255)
        text ("Play Now",200,Height/1.25 + 110)
        fill (255,255,255)

        
        
           
           
                
class BackgroundLayer:
    def __init__ (self,img,v,h):
        self.img = img
        self.v = v
        self.y = h
             
class Ship: 
    def __init__ (self,img0,img1):
        self.img0 = loadImage (path + img0)
        self.img1 = loadImage (path + img1)
        self.shieldImg = loadImage(path + "/shield.png")
        self.r = 100
        self.x = Width/2 - self.r
        self.y = Height - 2*self.r
        self.padding = 5
        self.keyHandler={LEFT:False,RIGHT:False,"SPACE":False,UP:False}
        self.shield = False
        self.secondGun = False
        self.health = 1000
        self.ammo = 20
    
    def display (self, n):
        if n==0:
            img = self.img0
        else:
            img = self.img1
        image (img, self.x, self.y, 2*self.r,2*self.r)
        if self.shield:
            image (self.shieldImg, self.x, self.y, 2*self.r,2*self.r) 
        
class Fire:
    def __init__(self,x,y): 
        self.x = x
        self.y = y 
        self.r = 15
        self.v = 15
        self.img = loadImage(path + "/fire.png")
        self.power = 1000
        
    def display (self):
        image(self.img,self.x - self.r, self.y - self.r*2,self.r*2,self.r*2)
        
    def update (self):
        self.y -= self.v
        
class Laser:
    def __init__(self,x,y): 
        self.x = x #center coodrinates 
        self.y = y 
        self.v = 10 
        self.r = 4
        self.negativePadding = 5
        self.img = loadImage(path + "/laser.png")
        self.power = 40  
        
    def display (self):
        image(self.img,self.x - self.r/2, self.y + self.negativePadding,self.r,self.r*7)
        
    def update (self):
        self.y -= self.v

class staticEnemy:
    def __init__ (self,type,x,y):
        if type == "stone":
            self.img = loadImage(path + "/stone.png")
            self.health = 100
            self.r = 60
        if type == "rock":
            self.img = loadImage(path + "/rock.png")
            self.health = 200
            self.r = 100
        self.v = 2
        self.x = x
        self.y = y
        
    def display(self):
        noFill()
        # ellipse(self.x,self.y,self.r,self.r)
        image(self.img, self.x - self.r/2, self.y - self.r/2, self.r,self.r)
    
    def update(self):
        self.y += self.v     

class Collectible: 
    def __init__ (self,type,x,y):
        self.type = type
        if type == "life":
            self.img = loadImage(path + "/lifeIcon.png")
        if type == "fire":
            self.img = loadImage(path + "/fireIcon.png")
        if type == "shield":
            self.img = loadImage(path + "/shieldIcon.png")        
        self.x = x
        self.y = y
        self.r = 50
        self.v = 2
                
    def display(self):
        image(self.img, self.x - self.r/2, self.y - self.r/2, self.r,self.r)
    
    def update(self):
        self.y += self.v     
        
class Destination: 
    def __init__ (self,img,x,y):
        self.img = img
        self.x = x
        self.y = y
        self.v = 2
        
    def display(self):
        image(self.img, self.x, self.y, 600,600)
    
    def update(self):
        self.y += self.v 

        
                            
Height = 720
Width = 1280
newGame = Game(Width,Height)

def setup():
    size(newGame.w, newGame.h)
    frameRate (120)
    global newFont
    newFont =  createFont("GeosansLight.ttf",32)
    newGame.sound_bg.play()
    
def draw():
    background (0,0,0)
    if newGame.state == "start":
        textFont(newFont)
        newGame.mainMenu()
    elif newGame.state == "play":
        newGame.backgroundDisplay()
        newGame.update()
        newGame.display()
    elif newGame.state == "killed":
        newGame.killScreen()
    elif newGame.state == "howTo":
        newGame.howToScreen()
    elif newGame.state == "win":
        newGame.winScreen()
    
        
        
        
        
def keyPressed():
    if keyCode == LEFT:
        newGame.apollo.keyHandler[LEFT]=True
    elif keyCode == RIGHT:
        newGame.apollo.keyHandler[RIGHT]=True
    elif keyCode == 32: #space bar
        newGame.apollo.keyHandler["SPACE"]=True
    elif keyCode == UP:
        newGame.apollo.keyHandler[UP]=True

def keyReleased():
    if keyCode == LEFT:
        newGame.apollo.keyHandler[LEFT]=False
    elif keyCode == RIGHT:
        newGame.apollo.keyHandler[RIGHT]=False
    elif keyCode == 32: #space bar
        newGame.apollo.keyHandler["SPACE"]=False
    elif keyCode == UP:
        newGame.apollo.keyHandler[UP]=False
        
def mouseClicked():
    global newGame
    if Width/2 -40 <= mouseX <= Width/2 -40 + 80 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 20 and newGame.state == "start":
        newGame.state = "play"
    if Width/2 -50 <= mouseX <= Width/2 -50 + 100 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 35 + 20 and newGame.state == "start":
        newGame.state = "howTo"
    if Width/2 -40 - 60<= mouseX <= Width/2 -40 + 80 + 60 and Height/2 + 92 <= mouseY<= Height/2 + 92 + 20 and (newGame.state == "killed" or newGame.state == "win"):
        newGame = Game(Width,Height)
        newGame.state = "start"
    if 200 -40 - 60<= mouseX <= 200 -40 + 80 + 60 and Height/1.25 + 92 <= mouseY<= Height/1.25 + 92 + 20 and newGame.state == "howTo":
        newGame.state = "play"


    