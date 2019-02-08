# -*- coding: cp1252 -*-
import pygame
import math

#todo
"""
lave command point system
lave meneur
lave optionsmenu
lave så man kan angribe med enheder
fikse felter med lidt overlap

lave så veh kan flytte ekstra i den retning de pejer, lige nu kan de flytte en ekstra mod højre
vise det ene ekstra felt i veh movement i UI

Hvis x og y er det samme på gameboard, så er der problemer med movement langs y aksen

"""

#Variables
char = ""
activePlayer = 0
activeUnit = 0
selectUnit = False
turning = False
attacking = False
menu = "menuMain"
gameboard = [[0 for x in range(11)] for y in range(12)]
units = [[0 for x in range(15)] for y in range(2)]
actionsP1 = 6
actionsP2 = 6
gencolour = (0, 0, 0 )
life = 0

class unit():
    def __init__(self, unittype, health, attack, vehicle, defFront, defBack, defSide, movement, facing, infMulti, vehMulti, posx, posy, timesmoved):
        self.typ = unittype
        self.hp = health
        self.atk = attack
        self.veh = vehicle
        self.defF = defFront
        self.defB = defBack
        self.defS = defSide
        self.mov = movement
        self.face = facing
        self.infMul = infMulti
        self.vehMul = vehMulti
        self.x = posx
        self.y = posy
        self.mt = timesmoved

#initialiser pygame
pygame.init()
screen = pygame.display.set_mode((1000, 650))
clock = pygame.time.Clock()
done = False

#lav det i en 2d array hvor den ene dimension er hvilken spiller ejer de givne enheder
#den anden er listen af enhederne defineret som klasser
#alle værdier i forhold til attack og defense skal ændres til endelige værdier
def initUnits():
    global units
    i1 = 0
    while i1 < 2:
        i2 = 0
        while i2 < 15:
            if i2 == 0:
                units[i1][i2] = unit("T", 100, 80, True, 80, 10, 60, 3, "north", 1, 1, 0, 0, 0)
            elif i2 > 0 and i2 < 3:
                units[i1][i2] = unit("A", 100, 80, True, 50, 0, 20, 2, "north", 0.75, 1, 0, 0, 0)
            elif i2 > 2 and i2 < 8:
                units[i1][i2] = unit("R", 100, 50, False, 30, 0, 0, 2, "north", 0.75, 1.5, 0, 0, 0)
            else:
                units[i1][i2] = unit("I", 100, 50, False, 30, 0, 0, 2, "north", 1, 1, 0, 0, 0)
            i2 = i2+1
        i1 = i1+1
    i1 = 0
    while i1<2:
        i2 = 0
        while i2<15:
            if i1 == 0:
                units[i1][i2].face = "east"
            if i1 == 1:
                units[i1][i2].face = "west"
            i2 = i2+1
        i1 = i1+1

def placeUnits():
    global units
    #place tanks
    i1 = 0
    while i1 < 2:
        units[i1][0].x = 1+i1*9
        units[i1][0].y = 5
        i1 = i1+1

    #place Artillery
    i1 = 0
    while i1 < 2:
        i2 = 1
        while i2 < 3:
            units[i1][i2].x = 0+11*i1
            units[i1][i2].y = 2+2*i2
            i2 = i2+1
        i1 = i1+1

    #place RPG
    i1 = 0
    while i1 < 2:
        i2 = 3
        while i2<8:
            units[i1][i2].x = 0+11*i1
            if i2 < 6:
                units[i1][i2].y = -1+i2+i2/5
            else:
                units[i1][i2].y = 1+i2
            #y skal være 2,3,5,7,8
            i2 = i2+1
        i1 = i1+1
        
    #place Inf
    i1 = 0
    while i1<2:
        i2 = 8
        while i2<15:
            if i2 < 14:
                units[i1][i2].x = 1+9*i1
            else:
                units[i1][i2].x = 2+7*i1
            if i2 < 14:
                units[i1][i2].y = -6+i2+i2/11
            else:
                units[i1][i2].y = 5
            i2 = i2+1
        i1 = i1+1

def attack(pos):
    global targetPlayer
    global activePlayer
    global units
    global activeUnit
    global targetUnit
    global attacking
    global selectUnit
    targetConfimred = True
    terrain = 0
    lastActiveUnit = activeUnit
    atacker = units[activePlayer][lastActiveUnit]
    checkTile(pos)
    defender = units[targetPlayer][targetUnit]
    self = False
    if atacker.x == defender.x and atacker.y == defender.y:
        self = True
    
    if atacker.typ == 'A':
        if atacker.face == 'north' or atacker.face == 'south':
            if (abs(defender.y-atacker.y) == 2 or abs(defender.y-atacker.y) == 3) and defender.x == atacker.x:
                targetConfimred = True
            elif abs(defender.y-atacker.y) == 3 and (defender.x == atacker.x+1 or defender.x == atacker.x-1):
                targetConfimred = True
        elif atacker.face == 'west' or atacker.face == 'east':
            if (abs(defender.x-atacker.x) == 2 or abs(defender.x-atacker.x) == 3) and defender.y == atacker.y:
                targetConfimred = True
            elif abs(defender.x-atacker.x) == 3 and (defender.y == atacker.y+1 or defender.y == atacker.y-1):
                targetConfimred = True
    else:
        if (abs(defender.y-atacker.y) == 1 and defender.x == atacker.x) or (abs(defender.x-atacker.x) == 1 and defender.y == atacker.y):
            targetConfimred = True
                
    if atacker.veh:
        inf = 5
    else:
        inf = math.ceil(atacker.hp/20)
    if defender.veh:
        multi = atacker.vehMul
    else:
        multi = atacker.infMul
    if defender.veh == False:
        direktion = 'front'
    else:
        direktion = direktionMulti(atacker, defender)
    if direktion == 'front' and atacker.typ != 'A':
        defence = defender.defF
    elif direktion == 'side' and atacker.typ != 'A':
        defence = defender.defS
    else:
        defence = defender.defB
		
    #terrain = gameboard[defender.x][defender.y]
    dmg = (atacker.atk/5 * inf * multi -(defence + terrain))
    if dmg > 0 and targetConfimred == True and self != True:
        defender.hp = defender.hp - dmg
    if defender.typ != 'A' and defender.hp > 0:
        if defender.veh:
            inf = 5
        else:
            inf = math.ceil(defender.hp/20)
        if atacker.veh:
            multi = defender.vehMul
        else:
            multi = defender.infMul
        defence = atacker.defF
        dmg = defender.atk/5 * inf * multi -(defence + terrain)
    
        if dmg > 0 and targetConfimred == True and self != True and direktion == 'front' and atacker.typ != 'A':
            atacker.hp = atacker.hp - dmg
    activeUnit = lastActiveUnit
    attacking = False
    selectUnit = False
    if defender.hp <= 0:
        defender.x = 57005
        defender.y = 57005
    if atacker.hp <= 0:
        atacker.x = 57005
        atacker.y = 57005

def direktionMulti(activeUnit, targetUnit):
    global units
    xt = targetUnit.x
    yt = targetUnit.y
    xa = activeUnit.x
    ya = activeUnit.y

    facingt = targetUnit.face
    if xa- xt == 0 and ya -yt == 1:
        if facingt == 'north':
            direktMulti = 'front'
        elif facingt == 'east' or facingt == 'west':
            direktMulti = 'side'
        else:
            dirketMulti = 'back'
    elif xa - xt == 1 and ya - yt == 0:
        if facingt == 'east':
            direktMulti = 'front'
        elif facingt == 'north' or facingt == 'south':
            direktMulti = 'side'
        else:
            direktMulti = 'back'
    elif xa - xt == 0 and ya - yt == -1:
        if facingt == 'south':
            direktMulti = 'front'
        elif facingt == 'east' or facingt == 'west':
            direktMulti = 'side'
        else:
            direktMulti = 'back'
    else:
        if facingt == 'west':
            direktMulti = 'front'
        elif facingt == 'north' or facingt == 'south':
            direktMulti = 'side'
        else:
            direktMulti = 'back'
    return direktMulti

def movement():
    global units
    global selectUnit
    global turning
    global whereToX
    global whereToY
    global attacking
    global actionsP1
    global actionsP2
    #vis hvor enheden kan gå hen
    x = units[activePlayer][activeUnit].x
    y = units[activePlayer][activeUnit].y
    movement = units[activePlayer][activeUnit].mov-units[activePlayer][activeUnit].mt+1
    muligt = 0
    langmoveVeh = False
    i1 = 0
    while i1<12:
        i2 = 0
        while i2<11:
            blocked = False
            i3 = 0
            if gameboard[i1][i2].collidepoint(pos):
                whereToX = i1
                whereToY = i2
                if units[activePlayer][activeUnit].veh:
                    if units[activePlayer][activeUnit].face == 'north' and i2 - units[activePlayer][activeUnit].y == -movement:
                        langmoveVeh = True
                    elif units[activePlayer][activeUnit].face == 'south' and i2 - units[activePlayer][activeUnit].y == movement:
                        langmoveVeh = True
                    elif units[activePlayer][activeUnit].face == 'east' and i1 - units[activePlayer][activeUnit].x == movement:
                        langmoveVeh = True
                    elif units[activePlayer][activeUnit].face == 'west' and i1 - units[activePlayer][activeUnit].x == -movement:
                        langmoveVeh = True

                if units[activePlayer][activeUnit].veh and langmoveVeh == False:
                    movement = movement-1
                while i3<2:
                    i4 = 0
                    while i4<15:                            
                        x = units[i3][i4].x
                        y = units[i3][i4].y
                        if i1 == units[activePlayer][activeUnit].x and i2 == units[activePlayer][activeUnit].y:
                            selectUnit = False
                            target()
                            if units[activePlayer][activeUnit].mt > 0:
                                units[activePlayer][activeUnit].mt = units[activePlayer][activeUnit].mt - 1
                            if activePlayer == 0 and attacking == False:
                                actionsP1 = actionsP1 + 0.5
                            elif activePlayer == 1 and attacking == False:
                                actionsP2 = actionsP2 + 0.5
                            break
                        if i1 == x and i2 == y:
                            blocked = True
                            break
                        elif i3 == 1 and i4 == 14:
                            muligt = 1
                        i4 = i4 +1
                        if blocked == True:
                            break
                    i3 = i3 +1
                        
                if muligt != 0 and (movement>=(abs(i1 - units[activePlayer][activeUnit].x) + abs(i2 - units[activePlayer][activeUnit].y))or langmoveVeh == True):                    
                    blocked = roadBlocked()
                    if blocked == False:
                        selectUnit = False
                        units[activePlayer][activeUnit].x = i1
                        units[activePlayer][activeUnit].y = i2
                    if units[activePlayer][activeUnit].veh == True and langmoveVeh == False:
                        selectUnit = True
                        turning = True
                    elif units[activePlayer][activeUnit].typ != 'A':
                        target()
                elif blocked == True:
                    selectUnit = False
        
            i2 = i2+1
        i1 = i1+1
        
def roadBlocked():
    global activePlayer
    global units
    global activeUnit
    global whereToX
    global whereToY
    blocked1 = False
    blocked2 = False
    blocked = False
    if abs(whereToX - units[activePlayer][activeUnit].x) + abs(whereToY - units[activePlayer][activeUnit].y) == 1:
        blocked == False
    elif abs(whereToX - units[activePlayer][activeUnit].x) == 1 and abs(whereToY - units[activePlayer][activeUnit].y) == 1:
        i1 = 0
        while i1 < 2:
            if i1== activePlayer:
                i1 = i1+1
            else:
                i2 = 0
                while i2 < 15:
                    x = units[i1][i2].x
                    y = units[i1][i2].y
                    if whereToX == x and units[activePlayer][activeUnit].y == y:
                        #print "Her kan du ikke rykke hen"
                        blocked1 = True

                    i2 = i2+1
                i1 = i1+1    
        i1 = 0
        while i1 < 2:
            if i1== activePlayer:
                i1 = i1+1
            else:
                i2 = 0
                while i2 < 15:
                    x = units[i1][i2].x
                    y = units[i1][i2].y
                    if whereToY == y and units[activePlayer][activeUnit].x == x:
                        #print "Her kan du ikke rykke hen"
                        blocked2 = True

                    i2 = i2+1
                i1 = i1+1
        if blocked1 == True and blocked2 == True:
            blocked = True
    else: 
        if abs(whereToX - units[activePlayer][activeUnit].x)>=2:
                i1 = 0
                while i1 < 2:
                    if i1== activePlayer:
                        i1 = i1+1
                    else:
                        i2 = 0
                        while i2 < 15:
                            x = units[i1][i2].x
                            y = units[i1][i2].y
                            if whereToX - units[activePlayer][activeUnit].x >= 1:
                                if whereToX-1 == x and units[activePlayer][activeUnit].y == y:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True  
                            if whereToX - units[activePlayer][activeUnit].x <= -1:
                                if whereToX+1 == x and units[activePlayer][activeUnit].y == y:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True 
                            i2 = i2+1
                        i1 = i1+1
                i1 = 0
                while i1 < 2:
                    if i1== activePlayer:
                        i1 = i1+1
                    else:
                        i2 = 0
                        while i2 < 15:
                            x = units[i1][i2].x
                            y = units[i1][i2].y
                            if whereToX - units[activePlayer][activeUnit].x >= 1:
                                if whereToX-2 == x and units[activePlayer][activeUnit].y == y:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True  
                            if whereToX - units[activePlayer][activeUnit].x <= -1:
                                if whereToX+2 == x and units[activePlayer][activeUnit].y == y:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True 
                            i2 = i2+1
                        i1 = i1+1
                        
        elif abs(whereToY - units[activePlayer][activeUnit].y)>= 2:
            i1 = 0
            while i1 < 2:
                if i1== activePlayer:
                    i1 = i1+1
                else:
                    i2 = 0
                    while i2 < 15:
                        x = units[i1][i2].x
                        y = units[i1][i2].y
                        if units[activePlayer][activeUnit].y - y <= -1:
                            if whereToY-1 == y and units[activePlayer][activeUnit].x == x:
                                #print "Her kan du ikke rykke hen"
                                blocked = True
                        elif units[activePlayer][activeUnit].y - y >= 1:
                            if whereToY+1 == y and units[activePlayer][activeUnit].x == x:
                                #print "Her Kan du ikke stå"
                                blocked = True
                        i2 = i2+1
                    i1 = i1+1
        
            if abs(whereToY - units[activePlayer][activeUnit].y) >= 2:
                i1 = 0
                while i1 < 2:
                    if i1== activePlayer:
                        i1 = i1+1
                    else:
                        i2 = 0
                        while i2 < 15:
                            x = units[i1][i2].x
                            y = units[i1][i2].y
                            if whereToY - units[activePlayer][activeUnit].y >= 1:
                                if whereToY-2 == y and units[activePlayer][activeUnit].x == x:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True
                            elif whereToY - units[activePlayer][activeUnit].y <= -1:
                                if whereToY+2 == y and units[activePlayer][activeUnit].x == x:
                                    #print "Her kan du ikke rykke hen"
                                    blocked = True

                            i2 = i2+1
                        i1 = i1+1
    return blocked

def turningVeh():
    global activeUnit
    global units
    global activePlayer
    global turning
    global selectUnit
    if units[activePlayer][activeUnit].x!= 11:
        if gameboard[units[activePlayer][activeUnit].x+1][units[activePlayer][activeUnit].y].collidepoint(pos):
            units[activePlayer][activeUnit].face = 'east'
    if units[activePlayer][activeUnit].y!= 10:
        if gameboard[units[activePlayer][activeUnit].x][units[activePlayer][activeUnit].y+1].collidepoint(pos):
            units[activePlayer][activeUnit].face = 'south'
    if gameboard[units[activePlayer][activeUnit].x-1][units[activePlayer][activeUnit].y].collidepoint(pos):
        units[activePlayer][activeUnit].face = 'west'        
    if gameboard[units[activePlayer][activeUnit].x][units[activePlayer][activeUnit].y-1].collidepoint(pos):
        units[activePlayer][activeUnit].face = 'north'
    
    #print units[activePlayer][activeUnit].face
    turning = False
    selectUnit = False
    if units[activePlayer][activeUnit].typ != 'A':
        target()
   
def target():
    global attacking
    global activePlayer
    global activeUnit
    global units
    global selectUnit
    unit = units[activePlayer][activeUnit]
    #print "target start"
    i1 = 0
    while i1 < 2:
        i2 = 0
        if i1 == activePlayer:
            i1 = i1+1
        else:
            while i2 < 15:
                #print i1
                #print i2
                if unit.typ == 'T':
                    #print "tank"
                    if unit.face == 'north' and (units[i1][i2].y - unit.y == -1 and units[i1][i2].x == unit.x):
                        attacking = True
                    elif unit.face == 'south' and (units[i1][i2].y - unit.y == 1 and units[i1][i2].x == unit.x):
                        attacking = True
                    elif unit.face == 'east' and (units[i1][i2].x - unit.x == 1 and units[i1][i2].y == unit.y):
                        #print 'her er jeg'
                        attacking = True
                    elif unit.face == 'west' and (units[i1][i2].x - unit.x == -1 and units[i1][i2].y == unit.y):
                        attacking = True
                elif unit.typ == 'A':
                    if unit.face == 'north':
                        if units[i1][i2].y - unit.y == -2 and units[i1][i2].x == unit.x:
                            attacking = True
                        elif units[i1][i2].y - unit.y == -3 and (units[i1][i2].x == unit.x or abs(units[i1][i2].x -unit.x) ==1):
                            attacking = True
                    elif unit.face == 'south':
                        if units[i1][i2].y - unit.y == 2 and units[i1][i2].x == unit.x:
                            attacking = True
                        elif units[i1][i2].y - unit.y == 3 and (units[i1][i2].x == unit.x or abs(units[i1][i2].x -unit.x) ==1):
                            attacking = True
                    elif unit.face == 'west':
                        if units[i1][i2].x - unit.x == -2 and units[i1][i2].y == unit.y:
                            attacking = True
                        elif units[i1][i2].x - unit.x == -3 and (units[i1][i2].y == unit.y or abs(units[i1][i2].y -unit.y) ==1):
                            attacking = True
                    elif unit.face == 'east':
                        if units[i1][i2].x - unit.x == 2 and units[i1][i2].y == unit.y:
                            attacking = True
                        elif units[i1][i2].x - unit.x == 3 and (units[i1][i2].y == unit.y or abs(units[i1][i2].y -unit.y) ==1):
                            attacking = True
            
                elif (abs(units[i1][i2].x - unit.x) == 1 and units[i1][i2].y == unit.y) or (abs(units[i1][i2].y - unit.y) == 1 and units[i1][i2].x == unit.x):
                    attacking = True
                    break
                i2 = i2+1
            i1 = i1+1
    if attacking == True:
        selectUnit = True

def checkTile(pos):
    global activeplayer
    global activeUnit
    global targetPlayer
    global targetUnit
    global selectUnit
    global turning
    global actionsP1
    global actionsP2
    
    if activePlayer == 0:
        targetPlayer = 1
    else:
        targetPlayer = 0
    if selectUnit and attacking == False:
        movement()
    else:
        #select unit
        i1 = 0
        while i1<12:
            i2 = 0
            while i2<11:
                if gameboard[i1][i2].collidepoint(pos):
                    if turning == False:
                        i3 = 0
                        while i3<15:
                            if attacking == True:
                                if units[activePlayer][activeUnit].x == i1 and units[activePlayer][activeUnit].y == i2:
                                    targetPlayer = activePlayer
                                    targetUnit = activeUnit
                                elif units[targetPlayer][i3].x == i1 and units[targetPlayer][i3].y == i2:
                                    targetUnit = i3
                            else:
                                if units[activePlayer][i3].x == i1 and units[activePlayer][i3].y == i2:
                                    activeUnit = i3
                                    if units[activePlayer][i3].mt != 2:
                                        units[activePlayer][i3].mt = units[activePlayer][i3].mt+1
                                        selectUnit = True
                                        if activePlayer == 0:
                                            actionsP1 = actionsP1-1
                                        else:
                                            actionsP2 = actionsP2-1
                            i3 = i3+1
                i2 = i2+1
            i1 = i1+1
        #check om der er en af spillerens enheder på feltet

def menuButton(fonttype, tekst, colour, posx, posy, center):
    text = fonttype.render(tekst, True, colour)
    if center == True:
        button = screen.blit(text, (posx - text.get_width() // 2, posy - text.get_height() // 2))
    else:
        button = screen.blit(text, (posx, posy))
    return button
    #lav en menu knap

def UI_uinfo(player, unit):
    menuButton(ttfont, "hp: " + str(units[player][unit].hp), (0, 0, 0), 25+player*800, 100, False)
    menuButton(ttfont, "atk: " + str(units[player][unit].atk), (0, 0, 0), 25+player*800, 125, False)
    if units[player][unit].typ == "T":
        menuButton(ttfont, "Type: Tank", (0, 0, 0), 25+player*800, 150, False)
    elif units[player][unit].typ == "A":
        menuButton(ttfont, "Type: Artillery", (0, 0, 0), 25+player*800, 150, False)
    elif units[player][unit].typ == "I":
        menuButton(ttfont, "Type: Infantry", (0, 0, 0), 25+player*800, 150, False)
    elif units[player][unit].typ == "R":
        menuButton(ttfont, "Type: Rocket", (0, 0, 0), 25+player*800, 150, False)
    menuButton(ttfont, "mov: " + str(units[player][unit].mov), (0, 0, 0), 25+player*800, 175, False)
    menuButton(ttfont, "Inf. Multi: " + str(units[player][unit].infMul), (0, 0, 0), 25+player*800, 200, False)
    menuButton(ttfont, "Veh. Multi: " + str(units[player][unit].vehMul), (0, 0, 0), 25+player*800, 225, False)
    if units[player][unit].veh == True:
        menuButton(ttfont, "Front Armour: " + str(units[player][unit].defF), (0, 0, 0), 25+player*800, 250, False)
        menuButton(ttfont, "Back Armour: " + str(units[player][unit].defB), (0, 0, 0), 25+player*800, 275, False)
        menuButton(ttfont, "Side Armour: " + str(units[player][unit].defS), (0, 0, 0), 25+player*800, 300, False)
    else:
        ufarm = menuButton(ttfont, "Armour: " + str(units[player][unit].defF), (0, 0, 0), 25+player*800, 250, False)

def UI():
    global menu
    global selectUnit
    global activePlayer
    global activeUnit
    global actionsP1
    global actionsP2
    global whereToX
    global whereToY
    global turning
    global attacking
    global end
    
    screen.fill((255, 255, 255)) #lav hvid skærm
    if menu == "menuMain":
        #Title = menuButton(tfont, "Warsquare", (0, 0, 0), 500, 100, True)
        img = pygame.image.load('sprites/warsquare.png')
        screen.blit(img,(174,0))
        UI.main_play = menuButton(font, "Start Game", (0, 0, 0), 500, 200, True)
        UI.main_rules = menuButton(font, "Rules", (0, 0, 0), 500, 250, True)
        UI.main_quit = menuButton(font, "Quit", (0, 0, 0), 500, 600, True)
    elif menu == "menuVictory":
        menuButton(tfont, "Victory", (0, 0, 0), 500, 50, True)
        if end == "redIsDead":
            menuButton(font, "Blue Player wins", (0, 0, 255), 500, 150, True)
        else:
            menuButton(font, "Red Player wins", (255, 0, 0), 500, 150, True)
        UI.victory_main = menuButton(tfont, "Back to main menu", (0, 0, 0), 500, 600, True)
    elif menu == "menuRules":
        menuButton(font, "Rules", (0, 0, 0), 500, 50, True)
        UI.rules_back = menuButton(font, "Back", (0, 0, 0), 100, 600, True)
        #skriv reglerne
        menuButton(ttfont, "2 players alwas play against each other one is red and the other is blue blue alwas starts", (0, 0, 0), 500, 100, True)
        menuButton(ttfont, "Every player has 15 units of 4 different types:", (0, 0, 0), 500, 125, True)
        menuButton(ttfont, "First is the Tank which you get one of", (0, 0, 0), 500, 175, True)
        img = pygame.image.load('sprites/tankbluN.png')
        screen.blit(img,(250,150))
        img = pygame.image.load('sprites/tankredN.png')
        screen.blit(img,(700,150))
        menuButton(ttfont, "You also have 2 artillery each", (0, 0, 0), 500, 225, True)
        img = pygame.image.load('sprites/ABluN.png')
        screen.blit(img,(250,200))
        #screen.blit(img,(250,200))
        img = pygame.image.load('sprites/ARedN.png')
        screen.blit(img,(700,200))
        #screen.blit(img,(700,200))
        menuButton(ttfont, "5 rocket launchers", (0, 0, 0), 500, 275, True)
        img = pygame.image.load('sprites/RBlue5.png')
        screen.blit(img,(250,250))
        img = pygame.image.load('sprites/RRed5.png')
        screen.blit(img,(700,250))
        menuButton(ttfont, "and 7 infantry units", (0, 0, 0), 500, 325, True)
        img = pygame.image.load('sprites/InfBlu5.png')
        screen.blit(img,(250,300))
        img = pygame.image.load('sprites/InfRed5.png')
        screen.blit(img,(700,300))
        menuButton(ttfont, "Under here you can see 4 buttons which will take you to an explanation of the game each", (0, 0, 0), 500, 375, True)

        UI.rules_attacking = menuButton(font, "Attacking", (0, 0, 0), 150, 450, True)
        UI.rules_movement = menuButton(font, "Movement", (0, 0, 0), 500, 450, True)
        UI.rules_stats = menuButton(font, "Unit Stats", (0, 0, 0), 850, 450, True)
        UI.rules_cmd = menuButton(font, "Command point system", (0, 0, 0), 500, 510, True)
    elif menu[:8] == "menuRSub":
        UI.rules_back = menuButton(font, "Back", (0, 0, 0), 100, 600, True)
        if menu == "menuRSubatk":
            menuButton(font, "Attacking", (0, 0, 0), 500, 50, True)
            menuButton(ttfont, "If you have selected a foot soldier and you want to attack the enemy", (0, 0, 0), 50, 100, False)
            menuButton(ttfont, "all you have to do is move right next to them in any direction", (0, 0, 0), 50, 125, False)
            menuButton(ttfont, "then the tile they are standing on will turn red ", (0, 0, 0), 50, 150, False)
            menuButton(ttfont, "if you click the enemy unit yours will attack", (0, 0, 0), 50, 175, False)

            menuButton(ttfont, "If you have selected an artillery and you want to attack, you click on the artillery", (0, 0, 0), 50, 275, False)
            menuButton(ttfont, "if an enemy is in range in the direction the artillery is pointing", (0, 0, 0), 50, 300, False)
            menuButton(ttfont, "then the tiles it can attack will turn red simply click the enemy to attack", (0, 0, 0), 50, 325, False)
            menuButton(ttfont, "enemies can’t counterattack artillery.", (0, 0, 0), 50, 350, False)
            menuButton(ttfont, "the artillery’s attack pattern is like a T and it can’t attack from one square away.", (0, 0, 0), 50, 375, False)

            menuButton(ttfont, "If you have selected the tank and you want to attack the enemy", (0, 0, 0), 50, 475, False)
            menuButton(ttfont, "you must be facing them and be right next to the enemy", (0, 0, 0), 50, 500, False)
            menuButton(ttfont, "if there is an enemy right in front of your tank, just click them to shoot", (0, 0, 0), 50, 525, False)

            menuButton(ttfont, "If you haven’t moved yet but still want to attack", (0, 0, 0), 550, 100, False)
            menuButton(ttfont, "just click on your unit again", (0, 0, 0), 550, 125, False)
            menuButton(ttfont, "attacking other units makes them counter attack", (0, 0, 0), 550, 150, False)
            menuButton(ttfont, "different units have different strengths and weaknesses", (0, 0, 0), 550, 175, False)
            menuButton(ttfont, "look in the stats tab for more info", (0, 0, 0), 550, 200, False)
            menuButton(ttfont, "if you click the enemy unit yours will attack.", (0, 0, 0), 550, 225, False)
            #mangler screenshots til attacking
        if menu == "menuRSubmov":
            menuButton(font, "Movement", (0, 0, 0), 500, 50, True)
            menuButton(ttfont, "You select units by clicking on the with the mouse", (0, 0, 0), 300, 100, False)
            menuButton(ttfont, "Then the square to which the unit can move, will be highlighted with green", (0, 0, 0), 300, 125, False)
            img = pygame.image.load('sprites/movScreen1.png')
            screen.blit(img,(50,50))
            menuButton(ttfont, "Footsoldiers can always move to their maximum range,", (0, 0, 0), 300, 200, False)
            menuButton(ttfont, "Vehicles however, can only move the max, if they are already pointed in that direction", (0, 0, 0), 300, 225, False)
            img = pygame.image.load('sprites/movScreen2.png')
            screen.blit(img,(50,175))
            menuButton(ttfont, "and i they aren't moving their maximum they will also be able to turn", (0, 0, 0), 300, 250, False)
            menuButton(ttfont, "When turning the 4 adjacent squares will highlight in green", (0, 0, 0), 300, 275, False)
            menuButton(ttfont, "And the vehicle will then turn towards the square that is clicked", (0, 0, 0), 300, 300, False)
            img = pygame.image.load('sprites/movScreen3.png')
            screen.blit(img,(700,300))
            menuButton(ttfont, "Units can also pass through friendly units, but not enemy units", (0, 0, 0), 125, 350, False)
            img = pygame.image.load('sprites/movScreen4.png')
            screen.blit(img,(250,400))
            img = pygame.image.load('sprites/movScreen5.png')
            screen.blit(img,(400,400))
        if menu == "menuRSubstat":
            menuButton(font, "Stats", (0, 0, 0), 500, 50, True)
            img = pygame.image.load('sprites/statsScreen1.png')
            screen.blit(img,(50,125))
            menuButton(ttfont, "All of the units have a set of statistics", (0, 0, 0), 250, 100, False)
            menuButton(ttfont, "Every unit has health or HP", (0, 0, 0), 250, 125, False)
            menuButton(ttfont, "They also have an attackpower represented by atk", (0, 0, 0), 250, 150, False)
            menuButton(ttfont, "The UI also shows the type of the unit if you mouse over them", (0, 0, 0), 250, 175, False)
            menuButton(ttfont, "Their max movement range is also shown with mov", (0, 0, 0), 250, 200, False)
            menuButton(ttfont, "They also have two multipliers one for infantry and one for vehicles", (0, 0, 0), 250, 225, False)
            menuButton(ttfont, "And the multiplier will be applied to their attack, before factoring in defense", (0, 0, 0), 250, 250, False)
            menuButton(ttfont, "They also have a value representing said defense", (0, 0, 0), 250, 275, False)
            menuButton(ttfont, "Foot soldiers only have one defense which is omnidirectional", (0, 0, 0), 250, 300, False)
            menuButton(ttfont, "Vehicles however have 3: front, sides and back, with the front being very heavily armoured", (0, 0, 0), 250, 325, False)
            menuButton(ttfont, "and the back to most lightly armoured", (0, 0, 0), 250, 350, False)
            menuButton(ttfont, "Another difference between foot soldiers and vehicles", (0, 0, 0), 250, 375, False)
            menuButton(ttfont, "is that foot soldiers lose strength when taking damage", (0, 0, 0), 250, 400, False)
            menuButton(ttfont, "For every 20 HP lost, they lose one of their 5 soldiers", (0, 0, 0), 250, 425, False)
            menuButton(ttfont, "thus they also lose one fifth of their attackpower", (0, 0, 0), 250, 450, False)
            menuButton(ttfont, "the damage that footsoldiers have taken is also shown visually", (0, 0, 0), 250, 475, False)
            menuButton(ttfont, "through their sprite losing men", (0, 0, 0), 250, 500, False)
            img = pygame.image.load('sprites/RRed4.png')
            screen.blit(img,(750,450))
            img = pygame.image.load('sprites/InfBlu2.png')
            screen.blit(img,(175,450))
        if menu == "menuRSubcmd":
            UI.rules_cmd = menuButton(font, "Spillets gang", (0, 0, 0), 500, 50, True)
            img = pygame.image.load('sprites/cmdScreen1.png')
            screen.blit(img,(50,125))
            menuButton(ttfont, "The map is 12*11, and the game always starts with the same setup", (0, 0, 0), 250, 125, False)
            menuButton(ttfont, "Where the infantry units are up front, with everyone else behind them", (0, 0, 0), 250, 150, False)
            menuButton(ttfont, "To move their units each player has 6 command points", (0, 0, 0), 250, 175, False)
            menuButton(ttfont, "Command points are represented by black circles on both sides of the map", (0, 0, 0), 250, 200, False)
            img = pygame.image.load('sprites/cmdScreen2.png')
            screen.blit(img,(450,225))
            menuButton(ttfont, "Command points are used by clicking on a unit and selecting it", (0, 0, 0), 250, 275, False)
            menuButton(ttfont, "The same unit can be selected up to two times pr turn", (0, 0, 0), 250, 300, False)
            menuButton(ttfont, "Though it does get a penalty to movement range of -1 on the second activation each turn", (0, 0, 0), 250, 325, False)
            menuButton(ttfont, "After each player has used up all of their command points, it's the other players turn", (0, 0, 0), 250, 350, False)
            menuButton(ttfont, "It is also possible to end a player turn prematurely, though all remaning points will be lost", (0, 0, 0), 250, 375, False)
            menuButton(ttfont, "There is also an indicater in the bottom saying which players turn it is", (0, 0, 0), 250, 400, False)
    elif menu == "gameboard":
        if activePlayer == 0:
            menuButton(ttfont, "Blue player", (0, 0, 255), 300, 610, True)
        else:
            menuButton(ttfont, "Red player", (255, 0, 0), 700, 610, True)
        UI.gameboard_endturn = menuButton(font, "end turn", (0, 0, 0), 500, 610, True)
        i1 = 0
        while i1<12:
            i2 = 0
            while i2 < 11:
                i3 = 0
                opponent = activePlayer+1
                if opponent == 2:
                    opponent = 0
                while i3 < 15:
                    movement = units[activePlayer][activeUnit].mov-units[activePlayer][activeUnit].mt+1
                    if units[activePlayer][activeUnit].veh == True:
                        movement = movement-1
                    if turning == True or attacking == True:
                        movement = 1
                    if selectUnit and movement >=(abs(i1 - units[activePlayer][activeUnit].x) + abs(i2 - units[activePlayer][activeUnit].y)):
                        if attacking == True:
                            if units[activePlayer][activeUnit].veh:
                                if units[activePlayer][activeUnit].typ == "T":
                                    if units[activePlayer][activeUnit].face == "north":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y-50, 50, 50])
                                    if units[activePlayer][activeUnit].face == "south":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y+50, 50, 50])
                                    if units[activePlayer][activeUnit].face == "west":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-50, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                    if units[activePlayer][activeUnit].face == "east":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+50, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                if units[activePlayer][activeUnit].typ == "A":
                                    if units[activePlayer][activeUnit].face == "north":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y-100, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y-150, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+50, 25+50*units[activePlayer][activeUnit].y-150, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-50, 25+50*units[activePlayer][activeUnit].y-150, 50, 50])
                                    if units[activePlayer][activeUnit].face == "south":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y+100, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y+150, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+50, 25+50*units[activePlayer][activeUnit].y+150, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-50, 25+50*units[activePlayer][activeUnit].y+150, 50, 50])
                                    if units[activePlayer][activeUnit].face == "west":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-100, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-150, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-150, 25+50*units[activePlayer][activeUnit].y+50, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x-150, 25+50*units[activePlayer][activeUnit].y-50, 50, 50])
                                    if units[activePlayer][activeUnit].face == "east":
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+100, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+150, 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+150, 25+50*units[activePlayer][activeUnit].y+50, 50, 50])
                                        pygame.draw.rect(screen, (255, 0, 0), [200+50*units[activePlayer][activeUnit].x+150, 25+50*units[activePlayer][activeUnit].y-50, 50, 50])
                            else:
                                pygame.draw.rect(screen, (255, 0, 0), [200+50*i1, 25+50*i2, 50, 50])
                        else:
                            pygame.draw.rect(screen, (0, 200, 0), [200+50*i1, 25+50*i2, 50, 50])
                        #tegn ekstra felt for vehicles
                        whereToX = units[activePlayer][activeUnit].x
                        whereToY = units[activePlayer][activeUnit].y-units[activePlayer][activeUnit].mov+(units[activePlayer][activeUnit].mt-1)
                        if units[activePlayer][activeUnit].face == "north" and units[activePlayer][activeUnit].veh == True and turning == False and attacking == False:
                            block = roadBlocked()
                            if block == False:
                                pygame.draw.rect(screen, (0, 200, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y-units[activePlayer][activeUnit].mov*50+50*(units[activePlayer][activeUnit].mt-1), 50, 50])
                                pygame.draw.rect(screen, (0, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y-units[activePlayer][activeUnit].mov*50+50*(units[activePlayer][activeUnit].mt-1), 50, 50], 2)
                        whereToY = units[activePlayer][activeUnit].y+units[activePlayer][activeUnit].mov-(units[activePlayer][activeUnit].mt-1)
                        if units[activePlayer][activeUnit].face == "south" and units[activePlayer][activeUnit].veh == True and turning == False and attacking == False:
                            block = roadBlocked()
                            if block == False:
                                pygame.draw.rect(screen, (0, 200, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y+units[activePlayer][activeUnit].mov*50-50*(units[activePlayer][activeUnit].mt-1), 50, 50])
                                pygame.draw.rect(screen, (0, 0, 0), [200+50*units[activePlayer][activeUnit].x, 25+50*units[activePlayer][activeUnit].y+units[activePlayer][activeUnit].mov*50-50*(units[activePlayer][activeUnit].mt-1), 50, 50], 2)
                        whereToX = units[activePlayer][activeUnit].x-units[activePlayer][activeUnit].mov+(units[activePlayer][activeUnit].mt-1)
                        whereToY = units[activePlayer][activeUnit].y
                        if units[activePlayer][activeUnit].face == "west" and units[activePlayer][activeUnit].veh == True and turning == False and attacking == False:
                            block = roadBlocked()
                            if block == False:
                                pygame.draw.rect(screen, (0, 200, 0), [200+50*units[activePlayer][activeUnit].x-units[activePlayer][activeUnit].mov*50+50*(units[activePlayer][activeUnit].mt-1), 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                pygame.draw.rect(screen, (0, 0, 0), [200+50*units[activePlayer][activeUnit].x-units[activePlayer][activeUnit].mov*50+50*(units[activePlayer][activeUnit].mt-1), 25+50*units[activePlayer][activeUnit].y, 50, 50], 2)
                        whereToX = units[activePlayer][activeUnit].x+units[activePlayer][activeUnit].mov-(units[activePlayer][activeUnit].mt-1)
                        if units[activePlayer][activeUnit].face == "east" and units[activePlayer][activeUnit].veh == True and turning == False and attacking == False:
                            block = roadBlocked()
                            if block == False:
                                pygame.draw.rect(screen, (0, 200, 0), [200+50*units[activePlayer][activeUnit].x+units[activePlayer][activeUnit].mov*50-50*(units[activePlayer][activeUnit].mt-1), 25+50*units[activePlayer][activeUnit].y, 50, 50])
                                pygame.draw.rect(screen, (0, 0, 0), [200+50*units[activePlayer][activeUnit].x+units[activePlayer][activeUnit].mov*50-50*(units[activePlayer][activeUnit].mt-1), 25+50*units[activePlayer][activeUnit].y, 50, 50], 2)
                            
                        whereToX = i1
                        whereToY = i2
                        blocked = roadBlocked()
                        if (i1 == units[opponent][i3].x and i2 == units[opponent][i3].y and attacking == False) or blocked:
                            pygame.draw.rect(screen, (255, 255, 255), [200+50*i1, 25+50*i2, 50, 50])#tegn hvidt felt hvis der er en fjende
                            break
                    i3 = i3+1
                gameboard[i1][i2] = pygame.draw.rect(screen, (0, 0, 0), [200+50*i1, 25+50*i2, 50, 50], 2)
                i2 = i2+1
            i1 = i1 + 1
        #tegn unit description
        pos2 = pygame.mouse.get_pos()
        if selectUnit == True:
            UI_uinfo(activePlayer, activeUnit)
        i1 = 0
        while i1<12:
            i2 = 0
            while i2<11:
                if gameboard[i1][i2].collidepoint(pos2):
                    i3 = 0
                    while i3<2:
                        i4 = 0
                        while i4<15:
                            if units[i3][i4].x == i1 and units[i3][i4].y == i2:
                                if selectUnit == True and activePlayer == i3:
                                    i = 0
                                else:
                                    UI_uinfo(i3, i4)
                            i4=i4+1
                        i3 = i3+1
                        
                i2=i2+1
            i1=i1+1
        #tegn enheder
        i1 = 0
        while i1<2:
            i2 = 0
            while i2 < 15:
                if i1 == 0:
                    if units[i1][i2].typ == "T":
                        if units[i1][i2].face == "north":
                            img = pygame.image.load('sprites/tankbluN.png')
                        elif units[i1][i2].face == "south":
                            img = pygame.image.load('sprites/tankbluS.png')
                        elif units[i1][i2].face == "east":
                            img = pygame.image.load('sprites/tankbluE.png')
                        elif units[i1][i2].face == "west":
                            img = pygame.image.load('sprites/tankbluW.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "I":
                        if units[i1][i2].hp > 80:
                            img = pygame.image.load('sprites/InfBlu5.png')
                        elif units[i1][i2].hp > 60:
                            img = pygame.image.load('sprites/InfBlu4.png')
                        elif units[i1][i2].hp > 40:
                            img = pygame.image.load('sprites/InfBlu3.png')
                        elif units[i1][i2].hp > 20:
                            img = pygame.image.load('sprites/InfBlu2.png')
                        elif units[i1][i2].hp <= 20:
                            img = pygame.image.load('sprites/InfBlu1.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "R":
                        if units[i1][i2].hp > 80:
                            img = pygame.image.load('sprites/RBlue5.png')
                        elif units[i1][i2].hp > 60:
                            img = pygame.image.load('sprites/RBlue4.png')
                        elif units[i1][i2].hp > 40:
                            img = pygame.image.load('sprites/RBlue3.png')
                        elif units[i1][i2].hp > 20:
                            img = pygame.image.load('sprites/RBlue2.png')
                        elif units[i1][i2].hp <= 20:
                            img = pygame.image.load('sprites/RBlue1.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "A":
                        if units[i1][i2].face == "north":
                            img = pygame.image.load('sprites/ABluN.png')
                        elif units[i1][i2].face == "south":
                            img = pygame.image.load('sprites/ABluS.png')
                        elif units[i1][i2].face == "east":
                            img = pygame.image.load('sprites/ABluE.png')
                        elif units[i1][i2].face == "west":
                            img = pygame.image.load('sprites/ABluW.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                elif i1 == 1:
                    if units[i1][i2].typ == "T":
                        if units[i1][i2].face == "north":
                            img = pygame.image.load('sprites/tankredN.png')
                        elif units[i1][i2].face == "south":
                            img = pygame.image.load('sprites/tankredS.png')
                        elif units[i1][i2].face == "east":
                            img = pygame.image.load('sprites/tankredE.png')
                        elif units[i1][i2].face == "west":
                            img = pygame.image.load('sprites/tankredW.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "I":
                        if units[i1][i2].hp > 80:
                            img = pygame.image.load('sprites/InfRed5.png')
                        elif units[i1][i2].hp > 60:
                            img = pygame.image.load('sprites/InfRed4.png')
                        elif units[i1][i2].hp > 40:
                            img = pygame.image.load('sprites/InfRed3.png')
                        elif units[i1][i2].hp > 20:
                            img = pygame.image.load('sprites/InfRed2.png')
                        elif units[i1][i2].hp <= 20:
                            img = pygame.image.load('sprites/InfRed1.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "R":
                        if units[i1][i2].hp > 80:
                            img = pygame.image.load('sprites/RRed5.png')
                        elif units[i1][i2].hp > 60:
                            img = pygame.image.load('sprites/RRed4.png')
                        elif units[i1][i2].hp > 40:
                            img = pygame.image.load('sprites/RRed3.png')
                        elif units[i1][i2].hp > 20:
                            img = pygame.image.load('sprites/RRed2.png')
                        elif units[i1][i2].hp <= 20:
                            img = pygame.image.load('sprites/RRed1.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                    if units[i1][i2].typ == "A":
                        if units[i1][i2].face == "north":
                            img = pygame.image.load('sprites/ARedN.png')
                        elif units[i1][i2].face == "south":
                            img = pygame.image.load('sprites/ARedS.png')
                        elif units[i1][i2].face == "east":
                            img = pygame.image.load('sprites/ARedE.png')
                        elif units[i1][i2].face == "west":
                            img = pygame.image.load('sprites/ARedW.png')
                        if units[i1][i2].hp > 0:
                            screen.blit(img,(200+50*units[i1][i2].x,25+50*units[i1][i2].y))
                i2 = i2+1
            i1 = i1+1
        #tegn action points
        i2 = 0
        while i2<actionsP1:
            pygame.draw.circle(screen, (0, 0, 0), [25+i2*25, 50], 10)
            i2 = i2+1
        i2 = 0
        while i2<actionsP2:
            pygame.draw.circle(screen, (0, 0, 0), [975+i2*-25, 50], 10)
            i2 = i2+1
		
    pygame.display.flip() #tegn skærmen

def victory():
    global units
    dead = 0
    i1 = 0
    end = False
    while i1 <2:
        i2 = 0
        while i2 < 15:
            if units[i1][i2].x == 57005:
                dead = dead +1
            i2 = i2 + 1
        if dead == 15 and i1 == 0:
            end = True
            return 'blueIsDead'
        elif dead == 15 and i1 == 1:
            end = True
            return 'redIsDead'
            
        dead = 0
        i1 = i1 + 1
    if end == False:
        return 'noOneIsDead'

    
#kør kode
while 1:
    initUnits()
    placeUnits()
    tfont = pygame.font.SysFont("arial", 72)
    font = pygame.font.SysFont("arial", 54)
    ttfont = pygame.font.SysFont("arial", 18)
    UI()
    while 1:
        if menu[:4] == "menu":
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if menu == "menuMain":
                        if UI.main_play.collidepoint(pos):
                            menu = "gameboard"
                        elif UI.main_rules.collidepoint(pos):
                            menu = "menuRules"
                        elif UI.main_quit.collidepoint(pos):
                            pygame.quit()
                    elif menu == "menuVictory":
                        if UI.victory_main.collidepoint(pos):
                            menu = "menuMain"
                    elif menu == "menuRules":
                        if UI.rules_back.collidepoint(pos):
                            menu = "menuMain"
                        if UI.rules_attacking.collidepoint(pos):
                            menu = "menuRSubatk"
                        if UI.rules_movement.collidepoint(pos):
                            menu = "menuRSubmov"
                        if UI.rules_stats.collidepoint(pos):
                            menu = "menuRSubstat"
                        if UI.rules_cmd.collidepoint(pos):
                            menu = "menuRSubcmd"
                    elif menu[:8] == "menuRSub":
                        if UI.rules_back.collidepoint(pos):
                            menu = "menuRules"
                    UI()
        while menu == "gameboard":
            end = victory()
            if end == "blueIsDead":
                menu = "menuVictory"
                break
            if end == "redIsDead":
                menu = "menuVictory"
                break
            if (actionsP2 == 0 or actionsP1 == 0) and selectUnit == False:
                i1 = 0
                while i1 < 2:
                    i2 = 0
                    while i2<15:
                        units[i1][i2].mt = 0
                        i2 = i2+1
                    i1 = i1+1
            if actionsP1 == 0 and selectUnit == False:
                actionsP1 = 6
                activePlayer = 1
            elif actionsP2 == 0 and selectUnit == False:
                actionsP2 = 6
                activePlayer = 0
            UI()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if turning:
                        turningVeh()
                    elif attacking:
                        attack(pos) #passer pos ind i dmg formula og find target
                    elif UI.gameboard_endturn.collidepoint(pos):
                        if activePlayer == 0:
                            actionsP1 = 0
                        else:
                            actionsP2 = 0
                    else:
                        checkTile(pos)
