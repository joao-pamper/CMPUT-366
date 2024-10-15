import heapq

def a_star_search(initial_state, goal_state, map):
    """
    Performs A* search in given map with known initial and goal states.
    """
    open_heap = []
    closed_dict = {}
    expansions = 0
    
    #Update cost for initial state
    initial_state.set_cost(initial_state.get_g() + h_value(initial_state, goal_state))
    
    #Insert initial state to open and closed
    heapq.heappush(open_heap, initial_state)
    closed_dict[initial_state.state_hash()] = initial_state.get_cost()

    while len(open_heap) > 0:
        expansions += 1
        n = heapq.heappop(open_heap)
        
        if n == goal_state: 
            return n.get_cost(), expansions
        
        #Get all children
        successors = map.successors(n)
        
        for child in successors:

            #calculate f-value of child
            f_value = child.get_g() + h_value(child, goal_state)
            #update cost of state 
            child.set_cost(f_value)

            #if child has not been seen
            if child.state_hash() not in closed_dict or child.get_cost() < closed_dict[child.state_hash()]:
                
                #update cost of state 
                child.set_cost(f_value)
                
                #Add to open and closed
                heapq.heappush(open_heap, child)
                closed_dict[child.state_hash()] = child.get_cost()

    return -1, expansions

def h_value(current_state, goal_state):
    """
    Will calculate the Octile distance from current state to goal state.
    """
    delta_x = abs(current_state.get_x() - goal_state.get_x())
    delta_y = abs(current_state.get_y() - goal_state.get_y())

    h = 1.5 * min(delta_x, delta_y) + abs(delta_x - delta_y)

    return h