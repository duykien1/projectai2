# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"


        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        score = successorGameState.getScore()

        # Thức ăn: càng gần hạt gần nhất càng tốt (dùng nghịch đảo)
        foodList = newFood.asList()
        if foodList:
            minFood = min(manhattanDistance(newPos, f) for f in foodList)
            score += 1.0 / (minFood + 1)
        score -= 0.5 * len(foodList)

        # Ma
        for ghost, scaredTime in zip(newGhostStates, newScaredTimes):
            d = manhattanDistance(newPos, ghost.getPosition())
            if scaredTime > d:
                # ma còn sợ đủ lâu: lại gần để ăn
                score += 2.0 / (d + 1)
            elif d <= 1:
                score -= 500
            else:
                score -= 1.0 / d

        if action == Directions.STOP:
            score -= 5

        return score
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()

        def value(state, agent, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            nextAgent = (agent + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth
            values = [value(state.generateSuccessor(agent, a), nextAgent, nextDepth)
                      for a in actions]
            return max(values) if agent == 0 else min(values)

        bestScore, bestAction = float('-inf'), None
        for action in gameState.getLegalActions(0):
            score = value(gameState.generateSuccessor(0, action), 1, 0)
            if score > bestScore:
                bestScore, bestAction = score, action
        return bestAction
        util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()

        def value(state, agent, depth, alpha, beta):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            nextAgent = (agent + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth

            if agent == 0:  # MAX
                v = float('-inf')
                for a in state.getLegalActions(agent):
                    v = max(v, value(state.generateSuccessor(agent, a),
                                     nextAgent, nextDepth, alpha, beta))
                    if v > beta:
                        return v
                    alpha = max(alpha, v)
                return v
            else:           # MIN
                v = float('inf')
                for a in state.getLegalActions(agent):
                    v = min(v, value(state.generateSuccessor(agent, a),
                                     nextAgent, nextDepth, alpha, beta))
                    if v < alpha:
                        return v
                    beta = min(beta, v)
                return v

        alpha, beta = float('-inf'), float('inf')
        bestScore, bestAction = float('-inf'), None
        for action in gameState.getLegalActions(0):
            score = value(gameState.generateSuccessor(0, action), 1, 0, alpha, beta)
            if score > bestScore:
                bestScore, bestAction = score, action
            alpha = max(alpha, bestScore)
        return bestAction
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()

        def value(state, agent, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            nextAgent = (agent + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth
            values = [value(state.generateSuccessor(agent, a), nextAgent, nextDepth)
                      for a in actions]
            if agent == 0:
                return max(values)
            return sum(values) / len(values)

        bestScore, bestAction = float('-inf'), None
        for action in gameState.getLegalActions(0):
            score = value(gameState.generateSuccessor(0, action), 1, 0)
            if score > bestScore:
                bestScore, bestAction = score, action
        return bestAction
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    if currentGameState.isWin() or currentGameState.isLose():
        return currentGameState.getScore()

    pos = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    capsules = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()

    score = currentGameState.getScore()

    # Thức ăn
    if foodList:
        minFood = min(manhattanDistance(pos, f) for f in foodList)
        score += 2.0 / (minFood + 1)
    score -= 4.0 * len(foodList)

    # Thuốc
    score -= 15.0 * len(capsules)
    if capsules:
        minCap = min(manhattanDistance(pos, c) for c in capsules)
        score += 1.0 / (minCap + 1)

    # Ma
    for ghost in ghostStates:
        d = manhattanDistance(pos, ghost.getPosition())
        if ghost.scaredTimer > d:
            score += 20.0 / (d + 1)
        elif d <= 1:
            score -= 200
        elif d <= 3:
            score -= 10.0 / d

    return score
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
