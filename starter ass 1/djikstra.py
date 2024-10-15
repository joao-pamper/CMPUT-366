import heapq

def djikstra_search(initial_state, goal_state, map):
    open_heap = []
    closed_dict = {}
    expansions = 0
    
    #Insert initial state to open and closed
    heapq.heappush(open_heap, initial_state)
    closed_dict[initial_state.state_hash()] = initial_state.get_cost()

    while len(open_heap) > 0:
        expansions += 1
        n = heapq.heappop(open_heap)
        
        if n == goal_state: 
            return n.get_cost(), expansions
        
        successors = map.successors(n)
        
        for child in successors:
            #if child has not been seen or cost is lower
            if child.state_hash() not in closed_dict or child.get_g() < closed_dict[child.state_hash()]:
                
                #update cost of state and add to open and closed
                child.set_cost(child.get_g())
                heapq.heappush(open_heap, child)
                closed_dict[child.state_hash()] = child.get_cost()


    return -1, expansions