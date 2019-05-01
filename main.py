# Welcome to Python on Pokitto!
import upygame as pygame
import umachine
import urandom
import assets


pygame.display.init()
pygame.display.set_palette_16bit([
    0, 6438, 18917, 10825, 47398, 688, 41764, 17475,
    58225, 13598, 60486, 40179, 42596, 46845, 63245, 65535
]);

# Initialize sound
g_sound = pygame.mixer.Sound()
g_sound.play_from_sd("ufointro.snd")


screen = pygame.display.set_mode() # full screen
back_sf = pygame.surface.Surface(110, 88, assets.backgroundPixels)
gun_sf = pygame.surface.Surface(8, 8, assets.gunPixels)
gunRect = pygame.Rect(54,43,2,1)
arrow1_sf = pygame.surface.Surface(10,10,assets.ArrowPixels1)
arrow2_sf = pygame.surface.Surface(10,10,assets.ArrowPixels2)
arrow3_sf = pygame.surface.Surface(10,10,assets.ArrowPixels3)
arrow4_sf = pygame.surface.Surface(10,10,assets.ArrowPixels4)

timeIndicator_sf = pygame.surface.Surface(16,12,assets.timeIndicatorPixels)
robot_sf1 = pygame.surface.Surface(18, 19, assets.robotPixels1)
robot_sf2 = pygame.surface.Surface(18, 19, assets.robotPixels2)
robot_sf3 = pygame.surface.Surface(18, 19, assets.robotPixels3)
flyingsaucer_sf = pygame.surface.Surface(16, 16, assets.flyingSaucerPixels)
flyingsaucer_sf2 = pygame.surface.Surface(16, 16, assets.flyingSaucerPixels2)
flyingsaucer_sf3 = pygame.surface.Surface(16, 16, assets.flyingSaucerPixels3)
cockpit_sf = pygame.surface.Surface(110,12,assets.cockpitPixels)
cockpitright_sf = pygame.surface.Surface(110,24,assets.cockpitPixelsRight)
cockpitleft_sf = pygame.surface.Surface(110,24,assets.cockpitPixelsLeft)
laserleft_sf = pygame.surface.Surface(44,33,assets.laserLeftPixels)
laserright_sf = pygame.surface.Surface(44,33,assets.laserRightPixels)
explosion_sf1 = pygame.surface.Surface(16,16,assets.explosionPixels1)
explosion_sf2 = pygame.surface.Surface(16,16,assets.explosionPixels2)
explosion_sf3 = pygame.surface.Surface(16,16,assets.explosionPixels3)
explosion_sf4 = pygame.surface.Surface(16,16,assets.explosionPixels4)
rock_sf = pygame.surface.Surface(16,16,assets.rockPixels)
rect1_sf= pygame.surface.Surface(2,1,assets.rect1Pixels)
moon = pygame.surface.Surface(26, 39, assets.moonPixels)
nebula = pygame.surface.Surface(64, 64, assets.nebulaPixels)
vx=0
vy=0
xufo =40
yufo =40
vxufo = 0
vyufo = 0
ufoType = 1 #1: Large 2:Medium 3: Small
ufoRect = pygame.Rect(xufo+4,yufo+7,10-4,14-7)
xrock = 55-8
yrock = 44-8
xnebula = 10
ynebula = 200
counter = 0;
#laser = 0;
laserleft = 1;
cockpitState =2; #1: left 2: center 3: right
xcoordint = [];
xcoordfrac = [];
ycoordint = [];
ycoordfrac = [];
startTime = umachine.time_ms()
remainingTime = 60;
gameState = 0;  #0: TitleScreen, 1:Play Game, 2:Game Over
explosionState = 0
robotcounter = 0
score = 0
currentUFOscore = 0

#Function to draw title screen (+initialize random generator)
def titleScreen():
    visible = 0
    #g_sound.play_from_sd("ufointro.snd")
    while True:
        urandom.getrandbits(30)
        eventtype = pygame.event.poll()
        if eventtype != pygame.NOEVENT and eventtype.type == pygame.KEYDOWN and eventtype.key == pygame.BUT_C:
            return
        screen.blit( back_sf, 0, 0 ) 
        drawText( 55 - 3*5, 40, "U.F.O.", 15, 5)
        if visible>8:
            umachine.draw_text(55-3*5,78,"Press C", 15)
        if visible == 16:
            visible = 0
        visible = visible + 1;
        pygame.display.flip()

#Initialize the position of the stars: xcoordint,ycoordint : integer part of the positon, xcoordfrac,ycoordfrac : fractional part        
def initializeStars():
    for i in range(20):
        xcoordint.append(urandom.getrandbits(7)%110)
        xcoordfrac.append(0)
        ycoordint.append(urandom.getrandbits(7)%88)
        ycoordfrac.append(0)
    return

#Update the position of the stars
def updateStarsPosition():
    for i in range(20):
        temp = ((xcoordint[i]-55)*110+xcoordfrac[i]*110//100 + 55*100)
        xcoordint[i] = temp//100
        xcoordfrac[i] = temp%100
        temp = ((ycoordint[i]-44)*110 + ycoordfrac[i]*110//100 + 44*100)
        ycoordint[i] = temp//100
        ycoordfrac[i] = temp%100
        
        
        if (xcoordint[i]<0 or xcoordint[i]>109) or (ycoordint[i]<0) or (ycoordint[i]>87):
            xcoordint[i] = urandom.getrandbits(7)%110
            xcoordfrac[i] = 0
            ycoordint[i] = urandom.getrandbits(7)%88
            ycoordfrac[i] = 0
    return

#Poll buttons
def pollButtons():
    global vx
    global vy
    global laserleft
    global explosionState
    global gameState
    global cockpitState
    eventtype = pygame.event.poll()
    if eventtype != pygame.NOEVENT:
        if eventtype.type== pygame.KEYDOWN:
            if eventtype.key == pygame.K_RIGHT:
                vx = 1
                cockpitState = 3
            if eventtype.key == pygame.K_LEFT:
                vx = -1
                cockpitState = 1
            if eventtype.key == pygame.K_UP:
                vy = -1
            if eventtype.key == pygame.K_DOWN:
                vy = 1
            if eventtype.key == pygame.BUT_A:
                #laser = 1
                #if cockpitState == 2:
                    drawLaser()
                    g_sound.play_sfx(assets.laserSound, len(assets.laserSound), True)
                    if checkCollision() == True:
                        if explosionState ==0:
                            explosionState = 30
            if eventtype.key == pygame.BUT_B:
                gameState = 2
        if eventtype.type == pygame.KEYUP:
            if eventtype.key == pygame.K_RIGHT:
                vx = 0
                cockpitState = 2
            if eventtype.key == pygame.K_LEFT:
                vx = 0
                cockpitState = 2
            if eventtype.key == pygame.K_UP:
                vy = 0
            if eventtype.key == pygame.K_DOWN:
                vy = 0
    return

#Draw text with background and foreground colors
def drawText(xpos, ypos, textstring, foregroundcolor, backgroundcolor):
    umachine.draw_text( xpos - 1, ypos, textstring, backgroundcolor)
    umachine.draw_text( xpos + 1, ypos, textstring, backgroundcolor)
    umachine.draw_text( xpos, ypos - 1, textstring, backgroundcolor)
    umachine.draw_text( xpos, ypos + 1, textstring, backgroundcolor)
    umachine.draw_text( xpos, ypos, textstring, foregroundcolor)
    return

#Draw the stars
def drawStars():
    for i in range(1,20):
        screen.blit(rect1_sf, xcoordint[i-1], ycoordint[i-1])
    return

def drawNebula():
    global xnebula
    global ynebula
    xnebula = (xnebula - vx)%220 
    ynebula = (ynebula - vy)%176 
    screen.blit(nebula,xnebula - 110,ynebula - 88)
    screen.blit(moon,(xnebula -110)%220 - 110,(ynebula - 88)%176 - 88)
    return

#Initialize the UFO: type + position + velocity
def initializeUFO():
    global xufo
    global yufo
    global vxufo
    global vyufo
    global ufoType
    global currentUFOscore
    xufo = urandom.getrandbits(7)%110
    yufo = urandom.getrandbits(7)%88
    vxufo = urandom.getrandbits(1)*2-1
    vyufo = urandom.getrandbits(1)*2-1
    ufoType = urandom.getrandbits(2)%3+1
    if ufoType == 1:
        ufoRect.x = xufo + 5
        ufoRect.y = yufo + 7
        ufoRect.width = 10-5+1
        ufoRect.height = 14-7
    elif ufoType == 2:
        ufoRect.x = xufo + 6
        ufoRect.y = yufo + 10
        ufoRect.width = 9-6+1
        ufoRect.height = 13-10
    else:
        ufoRect.x = xufo + 7
        ufoRect.y = yufo + 10
        ufoRect.width = 8-7+1
        ufoRect.height = 11-10
    currentUFOscore = 10*ufoType
    return

#Draw UFO
def drawUFO():
    if ufoType == 1: 
        screen.blit(flyingsaucer_sf,xufo,yufo)
    elif ufoType == 2:
        screen.blit(flyingsaucer_sf2,xufo,yufo)
    else:
        screen.blit(flyingsaucer_sf3,xufo,yufo)
    #screen.fill(4,ufoRect)
    return

#Update position of UFO
def updateUFOPosition():
    global xufo
    global yufo
    global vxufo
    global vyufo
    global counter
    if counter ==4 :
        xufo = xufo + vxufo
        yufo = yufo + vyufo
        ufoRect.x =ufoRect.x + vxufo
        ufoRect.y =ufoRect.y + vyufo
        counter = 0
    counter = counter + 1
    xufo = (xufo - vx)
    yufo = (yufo - vy)
    ufoRect.x =ufoRect.x - vx
    ufoRect.y =ufoRect.y - vy
    return

#Draw Laser animation
def drawLaser():
    global laserleft
    if (laserleft >0):
        screen.blit(laserleft_sf,12,45)
    else:
        screen.blit(laserright_sf,97-43,45)
    laserleft = laserleft*(-1)
    return

#Check if UFO collides with gun
def checkCollision():
    return ufoRect.colliderect(gunRect)

#Draw an animated explosion
def drawExplosion():
    global explosionState
    global score
    if explosionState>24:
        explosionState = explosionState - 1
    elif explosionState>18:
        screen.blit(explosion_sf1,54-7,43-7)
        explosionState = explosionState - 1
    elif explosionState>12:
        screen.blit(explosion_sf2,54-7,43-7)
        explosionState = explosionState - 1
    elif explosionState>6:
        screen.blit(explosion_sf3,54-7,43-7)
        explosionState = explosionState - 1
    else :
        screen.blit(explosion_sf4,54-7,43-7)
        explosionState = explosionState - 1
        if explosionState == 0:
            score = score + currentUFOscore
            initializeUFO()
    return

#Draw the player Ship
def drawPlayerShip():
    if cockpitState==1:
        screen.blit(cockpitleft_sf,0,64)
    elif cockpitState==3:
        screen.blit(cockpitright_sf,0,64)
    else:
        screen.blit(cockpit_sf,0,76)
    screen.blit(gun_sf, 54-3, 43-3)
    if (ufoRect.x+ufoRect.width//2)<55:
        if (ufoRect.y+ufoRect.height//2)<44:
            screen.blit(arrow1_sf,4,4)
        else:
            screen.blit(arrow4_sf,4,4)
    else:
        if (ufoRect.y+ufoRect.height//2)<44:
            screen.blit(arrow2_sf,4,4)
        else:
            screen.blit(arrow3_sf,4,4)
    return

#Draw Game Over Screen
def drawRobot():
    global robotcounter
    global counter
    global gameState
    
    robotState = robotcounter%4
    if robotState==0:
        screen.blit(robot_sf1,10,10)
    elif robotState==1:
        screen.blit(robot_sf2,10,10)
    elif robotState==2:
        screen.blit(robot_sf1,10,10)
    else:
        screen.blit(robot_sf3,10,10)
    if counter == 4:
        robotcounter = robotcounter + 1
        counter = 0
    
    counter = counter + 1
    scorestr = (5-len(str(score)))*"0"+str(score)
    drawText(55 -2*5, 10, scorestr, 15, 5)
    drawText(55 -4*5, 54, "Game Over", 15, 5)
    eventtype = pygame.event.poll()
    if eventtype != pygame.NOEVENT and eventtype.type == pygame.KEYDOWN and eventtype.key == pygame.BUT_C:
        gameState = 0
    return

#Main game loop
while True:
    if gameState == 0: #Show title screen and initialze the game
        titleScreen()
        initializeStars()
        initializeUFO()
        startTime=umachine.time_ms()
        remainingTime = 120
        score = 0
        gameState = 1
    elif gameState == 1: #Play the game
        if (umachine.time_ms()-startTime)>=1000:
            remainingTime = remainingTime -1;
            startTime=umachine.time_ms()
        if remainingTime == 0:
            gameState = 2
        screen.blit(timeIndicator_sf,40,1)
        umachine.draw_text(55-1*5,2,str(remainingTime),15)
        drawNebula()
        updateStarsPosition()
        drawStars()
        drawUFO()
        if explosionState>0:
            drawExplosion()
        else:
            updateUFOPosition()
            
        pollButtons()
        drawPlayerShip()
        screen.fill(14,gunRect)
    elif gameState == 2: #Game Over
        drawRobot()
    
    pygame.display.flip()