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

import math

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
        super(AIPlayer,self).__init__(inputPlayerId, "EpicAgentName")
    
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
        depth = 3
        root = self.makeNode(None, currentState, 0, None)
        bestMove = None
        bestVal = -math.inf

        children = self.expandNode(root)
        if not children:
            return Move(END, None, None)


        for child in children:
            val = self.miniMax(child, depth-1, -math.inf, math.inf)
            if val > bestVal:
                bestVal = val
                bestMove = child["move"]

        #fallback in case nothing gets chosen
        if bestMove is None:
            return Move(END, None, None)
        
        return bestMove

    
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
    #Description: Takes an initial node, runs a minimax algorithm, adjusting the eval of the nodes
    #
    #Parameters:
    #   initNode - the inital node
    #   depth - the depth to look down (how many moves ahead)
    #   maximizing - 0-1 val (0 if we are max, 1 if were min)
    #
    #Return:
    #   best child node
    ## ========================================================= ##
    ##                     MINIMAX WITH α-β                      ##
    ## ========================================================= ##
    def miniMax(self, node, depth, alpha, beta):
        state = node["state"]

        # Early stop if game over
        winner = getWinner(state)
        if depth == 0 or winner is not None:
            if winner == self.playerId:
                return 9999
            elif winner is not None:
                return -9999
            return self.utility(state)

        isMax = (state.whoseTurn == self.playerId)
        children = self.expandNode(node)
        if not children:
            return self.utility(state)

        if isMax:
            value = -math.inf
            for child in children:
                val = self.miniMax(child, depth - 1, alpha, beta)
                value = max(value, val)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # prune
            return value
        else:
            value = math.inf
            for child in children:
                val = self.miniMax(child, depth - 1, alpha, beta)
                value = min(value, val)
                beta = min(beta, value)
                if alpha >= beta:
                    break  # prune
            return value






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
    # maximizing - the current player's turn to choose for (for minimax)
    #
    # Returns: our "node" representation
    def bestMove(self, nodeList, maximizing):
        # Type checking
        if not isinstance(nodeList, list):
            print("bestMove: ", nodeList , " is not a list of node")
            return None
        # start with the first node as the best
        bestNode = nodeList[0]

        # List to track nodes that have equal evaluation to the best node
        bestList = []

        # (HW3) Get the node based on player turn max (us) vs mini (opp)

        # go through each node in the list
        if maximizing == PLAYER_ONE:
            for node in nodeList:
                # if this node has a smaller eval score than our current best
                if node["eval"] < bestNode["eval"]:
                    #update bestNode
                    bestNode = node
                    #clear the list equal and best nodes (a new best node is found, so no similar nodes)
                    bestList.clear()
                elif node["eval"] == bestNode["eval"]:
                    bestList.append(node)
        elif maximizing == PLAYER_TWO:
            for node in nodeList:
                # if this node has a bigger eval score than our current best
                if node["eval"] > bestNode["eval"]:
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

    ##
    # expandNode
    # Description: takes an existing node and return a list of nodes (copied from hw2)
    #
    # Parameters:
    # initNode - the initial node
    #
    # Returns: list of nodes
    ## ========================================================= ##
    ##                  EXPAND NODE (TOP N%)                     ##
    ## ========================================================= ##
    def expandNode(self, initNode, top_percent=0.5):
        if initNode is None:
            return None
        moves = listAllLegalMoves(initNode["state"])
        if not moves:
            return None

        nodes = []
        for m in moves:
            nextState = getNextStateAdversarial(initNode["state"], m)
            node = self.makeNode(m, nextState, initNode["depth"] + 1, initNode)
            nodes.append(node)

        # Sort by eval (higher is better for us)
        nodes.sort(key=lambda n: n["eval"], reverse=True)
        keep = max(1, int(len(nodes) * top_percent))
        return nodes[:keep]


    ## 
    #utility
    #Description: Looks at a GameState object and gives a 
    #   heuristic guess of good the game state is. 
    #   Estimates # of moves to reach its goal from current state (copied from HW2)
    #
    #Parameters:
    #   currentState - The current GameState object
    #   
    #Returns: number of moves to get to the goal state
    def utility(self, currentState):
        # Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        enemyInv = getEnemyInv(self, currentState)
        
        # Get the three ways of winning, we want to return the method of
        # winning that will take the least ammount of moves

        foodTurns = 0
        queenTurns = 0
        anthillTurns = 0

        ######
        #FOOD#
        ######

        myWorkerList = getAntList(currentState, myInv.player, (WORKER,))
        myFood = getCurrPlayerFood(self, currentState)
        myFoodCount = myInv.foodCount
        numWorkers = len(myWorkerList)
        myAntHill = myInv.getAnthill()
        myTunnel = myInv.getTunnels()[0]

        enemyWorkerList = getAntList(currentState, enemyInv.player, (WORKER,))
        enemyFoodCount = enemyInv.foodCount
        numEnemyWorkers = len(enemyWorkerList)
        enemyAntHill = enemyInv.getAnthill()
        enemyTunnel = enemyInv.getTunnels()[0]

        # Catch error when starting game (the food doesn't exist yet)
        if len(myFood) == 0:
            return -1

        # Food win/loss
        if myFoodCount == FOOD_GOAL:
            return -math.inf
        elif enemyFoodCount == FOOD_GOAL:
            return math.inf
        
        foodTurns = (FOOD_GOAL - myFoodCount) * 5

        # If we have no workers, it's impossible to win off food
        if numWorkers == 0:
            foodTurns += 100
        elif numWorkers == 1:
            foodTurns -= 10
        else: # Too many workers
            foodTurns += 100

        # Impact based on enemy worker
        if foodTurns != math.inf and numEnemyWorkers >= 1:
            foodTurns = foodTurns + math.ceil(foodTurns*numEnemyWorkers / 2)

        # Impact the turns based on if workers ants are carrying or not
        # Also impact based on how close they are to the food or tunnel/anthill based on that


        for worker in myWorkerList:
            # Workers should stay on our side
            if worker.coords[1] > 3:
                foodTurns += 1000
            if not worker.hasMoved:
                foodTurns += 10
            

            if worker.carrying:
                foodTurns -= 2
                bestDist = math.inf
                distFromTunnel = stepsToReach(currentState, worker.coords, myTunnel.coords)
                distFromAnthill = stepsToReach(currentState, worker.coords, myAntHill.coords)
                if distFromAnthill < distFromTunnel:
                    bestDist = distFromAnthill
                    bestCoords = myAntHill.coords
                else:
                    bestDist = distFromTunnel
                    bestCoords = myTunnel.coords
                # Greater distance means more turns to take
                if bestDist == 0:
                    foodTurns -= 15
                else:
                    foodTurns -= 12 - bestDist

            else:
                bestDist = math.inf
                distFromFoodOne = stepsToReach(currentState, worker.coords, myFood[0].coords)
                distFromFoodTwo = stepsToReach(currentState, worker.coords, myFood[1].coords)
                if distFromFoodTwo < distFromFoodOne:
                    bestDist = distFromFoodTwo
                    bestCoords = myFood[1].coords
                else:
                    bestDist = distFromFoodOne
                    bestCoords = myFood[0].coords

                # Greater distance means more turns to take
                if bestDist == 0:
                    foodTurns -= 15
                else:
                    foodTurns -= 12 - bestDist 

            # If they're close to enemies, punish that harshly
            adjacentToWorker = listAdjacent(worker.coords)
            for coord in adjacentToWorker:
                ant = getAntAt(currentState, coord)
                if ant != None and ant.player == PLAYER_TWO:
                    foodTurns += 2 * approxDist(worker.coords, ant.coords)
        
        ## Combat ##
        score = 0

        # --- Queen logic --- #
        myQueen = myInv.getQueen()
        enemyQueen = enemyInv.getQueen()
        if myQueen and enemyQueen:
            distToEnemyQueen = stepsToReach(currentState, myQueen.coords, enemyQueen.coords)
            score += (10 - enemyQueen.health) * 20

            #encourage leaving anthill but staying close
            if myQueen.coords == myAntHill.coords:
                score -= 10
            else:
                score += 5


            if myQueen.health > 6 and distToEnemyQueen < 7:
                score += 8

            #defend base
            if myAntHill.captureHealth <= 1:
                score -= 15

        #########
        #ANTHILL#
        #########

        anthillHealthDifference = enemyAntHill.captureHealth - myAntHill.captureHealth

        # For a anthill win, estimate that it'll take 30 turns to reduce 1 health
        anthillTurns = 30 * enemyAntHill.captureHealth
        attackAntList = getAntList(currentState, myInv.player, (QUEEN, SOLDIER, DRONE, R_SOLDIER))
        enemyAntList = getAntList(currentState, enemyInv.player, (SOLDIER, DRONE, R_SOLDIER, WORKER, QUEEN))

        antTypeCount = [0,0,0,0,0] 

        combatScore = (len(enemyAntList)*2 - len(attackAntList))*10
        for attackAnt in attackAntList:
            if attackAnt.hasMoved:
                combatScore -= 5
            else:
                combatScore += 5

            # Good if our ants are towards the enemy
            if attackAnt.coords[1] >= 5:
                combatScore -= 2
            # Find the closest enemy and worker
            closestEnemy = None
            closestWorker = None
            shortestDist = math.inf
            for enemy in enemyAntList:
                enemyDist = stepsToReach(currentState, enemy.coords, attackAnt.coords)
                if closestEnemy == None or enemyDist < shortestDist:
                    shortestDist = enemyDist
                    closestEnemy = enemy
                    if enemy.type == WORKER:
                        closestWorker = enemy

            if closestEnemy == None:
                break
            # Unique combat for each ant type
            if attackAnt.type == QUEEN:
                if attackAnt.health <= 4:
                    # Run away when low
                    combatScore -= shortestDist
                elif closestEnemy.type != WORKER:
                    combatScore += shortestDist
                for coord in listReachableAdjacent(currentState, attackAnt.coords, UNIT_STATS[QUEEN][MOVEMENT]):
                    if getAntAt(currentState, coord) != None and getAntAt(currentState, coord).type == WORKER:
                        foodTurns -= 3
            elif attackAnt.type == DRONE: # get workers
                if closestWorker != None:
                    combatScore += approxDist(attackAnt.coords, closestWorker.coords)
                else:
                    combatScore += shortestDist
            elif attackAnt.type == R_SOLDIER:
                if UNIT_STATS[R_SOLDIER][RANGE] == shortestDist:
                    combatScore -= 1
                else:
                    combatScore += shortestDist
            elif attackAnt.type == SOLDIER:
                combatScore += shortestDist
        
            # If we're within range the enemies next move, bad
            if enemyDist <= UNIT_STATS[enemy.type][MOVEMENT] and closestEnemy.type != WORKER:
                combatScore += 1

            # If we can kill the closest ant, good
            if (attackAnt.type != R_SOLDIER and
                attackAnt.coords in listAdjacent(closestEnemy.coords) and
                UNIT_STATS[attackAnt.type][ATTACK] >= closestEnemy.health):
                combatScore -= 10

            # If we;re on the enenmy anthill, good
            if attackAnt.coords == enemyAntHill.coords:
                combatScore -= 10
            
            if approxDist(attackAnt.coords, enemyTunnel.coords) <= 3:
                combatScore -= 1

            # Protect the anthill when hp low
            if myAntHill.captureHealth == 1 and attackAnt.coords == myAntHill.coords:
                combatScore -= 5
            # When it's not low we get off important structures
            elif (attackAnt.coords == myTunnel.coords or
                attackAnt.coords == myFood[0].coords or attackAnt.coords == myFood[1].coords):
                combatScore += 10

        numDrones = len(getAntList(currentState, myInv.player, (DRONE,)))
        numSoldiers = len(getAntList(currentState, myInv.player, (SOLDIER,)))
        numR_Soldiers = len(getAntList(currentState, myInv.player, (R_SOLDIER,)))

        # Should have at least one troop
        if (numDrones + numSoldiers + numR_Soldiers) == 0:
            combatScore += 200

        # Have a drone against a worker
        if numDrones == 1 and numEnemyWorkers == 1:
            combatScore -= 5
        elif numEnemyWorkers == 0:
            combatScore -= 20

        # Have at least a soldier when enemy has threats
        if (numSoldiers == 0 and len(enemyAntList) != (numEnemyWorkers + 1)):
            combatScore += 5
        else:
            combatScore -= 10

        # Having at least one range and soldiers match the enemy count is good, other equal soldiers is good
        if numR_Soldiers == 1 and (numSoldiers - 1) == len(enemyAntList):
            combatScore -= 3
        elif numSoldiers == len(enemyAntList):
            combatScore -= 2


        bestGuess = min(queenTurns, anthillTurns, foodTurns) + combatScore + math.floor(foodTurns/4)
        
        if currentState.whoseTurn == PLAYER_TWO:
            return -bestGuess
        return bestGuess