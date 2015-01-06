import pygame, random, sys, time
from pygame.locals import *
from math import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480


BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)

BGCOLOR = BLACK

TOPLEFT = 7
TOPRIGHT = 9
BOTTOMLEFT = 1
BOTTOMRIGHT = 3


def main():
    global FPSCLOCK,playerspeed,DISPLAYSURF,shotspeed,asteroidspeed
    playerx,playery = WINDOWWIDTH/2,WINDOWHEIGHT/2
    clockwise,anticlockwise,forward,shots = False,False,False,False
    degree = 0.00000001 # instead of 0 to fix the initial stuck and static shots bug

    playerspeed = 0
    score = 0
    shotspeed = 10
    asteroidspeed = [4,3,1]
    asteroidsize = [30,40,50]
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    pygame.display.set_caption('Interstellar!')
    surfaceobj,rectobj = drawText('INTERSTELLAR',WHITE,'Agency FB',48,WINDOWWIDTH/2-10,WINDOWHEIGHT/2-10)
    DISPLAYSURF.blit(surfaceobj,rectobj)
    surfaceobj,rectobj = drawText('Press any key to continue to game..',WHITE,'Agency FB',24,WINDOWWIDTH/2,WINDOWHEIGHT/2+40)
    DISPLAYSURF.blit(surfaceobj,rectobj)
    pygame.display.update()

    waitforinput()

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    pygame.display.set_caption('Interstellar')
    playerRect = pygame.Rect(WINDOWWIDTH/2-40,WINDOWHEIGHT/2,25,25)
    playerImage = pygame.image.load('player1.png')
    playerRect.center = (playerx,playery)
    shotsound = pygame.mixer.Sound('badswap.wav')
    totalshots = []
    asteroids = []
    check = time.time()
    DISPLAYSURF.blit(playerImage,playerRect)
    motionangle,motiondirection = 0,1
    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                terminate()
            if event.type == KEYDOWN and event.key == K_SPACE:
                shots,maxshots = True,1
            if event.type == KEYUP and event.key == K_SPACE:
                shots = False
            if event.type == KEYDOWN and event.key == K_RIGHT:
                clockwise = True
                anticlockwise = False
            if event.type == KEYDOWN and event.key == K_LEFT:
                anticlockwise = True
                clockwise = False
            if event.type == KEYUP and event.key == K_RIGHT:
                clockwise = False
            if event.type == KEYUP and event.key == K_LEFT:
                anticlockwise = False
            if event.type == KEYDOWN and event.key == K_UP:
                forward = True
            if event.type == KEYUP and event.key == K_UP:
                forward = False
        if clockwise:
            increment = -8
        if anticlockwise:
            increment = 8
        if not (clockwise and anticlockwise and forward):
            rotatedplayer = pygame.transform.rotate(playerImage,degree)
            rotatedrect = rotatedplayer.get_rect()
            rotatedrect.center = (playerx,playery)
        if clockwise or anticlockwise:
            degree+=increment
            rotatedplayer = pygame.transform.rotate(playerImage,degree)
            rotatedrect = rotatedplayer.get_rect()
            rotatedrect.center = (playerx,playery)
        if forward:
            if playerx == WINDOWWIDTH/2 and playery == WINDOWHEIGHT/2:
                rotatedplayer = pygame.transform.rotate(playerImage,degree)
                rotatedrect = pygame.transform.rotate(playerImage,degree).get_rect()
                rotatedrect.center = (playerx,playery)
            if playerspeed:
                motionangle1,motiondirection1 = motionangle,motiondirection
                motionangle,motiondirection = getAngleDirection(degree)
                playerspeed,motionangle,motiondirection = getResultantspeed(motionangle1,motiondirection1,motionangle,motiondirection,playerspeed)
            else:
                motionangle,motiondirection = getAngleDirection(degree)
                playerspeed = 0.5
        playerx2,playery2 = moveEntity([motionangle,motiondirection,playerx,playery,playerspeed])
        playerx,playery = playerx2,playery2
        rotatedrect.center = (playerx,playery)
        if shots and maxshots:
            totalshots.append(createShot(playerx,playery,degree))
            maxshots = 0                   # maxshots variable is to make sure that only one shot is fired per one key stroke
        for shot in totalshots:
            centerx2,centery2 = updateShotPos(shot)
            shot[1].centerx, shot[1].centery = centerx2,centery2
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(rotatedplayer,rotatedrect)
        if len(asteroids)<10 and time.time()-check>=1.5:
            asteroids.append(makeAsteroids(random.choice(asteroidsize),x=None,y=None))
            check = time.time()
        for asteroid in asteroids:
            # datastructure - asteroid : [angle,direction,x,y,speed,asteroidSurf,asteroidRect]
            astx2,asty2 = moveEntity(asteroid[:5])
            asteroid[2],asteroid[3] = astx2,asty2
            asteroid[6].centerx,asteroid[6].centery = astx2,asty2
            DISPLAYSURF.blit(asteroid[5],asteroid[6])
        for shot in totalshots[:]:
            DISPLAYSURF.blit(shot[0],shot[1])
            # to remove out of bound shots... no teleporting here 
            if shot[1].centerx > WINDOWWIDTH or shot[1].centerx < 0 or shot[1].centery <0 or shot[1].centery> WINDOWHEIGHT:
                totalshots.remove(shot)
        for asteroid in asteroids[:]:
            for shot in totalshots[:]:
                # shot's data structure [projectileSurf,projectilRect, degree]
                if asteroid[6].colliderect(shot[1]):
                    if asteroid[6].height==50:
                        totalshots.remove(shot)
                        for i in range(3): #3 asteroid fragments seperate out
                            asteroids.append(makeAsteroids(30,asteroid[6].centerx,asteroid[6].centery)) 
                        asteroids.remove(asteroid)
                        score += 75
                        break
                    elif asteroid[6].height==40:
                        totalshots.remove(shot)
                        asteroids.append(makeAsteroids(30,asteroid[6].centerx,asteroid[6].centery))
                        asteroids.append(makeAsteroids(30,asteroid[6].centerx,asteroid[6].centery))
                        asteroids.remove(asteroid)
                        score += 75
                        break
                    totalshots.remove(shot)
                    asteroids.remove(asteroid)
                    score += 50
                    break
        updateScore(score)        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def getResultantspeed(motionangle1,motiondirection1,motionangle,motiondirection,playerspeed):
    #returns resultant playerspeed,motionangle,motiondirection
    # motionangle1, motiondirection1 are INITIAL values , motionangle ,motiondirection are along THRUST
    ux1,uy1 = getComponents(playerspeed,motiondirection1,motionangle1)
    ux2,uy2 = getComponents(0.5,motiondirection,motionangle) # single thrust == 0.5 increase in speed
    vx = ux1 + ux2
    vy = uy1 + uy2
    resultantspeed = sqrt(vx*vx + vy*vy)
    resultantangle = degrees(atan(abs(vy)/abs(vx)))
    if (vx>0 and vy>0) or (vx>0 and vy==0):
        resultantdirection = TOPRIGHT
    elif (vx>0 and vy<0) or (vx==0 and vy<0):
        resultantdirection = BOTTOMRIGHT
    elif (vx<0 and vy>0) or (vx==0 and vy>0):
        resultantdirection = TOPLEFT
    elif (vx<0 and vy<0) or (vx<0 and vy==0):
        resultantdirection = BOTTOMLEFT
    return resultantspeed,resultantangle,resultantdirection

def updateScore(score):
    scoreSurface,scoreRect = drawText("SCORE: "+str(score),WHITE,'Agency FB',16,WINDOWWIDTH-50,20)
    DISPLAYSURF.blit(scoreSurface,scoreRect)
def getComponents(speed,direction,angle):
    if direction == TOPRIGHT:
        x = speed*cos(radians(angle))
        y = speed*sin(radians(angle))
    elif direction == TOPLEFT:
        x = -speed*cos(radians(angle))
        y = speed*sin(radians(angle))
    elif direction == BOTTOMRIGHT:
        x = speed*cos(radians(angle))
        y = -speed*sin(radians(angle))
    elif direction == BOTTOMLEFT:
        x = -speed*cos(radians(angle))
        y = -speed*sin(radians(angle))
    return x,y

def makeAsteroids(asteroidsize,x,y):
    asteroidImage = pygame.image.load('block'+str(random.choice([1,2]))+'.png')
    asteroidSurf = pygame.transform.scale(asteroidImage,(asteroidsize,asteroidsize))
    asteroidRect = asteroidSurf.get_rect()
    edge = random.choice([1,2,3,4])
    if x == None and y == None:
        if edge == 1:
            x, y = 0, random.choice(range(WINDOWHEIGHT))
        elif edge ==2:
            x, y = random.choice(range(WINDOWWIDTH)),0
        elif edge == 3:
            x, y = WINDOWWIDTH, random.choice(range(WINDOWHEIGHT))
        else:
            x, y = random.choice(range(WINDOWWIDTH)), WINDOWHEIGHT
    asteroidRect.center = (x,y)
    angle = random.choice(range(1,90))
    # The following code is to make sure that the asteroid doesnt get stuck in a small "loop?" 
    if (y==0 and x>320) or (x==640 and y<240) or (x==0 and y>240) or (y==480 and x<320):
        direction = random.choice([1,9])
    elif (y==0 and x<320) or (x==0 and y<240) or (y>240 and x==640) or (x>320 and y==480):
        direction = random.choice([3,7])
    else:
        direction = random.choice([7,9,1,3])
    speed = random.choice(asteroidspeed)
    return [angle,direction,x,y,speed,asteroidSurf,asteroidRect]

def createShot(playerx,playery,degree):
    projectileImage = pygame.image.load('shot.png')
    projectileSurf = projectileImage
    projectileRect = projectileSurf.get_rect()
    projectileRect.center = (playerx,playery)
    return [projectileSurf,projectileRect,degree]
    

def updateShotPos(shot):
    # Returns next position of the shot aka projectile
    projectileSurf,projectileRect,degree = shot[0],shot[1],shot[2]
    angle, direction = getAngleDirection(degree)
    slope = tan(radians(angle))
    shotx = projectileRect.centerx
    shoty = projectileRect.centery
    shotspeedx = getspeed(angle,shotspeed)
    if direction == TOPRIGHT:
        shotx2 = shotx + shotspeedx
        shoty2 = shoty - slope*(shotx2-shotx)
    elif direction == BOTTOMRIGHT:
        shotx2 = shotx + shotspeedx
        shoty2 = shoty + slope*(shotx2-shotx)
    elif direction == TOPLEFT:
        shotx2 = shotx - shotspeedx
        shoty2 = shoty + slope*(shotx2-shotx)
    elif direction == BOTTOMLEFT:
        shotx2 = shotx - shotspeedx
        shoty2 = shoty - slope*(shotx2-shotx)
    elif degree%360==0:
        shoty2,shotx2 = shoty - shotspeedx, shotx
    return shotx2,shoty2
def moveEntity(entity):
    # returns the next position based on current position,orientation and speed also takes care of teleporting the entities from the edges
    """ handles the spacecraft's(and asteroids) movements and manoeuvers :everything fine no bugs
    if the craft would have been like the classic alien spacecraft this fn would have been around 20 lines because of symmetry """
    angle,direction,playerx,playery,Entityspeed = entity[0],entity[1],entity[2],entity[3],entity[4]
    speedx = getspeed(angle,Entityspeed)
    slope = tan(radians(angle))
    if direction == TOPRIGHT and speedx:
        playerx2 = playerx + speedx
        playery2 = (-slope*(playerx2-playerx)+playery)
        if playery2 <=0:                                #handling cases when other end can be on either left or bottom edges, edge collision and stuff like that
            playerx2 = -(WINDOWHEIGHT-playery)/slope+playerx
            if playerx2<0:
                playerx2,playery2=0,(playery+slope*playerx)
            else:
                playery2 = WINDOWHEIGHT
            return playerx2,playery2
        if playerx2 >=WINDOWWIDTH:
            playery2 = playery + slope*playerx
            if playery2>WINDOWHEIGHT:                                   #handling extra cases : other end at left or bottom edges
                playery2,playerx2 = WINDOWHEIGHT,(playerx-(WINDOWHEIGHT-playery)/slope)
            else:
                playerx2 = 0
        return playerx2,playery2
    if direction == BOTTOMRIGHT and speedx:
        playerx2 = playerx + speedx
        playery2 = (slope*(playerx2-playerx)+playery)
        if playerx2 >= WINDOWWIDTH:
            playery2 = playery - slope*playerx
            if playery2 <0:                                             #extra cases like above
                playery2,playerx2 = 0,(playerx-playery/slope)
            else:
                playerx2 = 0
            return playerx2,playery2
        if playery2 >= WINDOWHEIGHT:
            playerx2 = -(playery)/slope + playerx
            if playerx2 <0:
                playerx2,playery2 = 0,(playery-slope*playerx)
            else:
                playery2 = 0
        return playerx2,playery2
    if direction == BOTTOMLEFT and speedx:
        playerx2 = playerx - speedx
        playery2 = (slope*(speedx)+playery)
        if playerx2 <=0:
            playery2 = playery - slope*(WINDOWWIDTH-playerx)
            if playery2 < 0:
                playery2, playerx2 = 0, (playerx + playery/slope)
            else:
                playerx2 = WINDOWWIDTH
            return playerx2,playery2
        if playery2 >= WINDOWHEIGHT:
            playerx2 = playerx + (playery)/slope
            if playerx2 > WINDOWWIDTH:
                playerx2, playery2 = WINDOWWIDTH, (playery-slope*(WINDOWWIDTH-playerx))
            else:
                playery2 = 0
        return playerx2,playery2
    if direction == TOPLEFT and speedx:
        playerx2 = playerx - speedx
        playery2 = (-slope*(speedx)+playery)
        if playerx2 <=0:
            playery2 = playery + slope*(WINDOWWIDTH-playerx)
            if playery2 > WINDOWHEIGHT:
                playery2,playerx2 = WINDOWHEIGHT, (playerx + (WINDOWHEIGHT-playery)/slope)
            else:
                playerx2 = WINDOWWIDTH
            return playerx2,playery2
        if playery2 <=0:
            playerx2 = playerx + (WINDOWHEIGHT-playery)/slope
            if playerx2 > WINDOWWIDTH:
                playerx2,playery2 = WINDOWWIDTH, (playery + slope*(WINDOWWIDTH-playerx))
            else:
                playery2 = WINDOWHEIGHT
        return playerx2,playery2
    else:
         if direction in [TOPRIGHT,TOPLEFT]:
             playery2 = playery - playerspeed
             if playery2 <=0:
                 playery2 = WINDOWHEIGHT
             return playerx,playery2
         playery2 = playery+playerspeed
         if playery2 >= WINDOWHEIGHT:
             playery2 = 0 
         return playerx,playery2
        
def getspeed(angle,speed):
    speedx = cos(radians(angle))*speed
    return speedx
    

def getAngleDirection(rot):
    """ Returns angle wrt x axis(+ or - according to direction) and direction wrt origin. Note that the angle is always positive.
        so that a line can be plotted in y = mx + c. Here rot is the wrt to pygame.transform. """
    if rot<=0:
        rot = -rot%360
        if rot >0 and rot <=90:
            return 90-rot,TOPRIGHT
        elif rot > 90 and rot <=180:
            return rot-90,BOTTOMRIGHT
        elif rot > 180 and rot <=270:
            return 270-rot,BOTTOMLEFT
        else:
            return rot-270,TOPLEFT
    if rot >0:
        rot = rot%360
        if rot >0 and rot<=90:
            return 90-rot,TOPLEFT
        elif rot >90 and rot <=180:
            return rot-90,BOTTOMLEFT
        elif rot >180 and rot <=270:
            return 270-rot,BOTTOMRIGHT
        else:
            return rot-270,TOPRIGHT
def drawText(text,color,font,size,x,y):
    fontobj = pygame.font.SysFont(font, size)
    textSurfaceObj = fontobj.render(text, True, color, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (x, y)
    return (textSurfaceObj,textRectObj)

def drawplayer():
    player = pygame.Rect(WINDOWWIDTH/2-40,WINDOWHEIGHT/2,25,25)
    playerImage = pygame.image.load('player1.png')
    DISPLAYSURF.blit(playerImage,player)
def waitforinput():
    while True:
        for event in pygame.event.get():
            if event.type == KEYUP and event.key not in [QUIT,K_ESCAPE]:
                return
            if event.type == KEYUP and event.key in [QUIT,K_ESCAPE]:
                pygame.quit()
                sys.exit()
    
if __name__=='__main__':
    main()
