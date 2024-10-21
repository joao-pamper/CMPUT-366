import copy
import heapq


class State:
    """
    Class to represent a state on grid-based pathfinding problems. The class contains two static variables:
    map_width and map_height containing the width and height of the map. Although these variables are properties
    of the map and not of the state, they are used to compute the hash value of the state, which is used
    in the CLOSED list.

    Each state has the values of x, y, g, h, and cost. The cost is used as the criterion for sorting the nodes
    in the OPEN list.
    """

    map_width = 0
    map_height = 0

    def __init__(self, x, y):
        """
        Constructor - requires the values of x and y of the state. All the other variables are
        initialized with the value of 0.
        """
        self._x = x
        self._y = y
        self._g = 0
        self._cost = 0
        self._parent = None

    def __repr__(self):
        """
        This method is invoked when we call a print instruction with a state. It will print [x, y],
        where x and y are the coordinates of the state on the map.
        """
        state_str = "[" + str(self._x) + ", " + str(self._y) + "]"
        return state_str

    def __lt__(self, other):
        """
        Less-than operator; used to sort the nodes in the OPEN list
        """
        return self._cost < other._cost

    def __hash__(self):
        """
        Given a state (x, y), this method returns the value of x * map_width + y. This is a perfect
        hash function for the problem (i.e., no two states will have the same hash value). This function
        is used to implement the CLOSED list of the algorithms.
        """
        return hash((self._y * State.map_width + self._x, self._g))

    def __eq__(self, other):
        """
        Method that is invoked if we use the operator == for states. It returns True if self and other
        represent the same state; it returns False otherwise.
        """
        return self._x == other._x and self._y == other._y and self._g == other._g

    def is_goal(self, goal):
        return self._x == goal._x and self._y == goal._y

    def get_x(self):
        """
        Returns the x coordinate of the state
        """
        return self._x

    def get_y(self):
        """
        Returns the y coordinate of the state
        """
        return self._y

    def get_g(self):
        """
        Returns the g-value of the state
        """
        return self._g

    def set_g(self, g):
        """
        Sets the g-value of the state
        """
        self._g = g

    def get_cost(self):
        """
        Returns the cost of a state; the cost is determined by the search algorithm
        """
        return self._cost

    def set_cost(self, cost):
        """
        Sets the cost of the state; the cost is determined by the search algorithm
        """
        self._cost = cost

    def set_parent(self, parent):
        """
        Defines the parent of a node in the A* search
        """
        self._parent = parent

    def get_parent(self):
        """
        Returns the parent of a node in the A* search
        """
        return self._parent

    def get_heuristic(self, target_state):
        """
        Returns the Manhattan distance heuristic between the state and the target state.
        """
        dist_x = abs(self.get_x() - target_state.get_x())
        dist_y = abs(self.get_y() - target_state.get_y())

        return dist_x + dist_y


class CBSState:

    def __init__(self, map, starts, goals):
        """
        Constructor of the CBS state. Initializes cost, constraints, maps, start and goal locations,
        number of agents, and the solution paths.
        """
        self._cost = 0
        self._constraints = {}
        self._map = map
        self._starts = starts
        self._goals = goals
        self._k = len(starts)

        # One dictionary of constraints for each agent
        for i in range(0, self._k):
            self._constraints[i] = {}

        self._paths = {}  # dict where key is i-th agent and value is list of

    def compute_cost(self):
        """
        Computes the cost of a CBS state. Assumes the sum of the cost of the paths as the objective function.
        """
        # compute solution path using a star for each agent i
        astar = AStar(self._map)
        for i in range(0, self._k):
            cost, path = astar.search(
                self._starts[i], self._goals[i], self._constraints[i]
            )
            # store each agent solution path in self._paths[i]
            self._paths[i] = path
            # add cost to sum
            self._cost += cost

        return self._paths, self._cost  # for debugging

        pass

    def is_solution(self):
        """
        Verifies whether a CBS state is a solution. If it isn't, it returns False and a tuple with
        the conflicting state and time step; returns True, None otherwise.
        """
        # loop through solution steps and check if any of the agents are at the same
        # state during the same time step

        # for each time step
        valid_solution = True
        time_step = 0
        agents_finished = 0
        conflict_tuple = None

        while agents_finished < self._k:
            step_set = set()
            agents_finished = 0
            # for each agent
            for i in range(0, self._k):
                # check if agent has a state in this time
                if time_step < len(self._paths[i]):
                    # get state of agent
                    current_state = self._paths[i][time_step]
                    # if so, check if any other agent is there at the same time
                    if current_state in step_set:
                        # add constraint
                        conflict_tuple = (current_state, current_state.get_g())
                        valid_solution = False
                    else:
                        step_set.add(current_state)
                else:
                    agents_finished += 1
            time_step += 1
        return valid_solution, conflict_tuple

    def successors(self):
        """
        Generates the two children of a CBS state that doesn't represent a solution.
        """
        successors_list = []
        valid, conflict_tuple = self.is_solution()
        if conflict_tuple is not None and valid is False:
            # we have to return a list of two state instances
            # find agents that were in conflict state during conflict time
            conflict_state = conflict_tuple[0]
            conflict_time = conflict_tuple[1]
            agents = []
            successors_list = []
            for i in range(0, self._k):
                # if agent exists during conflict time
                if conflict_time < len(self._paths[i]):
                    # if state of agent is the conflict state
                    if self._paths[i][conflict_time] == conflict_state:
                        # add agent to list of conflicting agents
                        agents.append(i)

            if len(agents) >= 2:
                # if agents exist, initialize them and add them to the list
                c1 = CBSState(self._map, self._starts, self._goals)
                c1._constraints = copy.deepcopy(self._constraints)
                c1.set_constraint(conflict_state, conflict_time, agents[0])
                successors_list.append(c1)

                c2 = CBSState(self._map, self._starts, self._goals)
                c2._constraints = copy.deepcopy(self._constraints)
                c2.set_constraint(conflict_state, conflict_time, agents[1])
                successors_list.append(c2)

            else:
                print("error creating childs since not enough conflicting agents found")

        return successors_list

    def set_constraint(self, conflict_state, conflict_time, agent):
        """
        Sets a constraint for agent in conflict_state and conflict_time
        """
        if (conflict_state.get_x(), conflict_state.get_y()) not in self._constraints[
            agent
        ]:
            self._constraints[agent][
                (conflict_state.get_x(), conflict_state.get_y())
            ] = set()

        self._constraints[agent][(conflict_state.get_x(), conflict_state.get_y())].add(
            conflict_time
        )

    def __repr__(self):
        """
        This method is invoked when we call a print instruction with a state.
        """
        state_str = str(self._constraints)
        return state_str

    def __lt__(self, other):
        """
        Less-than operator; used to sort the nodes in the OPEN list
        """
        return self._cost < other._cost

    def get_cost(self):
        """
        Returns the cost of a state
        """
        return self._cost

    def set_cost(self, cost):
        """
        Sets the cost of the state
        """
        self._cost = cost


class CBS:
    def search(self, start):
        """
        Performs CBS search for the problem defined in start.
        """
        return None, None


class AStar:

    def __init__(self, gridded_map):
        """
        Constructor of A*. Creates the datastructures OPEN and CLOSED.
        """
        self.map = gridded_map
        self.OPEN = []
        self.CLOSED = {}

    def compute_cost(self, state):
        """
        Computes the f-value of nodes in the A* search
        """
        state.set_cost(state.get_g() + state.get_heuristic(self.goal))

    def _recover_path(self, node):
        """
        Recovers the solution path A* finds.
        """
        path = []
        while node.get_parent() is not None:
            path.append(node)
            node = node.get_parent()
        path.append(node)
        return path[::-1]

    def search(self, start, goal, constraints=None):
        """
        A* Algorithm: receives a start state and a goal state as input. It returns the
        cost of a path between start and goal and the number of nodes expanded.

        If a solution isn't found, it returns -1 for the cost.
        """
        self.start = start
        self.goal = goal

        self.compute_cost(self.start)

        self.OPEN.clear()
        self.CLOSED.clear()

        heapq.heappush(self.OPEN, self.start)
        self.CLOSED[start.__hash__()] = self.start
        while len(self.OPEN) > 0:
            node = heapq.heappop(self.OPEN)

            if node.is_goal(self.goal):
                return node.get_g(), self._recover_path(node)

            children = self.map.successors(node, constraints)

            for child in children:
                hash_value = child.__hash__()
                self.compute_cost(child)
                child.set_parent(node)

                if hash_value not in self.CLOSED:
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[hash_value] = child

                if (
                    hash_value in self.CLOSED
                    and self.CLOSED[hash_value].get_g() > child.get_g()
                ):
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[hash_value] = child
        return -1, None
