from ast import List
import math
from game_state_abalone import GameStateAbalone
from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "final", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)

    
    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        max_depth = 4

        # Ajuster la profondeur selon le nombre de tours restants
        if max_depth + current_state.step > current_state.max_step:
            max_depth = 50 - current_state.step

        other_player = current_state.get_players()[1] if self != current_state.get_players()[1] else current_state.get_players()[0]
        
        def heuristic(state: GameStateAbalone):    
            score_h = abs(state.get_player_score(other_player)) + 2 * state.get_player_score(self)
            center_distance_h = 2 * distance_from_center(state,other_player) - distance_from_center(state,self)
            cohesion_h = cohesion(state,self) - 2 * cohesion(state,other_player)
            
            heuristic_value = 100000 * score_h + center_distance_h  + 10 * cohesion_h
            return heuristic_value

        # Maximizer
        def max_value(state: GameState, alpha:float, beta:float, depth:int):
            if depth >= max_depth or state.is_done():
                return Action(state, None)
            
            max_action: Action = Action(state, None)
            max_score: float = -math.inf

            action: Action
            for action in state.get_possible_actions():
                next_action: Action = min_value(action.get_next_game_state(), alpha, beta, depth + 1)                
                next_score = heuristic(next_action.get_current_game_state())

                if next_score >= max_score:
                    max_action = action
                    max_score = next_score
                    alpha = max(alpha, max_score)
                    
                if max_score >= beta: 
                    break
            
            return max_action

        # Minimizer
        def min_value(state: GameState, alpha:float, beta:float, depth:int):
            if depth >= max_depth or state.is_done():
                return Action(state, None)

            min_action: Action = Action(state, None)
            min_score: float = math.inf

            action: Action
            for action in state.get_possible_actions():
                next_action: Action = max_value(action.get_next_game_state(), alpha, beta, depth + 1)
                next_score = heuristic(next_action.get_current_game_state())

                if next_score <= min_score:
                    min_action = action
                    min_score = next_score
                    beta = min(beta, min_score)
                
                if min_score < alpha: 
                    break
            
            return min_action

        return max_value(current_state, -math.inf, math.inf, 0)
    

# Calcule la somme des distances de chaque piece d'un joueur. 
# La distance represente le nombre de déplacements requis afin d'atteindre la position du milieu (4,4)
def distance_from_center(state:GameStateAbalone, player: PlayerAbalone):
    grid: List[List[int]] = state.get_rep().get_grid()
    
    x_cm = 4
    y_cm = 4

    distance = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == player.get_piece_type():
                distance += max(abs(i - x_cm), abs(j - y_cm)) ** 4
            
    return distance

# Calcule la somme des pièces voisines de chaque piece d'un joueur. 
def cohesion(state:GameStateAbalone, player: PlayerAbalone):
    neighbors = 0

    env = state.get_rep().get_env()

    for x,y in env:
        piece_type = env.get((x,y)).get_type()
        
        if player.get_piece_type() == piece_type:
            neighbours_dict = state.get_neighbours(x,y)

            for key in neighbours_dict:
                neighbour = neighbours_dict.get(key)
                if neighbour[0] == piece_type:
                    neighbors += 1
                    
    return neighbors
