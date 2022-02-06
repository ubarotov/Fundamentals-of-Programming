#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)

def nearest_neighbors(dim, r, c):
    """
    Generates the list of nearest neighbors to the location (r, c).

    Parameters
    ----------
    dim : tuple
        (num_rows, num_cols) of the board
    r : integer
        first coordinate of the location, representing row number. r must be smaller than dim[0]
    c : integer
        second coordinate of the location, representing column number. c must be smaller than dim[1]

    Returns
    -------
    the list of tuples representing neighbors of the location (r, c)
    """
    neighbors_list = []
    for x in [r-1, r, r+1]:
        for y in [c-1, c, c+1]:
            if 0<=x<dim[0] and 0<=y<dim[1]:
                neighbors_list.append((x, y))
    neighbors_list.remove((r, c))
    return neighbors_list
    
def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    return dig_nd(game, (row, col))

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
   
    return render_nd(game, xray)


def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    nrow = game['dimensions'][0]
    ncol = game['dimensions'][1]
    render_list = render_2d(game, xray)
    render_str = ''
    for i in range(nrow):
        for j in range(ncol):
            render_str += render_list[i][j]
        render_str += '\n'
    return render_str[:-1]


# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    mask = create_nd_array(dimensions, False)
    board = create_nd_array(dimensions, 0)
    
    for bomb in bombs:
        set_value_in_nd_array(board, bomb, '.')
        for neighbor in nearest_neighbor_nd(dimensions, bomb):
            if get_value_in_nd_array(board, neighbor) != '.':
                value = get_value_in_nd_array(board, neighbor) + 1
                set_value_in_nd_array(board, neighbor, value)
    return {
        'dimensions': dimensions,
        'board': board,
        'mask': mask,
        'state': 'ongoing'
        }

def create_nd_array(dim, val):
    """
    given DIM and VAL of an array, returns a list of lists array with all values set to VAL

    Parameters
    ----------
    dimensions : tuple
        dimensions of an array to be created
    val: integer, float, boolean, list ...

    Returns
    -------
    list of lists, representing an array with dimensions DIM, and all values set to VAL
    
    >>> create_nd_array((4,3,2), 0)
    [[[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]]]

    """
    if len(dim) == 1:
        val_list = []
        for i in range(dim[0]):
            val_list.append(val)
        return val_list
    
    else:
        val_list = []
        for i in range(dim[0]):
            val_list.append(create_nd_array(dim[1:], val))
        return val_list

def set_value_in_nd_array(array, loc, val):
    """
    mutates the array to change the value at location LOC to VAL. Does not return anything

    Parameters
    ----------
    array : list
        nested list that represents an array
    loc : tuple
        represents a location in the array
    val : integer, float, string, boolean, etc ...
        DESCRIPTION.

    Returns
    -------
    Does not return anything, only mutates the array
    """
    if len(loc) == 1:
        array[loc[0]] = val
    else:
        return set_value_in_nd_array(array[loc[0]], loc[1:], val)
    
def nearest_neighbor_nd(dim, loc):
    """
    Given a dimension of an array DIM, and location LOC, returns list of all nearest neighbors to the location LOC

    Parameters
    ----------
    dim : tuple
        represents dimensions of an array
    loc : tuple
        represents a valid location inside the array

    Returns
    -------
    list of tuples, representing nearest neighbors of LOC
    
    >>> nearest_neighbor_nd((3,3), (0,0))
    [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    """
    if len(dim) == 1:
        neighbor_list = [loc[-1]-1, loc[-1], loc[-1]+1]
        neighbor_list = [(i,) for i in neighbor_list if 0<=i<dim[-1]]
        return neighbor_list
    
    else:
        neighbor_list = []
        for i in [loc[0]-1, loc[0], loc[0]+1]:
            if 0<=i<dim[0]:
                for j in nearest_neighbor_nd(dim[1:], loc[1:]):
                    neighbor_list.append((i,)+j)
        return neighbor_list
    
def get_value_in_nd_array(array, loc):
    """
    given an array ARRAY and location LOC, returns the element at that location inside the array.

    Parameters
    ----------
    array : nested lists, representing an array
        represents an array.
    loc : tuple
        represents a real location inside the array

    Returns
    -------
    the element at location LOC inside the array ARRAY.
    
    >>> get_value_in_nd_array([[[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], ['cinnamon', False]]], (3, 2, 0))
    'cinnamon'
    
    >>> get_value_in_nd_array([[[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], [0, 0]],
    ...                       [[0, 0], [0, 0], ['cinnamon', False]]], (3,2,1))
    False

    """
    if len(loc) == 1:
        return array[loc[0]]
    
    else:
        return get_value_in_nd_array(array[loc[0]], loc[1:])
    
def dig_nd(game, coordinates, is_root = True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coords (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    if get_value_in_nd_array(game['mask'], coordinates) == True:
        return 0
    
    elif get_value_in_nd_array(game['board'], coordinates) == '.':
        set_value_in_nd_array(game['mask'], coordinates, True)
        game['state'] = 'defeat'
        return 1
    
    else:
        if get_value_in_nd_array(game['board'], coordinates) == 0:
            set_value_in_nd_array(game['mask'], coordinates, True)
            revealed = 1
        
            for neighbor in nearest_neighbor_nd(game['dimensions'], coordinates):
                if get_value_in_nd_array(game['mask'], neighbor) == False:
                    revealed += dig_nd(game, neighbor, is_root = False)
        
        else:
            set_value_in_nd_array(game['mask'], coordinates, True)
            revealed = 1
            
        # checks if there is any tile to be uncovered
        if is_root:
            covered_squares = 0
            for loc in all_coordinates_in_array(game['dimensions']):
                if get_value_in_nd_array(game['mask'], loc) == False and get_value_in_nd_array(game['board'], loc) != '.':
                    covered_squares += 1
                    break
            if covered_squares == 0:
                game['state'] = 'victory'
        
        return revealed
        
def all_coordinates_in_array(dim):
    """
    given dimension of an array, returns a list containing all of the coordinates in the array.

    Parameters
    ----------
    dim : tuple
        tuple representing dimensions of an array

    Returns
    -------
    list conatining all of the coordinates in the array
    
    >>> all_coordinates_in_array((9,))
    [(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,)]
    
    >>> all_coordinates_in_array((2,2))
    [(0, 0), (0, 1), (1, 0), (1, 1)]

    """
    if len(dim) == 1:
        return [(i,) for i in range(dim[0])]
    
    else:
        coordinates_list = []
        for i in range(dim[0]):
            for j in all_coordinates_in_array(dim[1:]):
                coordinates_list.append((i,) + j)
        return coordinates_list

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    render_list = create_nd_array(game['dimensions'], '_')
    
    for loc in all_coordinates_in_array(game['dimensions']):
        
        if not xray:
            if get_value_in_nd_array(game['mask'], loc) == True:
                if get_value_in_nd_array(game['board'], loc) == 0:
                    set_value_in_nd_array(render_list, loc, ' ')
                else:
                    set_value_in_nd_array(render_list, loc, str(get_value_in_nd_array(game['board'], loc)))
            
        else:
            if get_value_in_nd_array(game['board'], loc) == 0:
                    set_value_in_nd_array(render_list, loc, ' ')
            else:
                    set_value_in_nd_array(render_list, loc, str(get_value_in_nd_array(game['board'], loc)))
            
    return render_list


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
