#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    
    if len(formula) == 0:
        return {}
    
    else:
        
        var_dict = select_variable(formula)
        if var_dict:
            
            simplified_formula = formula
            for variable, value in var_dict.items():
                simplified_formula = set_variable(simplified_formula, variable, value)
                if simplified_formula == False:
                    return None
            
            sol0 = satisfying_assignment(simplified_formula)
            
            if sol0 == None:
                return None
            
            else:
                sol0.update(var_dict)
                return sol0
                
        else:
            var = formula[0][0][0]
            exp1 = set_variable(formula, var, True)
            exp2 = set_variable(formula, var, False)
        
            if exp1 == False and exp2 == False:
                return None
        
            if exp1 != False:
                sol1 = satisfying_assignment(exp1)
                if sol1 != None:
                    sol1.update({var: True})
                    return sol1
            if exp2 != False:
                sol2 = satisfying_assignment(exp2)
                if sol2 != None:
                    sol2.update({var: False})
                    return sol2
        return None


def select_variable(formula):
    """

    Parameters
    ----------
    formula : LIST
        the CNF representation of a logical expression. list of lists containing at
        least one tuple, representing a literal in the CNF expression. Each tuple 
        contains two elements: the first element represents the variable, the 
        second element is a Boolean.

    Returns
    -------
    a dictionary. keys are variables that appear in a clause of length 1
    in the FORMULA. values are boolean that makes that clause True. If no
    clause of length 1 exists, returns empty dictionary.
    
    """
    var_dict = {}
    
    for i in range(len(formula)):
        if len(formula[i]) == 1:
            var_dict[formula[i][0][0]] = formula[i][0][1]
    return var_dict
        
def set_variable(formula, var, value):
    """

    Parameters
    ----------
    formula : LIST of lists.
        the CNF representation of a logical expression. lists of lists containing at
        least one tuple, representing a literal in the CNF expression. Each tuple
        contains two elements: the first element represents the variable VAR, and
        the second element is a Boolean.
    var : STRING
        variable that is present in the literals in the formula.
    value : BOOLEAN
        True or False

    Returns
    -------
    evaluates the expression FORMULA by setting VAR = VALUE. If this assignment
    results in falsifying the FORMULA, the function returns False. Otherwise, it 
    simplifies the FORMULA, and returns the resulting expression in CNF representation.
    If the function returns an empty list, it indicates that the expression evaluated to TRUE.

    
    >>> set_variable([[('a', True), ('b', True), ('c', True)],
    ...                 [('a', False), ('f', True)],
    ...                 [('d', False), ('e', True), ('a', True), ('g', True)],
    ...                 [('h', False), ('c', True), ('a', False), ('f', True)]], 'a', True)
    [[('f', True)], [('h', False), ('c', True), ('f', True)]]
    """
    output = []
    for i in range(len(formula)):
        
        if len(formula[i]) == 1:
            if var == formula[i][0][0] and formula[i][0][1] != value:
                return False
            elif var != formula[i][0][0]:
                output.append([formula[i][0]])
        
        else:
            clause = []
            for j in range(len(formula[i])):
                if var == formula[i][j][0] and formula[i][j][1] == value:
                    clause = []
                    break
                elif formula[i][j][0] != var:
                    clause.append(formula[i][j])
            if len(clause) != 0:
                output.append(clause)
    
    return output

def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    rules_preference = boolify_student_preference(student_preferences)
    rules_one_session = boolify_for_one_session(student_preferences)
    rules_session_capacity = boolify_session_capacity(student_preferences, session_capacities)
    
    rules = rules_preference + rules_one_session + rules_session_capacity
    
    return rules

# Helper functions for boolify_scheduling_problem
def boolify_student_preference(student_preferences):
    """

    Parameters
    ----------
    student_preferences : dictionary
        a dictionary mapping a student name (string) to a set of session 
        names (strings) that work for that student

    Returns
    -------
    list of lists, each inner list representing a clause. Returns a
    CNF representation of constraints for the student availability. 
    >>> boolify_student_preference({'Alice': {'basement', 'penthouse'},
    ...                        'Bob': {'kitchen'},
    ...                        'Charles': {'basement', 'kitchen'},
    ...                        'Dana': {'kitchen', 'penthouse', 'basement'}})
    [[('Alice_basement', True), ('Alice_penthouse', True)], 
         [('Bob_kitchen', True)], [('Charles_basement', True), ('Charles_kitchen', True)], 
         [('Dana_basement', True), ('Dana_kitchen', True), ('Dana_penthouse', True)]]
    """
    output = []
    
    for student, sessions in student_preferences.items():
        clause = []
        for session in sessions:
            literal = (student + '_' + session, True)
            clause.append(literal)
        output.append(clause)
        
    return output

def boolify_for_one_session(student_preferences):
    """

    Parameters
    ----------
    student_preferences : dictionary
        a dictionary mapping a student name (string) to a set of session 
        names (strings) that work for that student
    
    session_capacities : dictionary
        a dictionary mapping each session name to a positive integer 
        for how many students can fit in that session

    Returns
    -------
    list of lists, each inner list representing a clause. Returns a
    CNF representation of constraints limiting assignment of a student at most
    to one session
    
    >>> boolify_for_one_session({'Alice': {'basement', 'penthouse'},
    ...                        'Bob': {'kitchen'},
    ...                        'Charles': {'basement', 'kitchen'},
    ...                        'Dana': {'kitchen', 'penthouse', 'basement'}})
    [[('Alice_basement', False), ('Alice_penthouse', False)], 
         [('Charles_basement', False), ('Charles_kitchen', False)], 
         [('Dana_basement', False), ('Dana_kitchen', False)], 
         [('Dana_basement', False), ('Dana_penthouse', False)], 
         [('Dana_kitchen', False), ('Dana_penthouse', False)]]

    """
    output = []
    
    for student, sessions in student_preferences.items():
        sessions = list(sessions)
        for i in range(len(sessions)-1):
            for j in range(i+1, len(sessions)):
                clause = [(str(student) + '_' + sessions[i], False), (str(student) + '_' + sessions[j], False)]
                output.append(clause)
    return output

def boolify_session_capacity(student_preferences, session_capacities):
    """

    Parameters
    ----------
    student_preferences : dictionary
        a dictionary mapping a student name (string) to a set of session 
        names (strings) that work for that student
    
    session_capacities : dictionary
        a dictionary mapping each session name to a positive integer 
        for how many students can fit in that session

    Returns
    -------
    list of lists, each inner list representing a clause. Returns a
    CNF representation of constraints for the session capacity.
    >>> boolify_session_capacity({'Alice': {'basement', 'penthouse'},
    ...                        'Bob': {'kitchen'},
    ...                        'Charles': {'basement', 'kitchen'},
    ...                        'Dana': {'kitchen', 'penthouse', 'basement'}}, 
    ...                        {'basement': 1, 'kitchen': 2, 'penthouse': 4})
    [[('Alice_basement', False), ('Dana_basement', False)], 
         [('Alice_basement', False), ('Charles_basement', False)], 
         [('Dana_basement', False), ('Charles_basement', False)], 
         [('Bob_kitchen', False), ('Dana_kitchen', False), ('Charles_kitchen', False)]]

    """
    output = []
    
    for session, capacity in session_capacities.items():
        students = session_requests(student_preferences, session)
        if capacity < len(students):
            for subset in student_subset_n(students, capacity + 1):
                clause = []
                for student in subset:
                    clause.append((student + '_' + session, False))
                output.append(clause)
    return output
    
def session_requests(student_preferences, session):
    """
    

    Parameters
    ----------
    student_preferences : dictionary
        a dictionary mapping a student name (string) to a set of session 
        names (strings) that work for that student
    session : string
        session must be present inside set(s) in the student_preferences.values()

    Returns
    -------
    set of students who indicated preference for the SESSION.

    """
    output = set()
    for student, pref in student_preferences.items():
        if session in pref:
            output.add(student)
    return output

def student_subset_n(students, N):
    """

    Parameters
    ----------
    students : set
        set containing names of students.
    
    N : integer
        integer representing size of the desired subset of students. N must not
        be greater than number of students in the input set.

    Returns
    -------
    list of sets, each with N elements.
    
    >>> student_subset_n({'Alice', 'Bob', 'Charles', 'Dana'}, 3)
    [{'Alice', 'Bob', 'Dana'}, {'Alice', 'Bob', 'Charles'}, {'Alice', 'Dana', 'Charles'}, {'Bob', 'Dana', 'Charles'}]

    """
    output = []
    
    if N == 0:
            return [set()]
    else:
        for subset in student_subset_n(students, N-1):
            for student in students:
                if student not in subset:
                    subset2 = {s for s in subset}
                    subset2.add(student)
                    if subset2 not in output:
                        output.append(subset2)
    return output

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
