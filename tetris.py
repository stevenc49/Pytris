import os, sys
import random

import pygame #@UnresolvedImport
from pygame.sprite import Sprite #@UnresolvedImport

#Timing
FALL_DELAY = 500    #number of milliseconds before block falls (block speed)
LOCK_DELAY = 5      #number of frames a block waits on the ground before being locked

#Lengths
GAME_AREA_HEIGHT, GAME_AREA_WIDTH = 640, 400
BLOCK_MEDIAN = 20
BLOCK_WIDTH = BLOCK_MEDIAN * 2
LINE_WIDTH = 3
NUM_COLUMNS = GAME_AREA_WIDTH / BLOCK_WIDTH
NUM_ROWS = GAME_AREA_HEIGHT / BLOCK_WIDTH
CENTER = GAME_AREA_WIDTH / 2 - BLOCK_WIDTH

#Directions
UP      = 1
DOWN    = 2
LEFT    = 3
RIGHT   = 4
ROTATE  = 5

#Colors
BLUE = 0,61,245
GREEN = 51,255,102
RED = 255,51,102
YELLOW = 204,255,41
ORANGE = 255,204,51
CYAN = 51,255,204
PURPLE = 204,51,255
PINK = 255,51,204
BROWN = 184,138,0
WHITE = 255,255,255
BLACK = 0,0,0

BG_COLOR = 150, 150, 80
LINE_COLOR = BLACK


#Game Globals
clock = pygame.time.Clock()
screen = pygame.display.set_mode((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), 0, 32)


class Square:
    def __init__(self, color, pos):
        self.color = color
        self.x = pos[0]
        self.y = pos[1]
    
    def moveUp(self, occupiedGrid):
        self.y = self.y - 2*BLOCK_MEDIAN

    def moveDown(self, occupiedGrid):
        self.y = self.y + 2*BLOCK_MEDIAN

    def moveLeft(self, occupiedGrid):
        self.x = self.x - 2*BLOCK_MEDIAN

    def moveRight(self, occupiedGrid):
        self.x = self.x + 2*BLOCK_MEDIAN

    def rotate(self):
        """Clockwise"""
        old_x = self.x
        old_y = self.y
        self.x = -old_y
        self.y = old_x
    
    def rotateCCW(self):
        """Counter-clockwise"""
        old_x = self.x
        old_y = self.y
        self.x = old_y
        self.y = -old_x
    
    def settle(self, occupiedGrid):
        occupiedGrid[ pixelToGrid(self.x) ][ pixelToGrid(self.y) ] = self
    
    def unSettle(self, occupiedGrid):
        occupiedGrid[ pixelToGrid(self.x) ][ pixelToGrid(self.y) ] = None
    
    def drawSquare(self):
        corners = []
        corners.append( (self.x-BLOCK_MEDIAN, self.y-BLOCK_MEDIAN) )
        corners.append( (self.x+BLOCK_MEDIAN, self.y-BLOCK_MEDIAN) )
        corners.append( (self.x+BLOCK_MEDIAN, self.y+BLOCK_MEDIAN) )
        corners.append( (self.x-BLOCK_MEDIAN, self.y+BLOCK_MEDIAN) )
        corners.append( (self.x-BLOCK_MEDIAN, self.y-BLOCK_MEDIAN) )
        
        screen.lock()
        pygame.draw.rect(screen, self.color, pygame.Rect((self.x-BLOCK_MEDIAN,self.y-BLOCK_MEDIAN), (2*BLOCK_MEDIAN,2*BLOCK_MEDIAN)))
        pygame.draw.lines(screen, LINE_COLOR, False, corners, LINE_WIDTH);
        screen.unlock()

class Block():
    def moveUp(self, occupiedGrid):
        if checkCollision(self.getSquares(), occupiedGrid, UP) == False:
            for square in self.squares:
                square.moveUp(occupiedGrid)
            self.center_y = self.center_y - 2*BLOCK_MEDIAN
    
    def moveDown(self, occupiedGrid):
        if checkCollision(self.getSquares(), occupiedGrid, DOWN) == False:
            for square in self.squares:
                square.moveDown(occupiedGrid)
            self.center_y = self.center_y + 2*BLOCK_MEDIAN
        
    def moveLeft(self, occupiedGrid):
        if checkCollision(self.getSquares(), occupiedGrid, LEFT) == False:
            for square in self.squares:
                square.moveLeft(occupiedGrid)
            self.center_x = self.center_x - 2*BLOCK_MEDIAN
    
    def moveRight(self, occupiedGrid):
        if checkCollision(self.getSquares(), occupiedGrid, RIGHT) == False:
            for square in self.squares:
                square.moveRight(occupiedGrid)
            self.center_x = self.center_x + 2*BLOCK_MEDIAN
    
    def rotate(self, occupiedGrid):
        #do rotation
        for square in self.squares:
            square.x -= self.center_x
            square.y -= self.center_y
            
            square.rotate()
            
            square.x += self.center_x
            square.y += self.center_y
        
        #if collision detected, just rotate back
        if checkCollision(self.getSquares(), occupiedGrid, ROTATE) == True:
            for square in self.squares:
                square.x -= self.center_x
                square.y -= self.center_y
                
                square.rotateCCW()
                
                square.x += self.center_x
                square.y += self.center_y

    def settle(self, occupiedGrid):
        for square in self.squares:
            square.settle(occupiedGrid)

    def drawBlock(self):
        for square in self.squares:
            square.drawSquare()

    def getSquares(self):
        return self.squares

    def printxy(self):
        for square in self.getSquares():
            print square.x, square.y, pixelToGrid(square.x), pixelToGrid(square.y)

class TBlock(Block):
    def __init__(self):
        color = BLUE
        self.center_x = 260
        self.center_y = 60
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y-2*BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y)))

class OBlock(Block):
    def __init__(self):
        color = WHITE
        self.center_x = 240
        self.center_y = 40
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x-BLOCK_MEDIAN,self.center_y-BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x+BLOCK_MEDIAN,self.center_y-BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x-BLOCK_MEDIAN,self.center_y+BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x+BLOCK_MEDIAN,self.center_y+BLOCK_MEDIAN)))

class IBlock(Block):
    def __init__(self):
        color = CYAN
        self.center_x = 260
        self.center_y = 60
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x,self.center_y-2*BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x,self.center_y+2*BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x,self.center_y+4*BLOCK_MEDIAN)))

class JBlock(Block):
    def __init__(self):
        color = PURPLE
        self.center_x = 260
        self.center_y = 60
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y-2*BLOCK_MEDIAN)))      

class LBlock(Block):
    def __init__(self):
        color = PINK
        self.center_x = 260
        self.center_y = 60
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y-2*BLOCK_MEDIAN)))    
        
class SBlock(Block):
    def __init__(self):
        color = YELLOW
        self.center_x = 260
        self.center_y = 20
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x,self.center_y+2*BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y+2*BLOCK_MEDIAN))) 

class ZBlock(Block):
    def __init__(self):
        color = ORANGE
        self.center_x = 260
        self.center_y = 20
        
        self.squares = []
        self.squares.append(Square(color, (self.center_x,self.center_y)))
        self.squares.append(Square(color, (self.center_x-2*BLOCK_MEDIAN,self.center_y)))
        self.squares.append(Square(color, (self.center_x,self.center_y+2*BLOCK_MEDIAN)))
        self.squares.append(Square(color, (self.center_x+2*BLOCK_MEDIAN,self.center_y+2*BLOCK_MEDIAN))) 

def checkCollision(squares, occupiedGrid, dir):
    for square in squares:
        #check wall collision
        if dir == UP:
            if square.y - 2*BLOCK_MEDIAN < 0:
                return True
        if dir == DOWN:
            if square.y + 2*BLOCK_MEDIAN > GAME_AREA_HEIGHT:
                return True
        if dir == LEFT:
            if square.x - 2*BLOCK_MEDIAN < 0:
                return True
        if dir == RIGHT:
            if square.x + 2*BLOCK_MEDIAN > GAME_AREA_WIDTH:
                return True
        if dir == ROTATE:
            if square.x < 0 or square.y < 0 or square.x > GAME_AREA_WIDTH or square.y > GAME_AREA_HEIGHT:
                return True
        
        #check collisions with occupied squares
        for x in range(0,NUM_COLUMNS):
            for y in range(0,NUM_ROWS):
                if dir == UP:
                    if occupiedGrid[pixelToGrid(square.x)][pixelToGrid(square.y - 2*BLOCK_MEDIAN)]:
                        return True
                if dir == DOWN:
                    if occupiedGrid[pixelToGrid(square.x)][pixelToGrid(square.y + 2*BLOCK_MEDIAN)]:
                        return True
                if dir == LEFT:
                    if occupiedGrid[pixelToGrid(square.x - 2*BLOCK_MEDIAN)][pixelToGrid(square.y)]:
                        return True
                if dir == RIGHT:
                    if occupiedGrid[pixelToGrid(square.x + 2*BLOCK_MEDIAN)][pixelToGrid(square.y)]:
                        return True
                if dir == ROTATE:
                    if occupiedGrid[pixelToGrid(square.x)][pixelToGrid(square.y)]:
                        return True
        
    return False

def pixelToGrid(pixel_coordinate):
    return (pixel_coordinate-BLOCK_MEDIAN)/BLOCK_WIDTH

class Tetris():
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Tetris')
        self.focusedBlock = self.getRandomBlock()
        pygame.time.set_timer(pygame.USEREVENT+1, FALL_DELAY)
        self.lockDelay = 0
        
        self.occupiedGrid = []
        for x in range(0,NUM_COLUMNS):
            self.occupiedGrid.append([])
            for y in range(0,NUM_ROWS):
                self.occupiedGrid[x].append( None )
        
        font = pygame.font.Font(None, 36)
        self.text = font.render("Hello There", 1, (10, 10, 10))
        self.textpos = self.text.get_rect()
        self.textpos.centerx = screen.get_rect().centerx
    
    def handleKeyboardEvents(self, focusedBlock, occupiedGrid):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            focusedBlock.moveUp(occupiedGrid)
        if keys[pygame.K_DOWN]:
            focusedBlock.moveDown(occupiedGrid)
        if keys[pygame.K_LEFT]:
            focusedBlock.moveLeft(occupiedGrid)
        if keys[pygame.K_RIGHT]:
            focusedBlock.moveRight(occupiedGrid)
        if keys[pygame.K_r]:
            focusedBlock.rotate(occupiedGrid)
        if keys[pygame.K_s]:
            focusedBlock.settle(occupiedGrid)
            self.focusedBlock = self.getRandomBlock()
            
        if keys[pygame.K_d]:
            self.debug()
        
    def draw(self, focusedBlock, occupiedGrid):
        #background
        screen.fill(BG_COLOR)
        
        #draw all occupiedGrids
        for x in range(0,NUM_COLUMNS):
            for y in range(0,NUM_ROWS):
                if self.occupiedGrid[x][y]:
                    self.occupiedGrid[x][y].drawSquare()
        
        #focusedBlock
        focusedBlock.drawBlock()
        
        screen.blit(self.text, self.textpos)
        
        #flip buffer
        pygame.display.flip()

    def getRandomBlock(self):
        blockType = random.randint(1,7)
        
        if blockType == 1:
            return TBlock()
        if blockType ==  2:
            return OBlock()
        if blockType == 3:
            return IBlock()
        if blockType ==  4:
            return JBlock()
        if blockType == 5:
            return LBlock()
        if blockType ==  6:
            return SBlock()
        if blockType == 7:
            return ZBlock()
    
    def debug(self):
        
#        self.focusedBlock.printxy()

        #print pretty grid
        for y in range(0,NUM_ROWS):
            row = ""
            for x in range(0,NUM_COLUMNS):
                if self.occupiedGrid[x][y]:
                    row+="1"
                else:
                    row+="0"
            print row
        
        print "filledRows: ", self.filledRows
        
    def clearLines(self, occupiedGrid):
        
        #detect full lines
        self.filledRows = []
        
        for j in range(0,NUM_ROWS):
            self.filled = True
            for i in range(0,NUM_COLUMNS):
                if self.occupiedGrid[i][j] == None:
                    self.filled = False
            if self.filled ==  True:
                self.filledRows.append(j)
        
        #erase full lines
        for j in self.filledRows:
            for i in range(0,NUM_COLUMNS):
                if self.occupiedGrid[i][j]:
                    self.occupiedGrid[i][j] = None
        
        #move down squares
        if self.filledRows:
            while self.filledRows:
                clearedRow = self.filledRows.pop()

                for j in range (clearedRow, -1, -1):
                    for i in range (0, NUM_COLUMNS):
                        if self.occupiedGrid[i][j]:
                            tempSquare = self.occupiedGrid[i][j]
                            tempSquare.unSettle(self.occupiedGrid)
                            tempSquare.moveDown(self.occupiedGrid)
                            tempSquare.settle(self.occupiedGrid)
    
    def handleGroundCollision(self, focusedBlock, occupiedGrid):
        if checkCollision(self.focusedBlock.squares, self.occupiedGrid, DOWN) == True:
            self.lockDelay += 1
            
        if self.lockDelay == LOCK_DELAY:
            self.focusedBlock.settle(self.occupiedGrid)
            self.focusedBlock = self.getRandomBlock()
            self.lockDelay = 0
    
    def loseCondition(self, focusedBlock, occupiedGrid):
        for i in range(0, NUM_COLUMNS):
            for j in range (0, NUM_ROWS):
                for square in focusedBlock.squares:
                    if occupiedGrid[pixelToGrid(square.x)][pixelToGrid(square.y)]:
                        return True
        return False
    
    def mainLoop(self):
        
        while True:
            clock.tick(10) #caps the number of iterations in this loop per second

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.USEREVENT+1:
                    self.focusedBlock.moveDown(self.occupiedGrid)
            
            self.handleGroundCollision(self.focusedBlock, self.occupiedGrid)

            self.handleKeyboardEvents(self.focusedBlock, self.occupiedGrid)
            
            self.clearLines(self.occupiedGrid)
            
            self.draw(self.focusedBlock, self.occupiedGrid)
            
            if self.loseCondition(self.focusedBlock, self.occupiedGrid):
                print "You Lost :-("

if __name__ == '__main__':
    
    tetris = Tetris()
    tetris.mainLoop()
