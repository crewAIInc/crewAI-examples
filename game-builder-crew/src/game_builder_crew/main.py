import sys
from game_builder_crew.crew import GameBuilderCrew

def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    print("## Welcome to the Game Crew")
    print('-------------------------------')
    
    #examples = './input_examples.yaml'
    
    inputs = {
        'game' :  """
                        Game Overview:

                        Pac-Man is a classic arcade game where the player controls a character, Pac-Man, through a maze. The objective is to eat all the pellets in the maze while avoiding four ghosts that pursue Pac-Man. If Pac-Man eats a large power pellet, the ghosts turn blue, and Pac-Man can eat them for extra points. The game is over when Pac-Man is caught by a ghost or when the player runs out of lives.
                        Core Game Elements:

                            Maze Layout:
                                The game is set within a grid-like maze. The walls are solid, and Pac-Man cannot pass through them.
                                The maze contains corridors where Pac-Man can move in four directions: up, down, left, and right. Some sections of the maze loop back on themselves.
                                The maze contains two types of special tiles:
                                    Pellets: Small dots scattered throughout the maze, worth 10 points each.
                                    Power Pellets: Larger dots placed in the four corners of the maze, worth 50 points each. Eating a Power Pellet allows Pac-Man to eat the ghosts for a limited time.

                            Player Controls:
                                The player controls Pac-Man's movement using arrow keys (or other directional inputs, such as WASD).
                                Pac-Man moves continuously in the chosen direction until blocked by a wall or until the player changes direction.
                                Pac-Man cannot stop moving, so the player must carefully time movements and changes in direction.

                            Pac-Man Mechanics:
                                Movement: Pac-Man moves one tile at a time in a grid-based movement system.
                                Collision Detection: Pac-Man collides with walls, pellets, power pellets, and ghosts. Pac-Man cannot pass through walls.
                                Pellet Collection: When Pac-Man moves onto a tile containing a pellet, it is "eaten," and the pellet disappears.
                                Power Pellet Effects: Eating a Power Pellet allows Pac-Man to turn the ghosts blue for a short period (usually 7-10 seconds). During this time, Pac-Man can eat the ghosts for extra points. Ghosts revert to their regular form after the time limit.

                            Ghosts:
                                There are four ghosts: Blinky, Pinky, Inky, and Clyde. Each has a distinct behavior pattern:
                                    Blinky (Red Ghost): Aggressively pursues Pac-Man, always targeting his current location.
                                    Pinky (Pink Ghost): Attempts to ambush Pac-Man by aiming four tiles ahead of Pac-Man’s current direction.
                                    Inky (Cyan Ghost): Has a more complex behavior, targeting an area between Pac-Man and Blinky’s current location.
                                    Clyde (Orange Ghost): Alternates between chasing Pac-Man and wandering randomly when he gets too close to Pac-Man.
                                Ghost Movement: Ghosts move one tile at a time, just like Pac-Man, and they can change directions at intersections. Their goal is to catch Pac-Man.
                                Ghost States:
                                    Chase Mode: Ghosts actively pursue Pac-Man based on their unique behavior patterns.
                                    Scatter Mode: Ghosts move to specific corners of the maze, where they “scatter” and remain for a brief period before returning to Chase mode.
                                    Frightened Mode: After Pac-Man eats a Power Pellet, ghosts turn blue and flee from Pac-Man. In this mode, Pac-Man can eat them for extra points. When a ghost is eaten, it respawns at the center of the maze and resumes chasing Pac-Man.

                            Scoring System:
                                Eating a pellet: 10 points.
                                Eating a Power Pellet: 50 points.
                                Eating a ghost (in Frightened mode):
                                    First ghost: 200 points.
                                    Second ghost: 400 points.
                                    Third ghost: 800 points.
                                    Fourth ghost: 1600 points.
                                Clearing a level (eating all the pellets): Bonus points for completing the level.

                            Lives and Game Over:
                                Pac-Man starts the game with 3 lives.
                                If a ghost touches Pac-Man while in its normal or chase mode, Pac-Man loses a life.
                                When all lives are lost, the game ends.

                            Level Progression:
                                After all pellets and Power Pellets are consumed in the maze, Pac-Man progresses to the next level.
                                Each new level increases the game difficulty, making the ghosts move faster.
                                At higher levels, the time that ghosts remain blue after eating a Power Pellet decreases, eventually reaching a point where they no longer turn blue.

                            Warp Tunnels:
                                The maze has two special tunnels on the left and right edges that act as "warp tunnels."
                                When Pac-Man or the ghosts enter one side, they instantly reappear on the opposite side of the maze.

                        Mechanics Used in the Game:

                            Tile-Based Movement:
                                The entire game operates on a grid, where each movement happens from one tile to another. Both Pac-Man and the ghosts must follow the grid's structure.

                            Pathfinding (Ghost AI):
                                The ghosts use basic pathfinding algorithms to chase Pac-Man. One common method for this is the A algorithm* or a simplified greedy algorithm to determine the shortest path toward Pac-Man.
                                Each ghost has its unique targeting behavior, ranging from direct pursuit to attempting ambush strategies.

                            State Management:
                                Pac-Man's State: Handles whether Pac-Man is in a normal state, Power Pellet state (can eat ghosts), or has collided with a ghost.
                                Ghosts’ State: Manages transitions between three ghost states:
                                    Chase State: Actively chasing Pac-Man.
                                    Scatter State: Retreats to their designated corners.
                                    Frightened State: Turns blue and flees from Pac-Man, allowing Pac-Man to eat them.

                            Collision Detection:
                                Pellets and Pac-Man: When Pac-Man’s position matches a pellet's position, the pellet is eaten.
                                Ghosts and Pac-Man: When Pac-Man’s position matches a ghost’s position:
                                    If the ghost is in Frightened mode, Pac-Man eats the ghost.
                                    If the ghost is in Chase or Scatter mode, Pac-Man loses a life.

                            Timer and Speed Control:
                                The game runs on a time-based loop where Pac-Man and the ghosts move at set intervals.
                                Ghosts' speeds increase over time, making higher levels more difficult.

                            Level Design and Randomness:
                                While the layout of the maze stays the same, the randomness in ghost behavior and increasing speed add variability to each playthrough.

                            Game Over Conditions:
                                When Pac-Man has no remaining lives, the game ends, displaying a "Game Over" screen.
                                The players final score is shown"""
    }
    game= GameBuilderCrew().crew().kickoff(inputs=inputs)

    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("final code for the game:")
    print(game)
    

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'game' : 'hello world'
    }
    try:
        GameBuilderCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
