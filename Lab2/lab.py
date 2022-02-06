#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for lab 2 will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


def acted_together(data, actor_id_1, actor_id_2):
    """
    inputs:
        data: a list of tuples. Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 played together.
        actor_id_1: integer, representing an actor.
        actor_id_2: integer, representing another actor.
    output:
        True: if actor1 and actor2 acted together in a movie. (this information is taken from the "data".)
        False: if actor1 and actor2 did not act together in a movie.
    """
    data_set = set([(i[0],i[1]) for i in data])
    if (actor_id_1, actor_id_2) in data_set or (actor_id_2, actor_id_1) in data_set:
        return True
    else:
         return False

def actors_with_bacon_number(data, n):
    """
    Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 played together.
        
    n : integer

    Returns
    -------
    a set of integers, where each integer is an ID of some actor. This set contains all actors who are separated from
    Kevin Bacon with n movies. My algorithm uses breadth-first search.

    """
    actors_dict = {} #contains all actors as keys and their nearest neighbors as values (sets).
    for elem in data:
        if elem[0] != elem[1]:
            actors_dict.setdefault(elem[0], set()).add(elem[1])
            actors_dict.setdefault(elem[1], set()).add(elem[0])
    seen = {4724} # contains all of the names of actors at the deepest level in a breadth-first search.    
    
    if n == 0:
        return seen
    else:
        for i in range(n):
            set_new = set() # this set is used to collect names of actors in the next depth of breadth-first search.
            for actor1 in seen:
                for actor2 in actors_dict[actor1]:
                    if actor2 in actors_dict.keys() and actor2 not in seen:
                        set_new.add(actor2)
            for item in seen:
                del actors_dict[item]
            if len(set_new) == 0:
                return set()
            seen = set_new
        return set_new

def bacon_path(data, actor_id):
    """
    Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 played together.
        
    actor_id: integer that represents an actor. 

    Returns
    -------
    a list of integers (actor IDs) connecting Kevin Bacon to the actor_id. My algorithm uses breadth-first search.

    """
   
    return actor_to_actor_path(data, 4724, actor_id) 

def actor_to_actor_path(data, actor_id_1, actor_id_2):
    """
    Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 acted together.
        
    actor_id_1: integer: ID number of the first actor. 
    
    actor_id_2: integer: ID number of the second actor.

    Returns
    -------
    a list of integers (actor IDs) connecting actor_id_1 to the actor_id_2. My algorithm uses breadth-first search.

    """
    return actor_path(data, actor_id_1, lambda x: x == actor_id_2)

def movie_path_connecting_actors(data, actor_id_1, actor_id_2):
    """

   Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 acted together.
        
    actor_id_1: integer: ID number of the first actor. 
    
    actor_id_2: integer: ID number of the second actor.

    Returns
    -------
    a list of strings(movie names) connecting actor_id_1 to the actor_id_2.

    """
    actor_path = actor_to_actor_path(data, actor_id_1, actor_id_2)
    actor_pair_dict = {(item[0], item[1]): item[2] for item in data}
    movie_path = []
    for i in range(len(actor_path)-1):
        if (actor_path[i], actor_path[i+1]) in actor_pair_dict:
            movie = actor_pair_dict[(actor_path[i], actor_path[i+1])]
            movie_path.append(movie)
        elif (actor_path[i+1], actor_path[i]) in actor_pair_dict:
            movie = actor_pair_dict[(actor_path[i+1], actor_path[i])]
            movie_path.append(movie)
    return movie_path

def movie_name_from_id(movie_id):
    """

    Parameters
    ----------
    movie_id : integer

    Returns
    -------
    String, representing name of the movie.

    """
    
    with open('resources/movies.pickle', 'rb') as f:
        movies = pickle.load(f)
    
    names_list = list(movies.keys())
    IDs_list = list(movies.values())
    index = IDs_list.index(movie_id)
    return names_list[index]
    
def actor_path(data, actor_id_1, goal_test_function):
    """
    Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 acted together.
        
    actor_id_1: integer: ID number of the first actor. 
    
    goal_test_function: a function that takes in an actor ID, and returns True or False

    Returns
    -------
    a list of integers (actor IDs) connecting actor_id_1 to an actor that satisfies 
    goal_test_function (goal_test_function(actor) returns True). My algorithm uses breadth-first search.

    """
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    
    actors_dict = {} # Keys: actors, Values: their nearest neighbors.
    for elem in data:
        if elem[0] != elem[1]:
            actors_dict.setdefault(elem[0], set()).add(elem[1])
            actors_dict.setdefault(elem[1], set()).add(elem[0])
          
    parents_dict = {} #key: an actor, value: its parent
    parents_dict[actor_id_1] = actor_id_1
    seen = {actor_id_1} #contains all of the names of actors at the deepest level in a breadth-first search.
                        #currently, it only contains the ID of the first actor.
    goal_actor = actor_id_1 #it just initializes with the starting actor, but then changes to a different
                            #actor that satisfies the goal_test_function.
    while goal_test_function(goal_actor) == False:
        set_new = set() # this set is used to collect names of actors in the next depth of breadth-first search.
        for actor1 in seen:
            for actor2 in actors_dict[actor1]:
                if actor2 in actors_dict.keys() and actor2 not in seen:
                    set_new.add(actor2)
                    parents_dict[actor2] = actor1
                    if goal_test_function(actor2):
                        goal_actor = actor2
                        break
            if goal_test_function(goal_actor):
                break
        for item in seen:
            del actors_dict[item]
        if len(set_new) == 0:
            return None
        seen = set_new
    
    iteration = True # this is going to be used as a test in a while loop, to keep track of whether we found the actor_id_1 or not
    parent = goal_actor
    bacon_path_list = [] # constructs the list in reverse order, then reverses the list to get the correct order.
    bacon_path_list.append(parent)
    while iteration:
        parent = parents_dict[parent]
        bacon_path_list.append(parent)
        if parent == actor_id_1:
            iteration = False
    bacon_path_list.reverse()
    return bacon_path_list


def actors_connecting_films(data, film1, film2):
    """
     Parameters
    ----------
    data : list of tuples.
        Each tuple has three elements: ID of actor1, ID of actor2, and ID of the movie
        where actor1 and actor2 acted together.
        
    film1: integer: ID number of a movie. 
    
    film2: integer: ID number of another movie.

    Returns
    -------
    a list of integers (actor IDs) connecting film1 to film2 (shortest path). My algorithm uses breadth-first search.

    """
    movies_dict = {} # key: movie ID, value: set containing all actors who acted in that movie
    movies_neighbor_dict = {} # key: movie ID, value: set containing all other nearest neighbor movies.
    actors_dict = {} # key: actor ID, value: all movies where this actor played.
    
    for elem in data:
        movies_dict.setdefault(elem[2], set()).add(elem[0])
        movies_dict.setdefault(elem[2], set()).add(elem[1])
        actors_dict.setdefault(elem[0], set()).add(elem[2])
        actors_dict.setdefault(elem[1], set()).add(elem[2])
    
    for movie1 in movies_dict:
        for actor in movies_dict[movie1]:
            for movie2 in actors_dict[actor]:
                if movie1 != movie2:
                    movies_neighbor_dict.setdefault(movie1, set()).add(movie2)

    # building the parents dictionary
    parents_dict = {} # key: a movie, value: its parent movie
    parents_dict[film1] = film1
    seen = {film1}
    while film2 not in parents_dict:
        set_new = set()
        for movie1 in seen:
            for movie2 in movies_neighbor_dict[movie1]:
                if movie2 in movies_neighbor_dict.keys() and movie2 not in seen:
                    set_new.add(movie2)
                    parents_dict[movie2] = movie1
        if len(set_new) == 0:
            return None
        for item in seen:
            del movies_neighbor_dict[item]   
        seen = set_new
   
    # building the actors chain list    
    actors_list = []
    movie = film2
    parent = parents_dict[movie]
    while movie != film1:
        if len(movies_dict[movie] & movies_dict[parent]) == 0:
            return None
        for actor in movies_dict[movie] & movies_dict[parent]:
            actors_list.append(actor)
            break
        movie = parent
        parent = parents_dict[movie]
    actors_list.reverse()
    return actors_list
    

def actor_name_from_id(actor_id):
    """

    Parameters
    ----------
    actor_id : integer

    Returns
    -------
    String, name of the actor.

    """
    
    with open('resources/names.pickle', 'rb') as f:
        names = pickle.load(f)
    return list(names.keys())[list(names.values()).index(actor_id)]
    
if __name__ == '__main__':

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    ### loading the tiny.pickle database:
    # with open('resources/small.pickle', 'rb') as f:
    #     smalldb = pickle.load(f)
    # with open('resources/names.pickle', 'rb') as f:
    #     names = pickle.load(f)
    
    ### getting ID of James Staszkiel:
    #print('James Staszkiel: ', names['James Staszkiel'])
        
    ### getting the name corresponding to the ID 4788
    #list(names.keys())[list(names.values()).index(4788)]
    
    ### answer to actor path lab question 5.2:
    # actors_list = actor_to_actor_path(largePickle, names['Billie Brockwell'], names['Billy Bob Thornton'])
    # [actor_name_from_id(i) for i in actors_list]
    
    ### answer to question 6
    # movies_list = movie_path_connecting_actors(largePickle, names['Unknown Actor 15'], names['Anton Radacic'])
    # [movie_name_from_id(i) for i in movies_list]
    pass
