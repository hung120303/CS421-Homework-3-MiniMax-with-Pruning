import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

# Title: CS421-Homework-3-MiniMax-with-Alpha-Beta-Pruning
# @authors - Nick Tabra, Hung Vu
# @date - 10/7/2025

# File copied from Random.py and modified

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Random")
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];
            
        return selectedMove
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass


    ##
    #
    #miniMax
    #Description: Takes an initial node, runs a minimax algorithm by searching 3 levels (moves) ahead
    #             and returns the best move?
    #
    #Parameters:
    #   initNode - the inital node
    #   depth - the depth to look down (how many moves ahead)
    #
    #Returns: a node
    def miniMax(self, initNode, depth):
        if depth == 0: # If the depth is 0, we've reached the goal depth
            return initNode
        elif depth >= 1:
            # We first get all the moves possible from the current state
            initState = initNode["state"]
            initDepth = initNode["depth"]
            allLegalMoves = listAllLegalMoves(initState)

            nodeList = []
            for move in allLegalMoves:
                nextState = getNextStateAdversarial(initState, move)
                nextNode = self.makeNode(move, nextState, initDepth, initNode)
                nodeList.append(nextNode)


            # Need to update bestMove based on whose turn it is
            # If it's our turn, we want the node with the most negative score
            # If it's their turn, they'll take the node with the most positive score
            # Right now bestMove get's the lowest evaluated node
            whoseTurn = initState.whoseTurn
            bestNode = None
            if whoseTurn == 0: # our turn
                bestNode = self.bestMove(nodeList) 
            else: # their turn
                bestNode = self.bestMove(nodeList)

            # recurse till we get to depth
            return self.miniMax(bestNode, depth - 1)




    ##
    # makeNode
    # description: creates a search tree node (copied from HW#2)
    #
    # paramaters:
    # move - move taken from parent state
    # state - resulting gamestate after the move
    # depth - depth in the search tree
    # parent - parent node (or none if the root)
    #
    # returns dict representing the node
    ##
    def makeNode(self, move, state, depth, parent):
        return{
            "move": move,
            "state": state,
            "depth": depth,
            "eval": self.utility(state) + depth, 
            "parent": parent
        }
    
    ##
    # bestNode
    # Description: finds the node with the best evaluation (utility) (copied from HW#2)
    #
    # Parameters: 
    # nodeList - the list of nodes to search 
    #
    # Returns: our "node" representation
    def bestMove(self, nodeList):
        # Type checking
        if not isinstance(nodeList, list):
            print("bestMove: ", nodeList , " is not a list of node")
            return None

        # start with the first node as the best
        bestNode = nodeList[0]

        # List to track nodes that have equal evaluation to the best node
        bestList = []

        # go through each node in the list
        for node in nodeList:
            # if this node has a smaller eval score than our current best
            if node["eval"] < bestNode["eval"]:
                #update bestNode
                bestNode = node
                #clear the list equal and best nodes (a new best node is found, so no similar nodes)
                bestList.clear()
            elif node["eval"] == bestNode["eval"]:
                bestList.append(node)
        
        # If we have multiple best nodes, randomly choose between them (avoid cycling moves)
        if len(bestList) > 0 :
            bestList.append(bestNode)
            return bestList[random.randint(0, len(bestList) - 1)]
        else:
            # There's only one best node    
            return bestNode
