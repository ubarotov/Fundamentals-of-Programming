#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """

    Parameters
    ----------
    nodes_filename : string
        directory to the nodes dataset
    ways_filename : string
        directory to the ways dataset

    Returns
    -------
    nearest_neighbor_dict : dictionary
        key: node_id, value: set of nearest neighbors represented as tuples of two integers: (node_id, speed_limit)
    nodes_dict : dictionary
        key: node_id, value: (lat, lon)

    """
    nearest_neighbor_dict = {}
    for way in read_osm_data(ways_filename):
        if 'highway' in way['tags']:
            if way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                # finding max speed for the road:
                if 'maxspeed_mph' in way['tags']:
                    speed_limit = way['tags']['maxspeed_mph']
                else:
                    speed_limit = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                
                # updating nearest_neighbor_dict
                for i in range(len(way['nodes'])-1):
                    if 'oneway' in way['tags']:
                        if way['tags']['oneway'] == 'yes':
                            nearest_neighbor_dict.setdefault(way['nodes'][i], set()).add((way['nodes'][i+1], speed_limit))
                            nearest_neighbor_dict.setdefault(way['nodes'][i+1], set())
                        else:
                            nearest_neighbor_dict.setdefault(way['nodes'][i], set()).add((way['nodes'][i+1], speed_limit))
                            nearest_neighbor_dict.setdefault(way['nodes'][i+1], set()).add((way['nodes'][i], speed_limit))
                    else:
                        nearest_neighbor_dict.setdefault(way['nodes'][i], set()).add((way['nodes'][i+1], speed_limit))
                        nearest_neighbor_dict.setdefault(way['nodes'][i+1], set()).add((way['nodes'][i], speed_limit))
    
    nodes_dict = {}
    for node in read_osm_data(nodes_filename):
        if node['id'] in nearest_neighbor_dict:
            nodes_dict[node['id']] = (node['lat'], node['lon'])
    
    return (nearest_neighbor_dict, nodes_dict)


def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of distance.

    Parameters:
        aux_structures: (nearest_neighbor_dict, nodes_dict)
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    return find_path(aux_structures, loc1, loc2, 'short')

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    return find_path(aux_structures, loc1, loc2, 'fast')

def find_path(aux_structures, loc1, loc2, search_type):
    """
    Return the shortest or fastest path between the two locations. speed limits taken into account.

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location
        search_type: 'short' or 'fast'. It does find_short_path search if this 
              argument is 'short'', and find_fast_path if this argument is 'fast

    Returns:
        a list of (latitude, longitude) tuples representing the shortest (fastest) path
        from loc1 to loc2.
    """
    nearest_neighbor_dict = aux_structures[0]
    nodes_dict = aux_structures[1]
    nodes_dict_reverse = {nodes_dict[i]:i for i in nodes_dict}
    
    # find nearest node to loc1
    if loc1 in nodes_dict_reverse:
        n1 = loc1
    else:
        min_distance = float('inf')
        for node in nodes_dict:
            distance = great_circle_distance(loc1, nodes_dict[node])
            if distance < min_distance:
                n1 = nodes_dict[node]
                min_distance = distance
    # finding nearest node to loc2
    if loc2 in nodes_dict_reverse:
        n2 = loc2
    else:
        min_distance = float('inf')
        for node in nodes_dict:
            distance = great_circle_distance(loc2, nodes_dict[node])
            if distance < min_distance:
                n2 = nodes_dict[node]
                min_distance = distance         
    # finding a path from n1 to n2
    if n2 not in nodes_dict_reverse:
        return None
    agenda = {((n1,), 0)} # set of tuples with two elements: path (tuple), and cost
    expanded = set() # set of nodes that are visited by the search algorithm
    while agenda:
        if search_type == 'short':
            path = min(agenda, key = lambda x: x[1] + great_circle_distance(x[0][-1], n2))
        else:
            path = min(agenda, key = lambda x: x[1])
        terminal_vertex = path[0][-1]
        if terminal_vertex == n2:
            return list(path[0])
        elif terminal_vertex not in expanded:
            expanded.add(terminal_vertex)
            for child in nearest_neighbor_dict[nodes_dict_reverse[terminal_vertex]]: 
                (child, speed) = (child[0], child[1]) # index 0 has nearest neighbor, index 1 has speed information
                child = nodes_dict[child]
                if child not in expanded:
                    if search_type == 'short':
                        cost = path[1] + great_circle_distance(child, terminal_vertex)
                    else:
                        cost = path[1] + great_circle_distance(child, terminal_vertex)/speed
                    path_with_child = path[0] + (child,)
                    agenda.add((path_with_child, cost))
        agenda.remove(path)
    return None
## Helper functions for this lab
    
    
# Problem 3.1.3.3
def problem_3_1_3_3():
    
    # this function does not take any arguments. It solves problem 3.1.3.3 from the lab
    
    nodes_dict = {}
    for node in read_osm_data('resources/midwest.nodes'):
        nodes_dict[node['id']] = (node['lat'], node['lon'])
    
    for i in read_osm_data('resources/midwest.ways'):
        if i['id'] == 21705939:
            way = i['nodes']
    
    distance = 0
    for i in range(len(way)-1):
        loc1 = nodes_dict[way[i]]
        loc2 = nodes_dict[way[i+1]]
        distance += great_circle_distance(loc1, loc2)
    return distance

def problem_3_1_4():
    
    # this function does not take any arguments. It solves problem 3.1.4 from the lab
    
    nodes_dict = {}
    for node in read_osm_data('resources/midwest.nodes'):
        nodes_dict[node['id']] = (node['lat'], node['lon'])
    
    closest_nodes_to_consider = set() # Will get a set of all ways that are in an allowed way
    for way in read_osm_data('resources/midwest.ways'):
        if 'highway' in way['tags']:
            if way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                for node in way['nodes']:
                    closest_nodes_to_consider.add(node)
                
    loc = (41.4452463, -89.3161394)
    
    if loc in closest_nodes_to_consider:
        index = list(nodes_dict.values()).index(loc)
        loc_id = list(nodes_dict.keys())[index]
        return loc_id
    
    distance_list = []
    for loc1 in closest_nodes_to_consider:
        distance = great_circle_distance(loc, nodes_dict[loc1])
        distance_list.append((nodes_dict[loc1], distance))
    
    closest_to_loc = distance_list[0]
    for loc in distance_list:
        if loc[1] < closest_to_loc[1]:
            closest_to_loc = loc
    index = list(nodes_dict.values()).index(closest_to_loc[0])
    return list(nodes_dict.keys())[index]

# Number of items processed in agenda with heuristic: 47606
# Number of items processed in agenda without heuristic: 386072
if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
