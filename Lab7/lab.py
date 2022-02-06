#!/usr/bin/env python3
"""6.009 Lab 7: carlae Interpreter"""

import doctest
# NO ADDITIONAL IMPORTS!


class EvaluationError(Exception):
    """
    Exception to be raised if there is an error during evaluation other than a
    NameError.
    """
    pass


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    output = []
    source = source.splitlines()

    for line in source:
        
        line = line.split()
        line_list = []
        
        for word in line:
            line_list += split_word(word)
            
        for i in line_list:
            if i == ";":
                break
            else:
                output.append(i)
            
    return output
 
def split_word(word):
    """
    split the word before and after left paranthesis (, right
    paranthesis ), and ;. Returns a list containing all of the
    strings from the split, including (, ),and ;.

    Parameters
    ----------
    word : string

    Returns
    -------
    list of strings
    """       

    output = []
    word_copy = word
    
    for i in range(len(word)-1,-1,-1):
        
        if word[i] == '(' or word[i] == ')' or word[i] == ';':
            
            if i == len(word_copy)-1:
                output.append(word_copy[i])
                
            else:
                output.append(word_copy[i+1:])
                output.append(word_copy[i])
            
            word_copy = word_copy[:i]
    
    if len(word_copy) != 0:
        output.append(word_copy)
            
    output.reverse()
    return output

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """    
    def parse_expression(tokens, index):
        if is_real_number(tokens[index])[0]:
            return (is_real_number(tokens[index])[1], index+1)
        
        elif tokens[index] == "(":
            num_left_parentheses = 1
            num_right_parentheses = 0
            
            i = index
            while num_left_parentheses != num_right_parentheses:
                i = i + 1
                if i >= len(tokens):
                    raise SyntaxError
                if tokens[i] == "(":
                    num_left_parentheses += 1
                elif tokens[i] == ")":
                    num_right_parentheses += 1
            return (parse(tokens[index:i+1]), i+1)
        
        elif tokens[index] == ")":
            raise SyntaxError
        
        else:
            return (tokens[index], index + 1)
        
        
    if len(tokens) == 1:
        return parse_expression(tokens, 0)[0]
    
    else:
        if tokens[0] != "(":
            raise SyntaxError
        else:
            next_index = 1
            output = []
            while next_index < len(tokens)-1:
                parsed_expression, next_index = parse_expression(tokens, next_index)
                output.append(parsed_expression)
            
            return output

def is_real_number(string):
    """
    determine if the string represents a real number. In that case,
    return a tuple, with the first element being True and the second
    element being int or float, representing the number. Here, the
    number can be an integer or a float. If the string does not 
    represent a number, return a tuple with the first element being 
    False and the second element being the string itself.

    Parameters
    ----------
    string : STR

    Returns
    -------
    (True, number) if the string represents a number
    (False, string) if the string does not represent a number.

    """
    try:
        num = float(string)
        if num.is_integer():
            return (True, int(num))
        else:
            return (True, num)
    except:
        return (False, string)
        

def multiply(args):
    """
    given a list of numbers(int and float), multiply all of the elements: 
        args[0]/(args[1]*args[2]*...). If the list is empty, return one. 
        
    arguments: list of int and/or float
    """
    output = 1
    if len(args) == 0:
        return 1
    
    else:
        for i in args:
            output = output*i
        return output
    
def divide(args):
    """
    given a list of numbers (int and float), divide the first element with all of
    the remaining elements: args[0]/(args[1]*args[2]*...). If the 
    list is empty, raise an exception. If there is a zero at any index
    other than 0, raise a ZeroDivisionError
    
    arguments: list of int and/or float
    """
    if len(args) == 0:
        raise Exception('at least one argument must be given')
    
    else:
        output = args[0]
        for i in args[1:]:
            if i == 0:
                raise ZeroDivisionError('can not divide by zero')
            else:
                output = output/i
        return output


carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': multiply,
    '/': divide,
}


def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        env = Environment Object
    """
    if env == None:
        env = Environment()
        
    if isinstance(tree, int) or isinstance(tree, float):
        return tree
    
    elif isinstance(tree, str):
        if tree in env:
            return env[tree]
        elif tree in env.builtins:
            return env.builtins[tree]
        else:
            raise NameError("tree object is not defined")
    
    elif isinstance(tree, list):
        if isinstance(tree[0], str):
            if tree[0] in env: # checking if tree[0] is a user defined function
                    return env[tree[0]]([evaluate(i, env) for i in tree[1:]])
                
            elif tree[0] in env.builtins: # checking for built-in special methods
                if tree[0] == 'define':
                    if len(tree) != 3:
                        raise EvaluationError
                    elif isinstance(tree[1], list):
                        return env.builtins[tree[0]](tree[1][0], Function(tree[1][1:], tree[2], env))
                    else:
                        return env.builtins[tree[0]](tree[1], evaluate(tree[2], env))
                else:
                    return env.builtins[tree[0]]([evaluate(i, env) for i in tree[1:]])
            elif tree[0] == 'lambda': # checking for special method lambda
                return Function(tree[1], tree[2], env)
            else: # if tree[0] is string and not a special method, it must be name of user defined function
                raise NameError("object not defined")
                
        else: # if not special method, it represents a function call
            if isinstance(tree[0], list):
                func = evaluate(tree[0], env)
                return func([evaluate(i, env) for i in tree[1:]])
            elif isinstance(tree[0], int) or isinstance(tree[0], float):
                raise EvaluationError
            else:
                return tree[0](evaluate(i, env) for i in tree[1:])
                


def result_and_env(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language. This function does the same thing as evaluate, but also returns
    the environment in which the syntax tree was evaluated.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        env - Environment Object
    """
    if env == None:
        env = Environment("Global")
        
    result = evaluate(tree, env)
    return (result, env)


def repl():
    """
    take an expression from the user, tokenize and parse it, and finally evaluate it.
    print an error message if an exception is raised during the evaluation process.
    execute the program if user types QUIT
    """
    inp = input("Type the expression you want to evaluate in carlae: ")
    env = Environment("Global")
    
    while inp != "QUIT":
        tokens = tokenize(inp)
        parsed_expressions = parse(tokens)
        
        try:
            print(evaluate(parsed_expressions, env))
        
        except:
            print("Error: the expression could not be evaluated. An exception was raised")
        
        inp = input("Type the expression you want to evaluate in carlae: ")
        
       
class Builtins(object):
    """
    This class is parent class of all Environment objects. It stores some primitive
    functions, such as '+', '-', '*', '/', and 'define', and some variables.
    """
    def __init__(self):
        self.builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': multiply,
    '/': divide,
    "define": self.define,
}
    def define(self, var, exp):
        """
        This function takes an Environment object self, and updates its variables
        dictionary with a mapping from var to exp.
        """
        self.variables[var] = exp
        return exp


class Environment(Builtins):
    """
    This class will store mappings from variables to values and variables to
    functions in a dictionary to allow evaluation a code in one environment. 
    """
    def __init__(self, parentEnv=None):
        Builtins.__init__(self)
        self.variables = {}
        self.parent = parentEnv
        
    def __contains__(self, var):
        """
        if var in self object or its parent variables dictionary return True, else
        return False
        """
        if var in self.variables:
            return True
        elif self.parent != None:
            return self.parent.__contains__(var)
        else:
            return False
    
    def __getitem__(self, key):
        """
        If key in self or in parent, return the mapping associated to the key.
        Otherwise, return a NameError
        """
        if key in self:
            if key in self.variables:
                return self.variables[key]
            else:
                return self.parent.__getitem__(key)
        else:
            raise NameError
            
    
class Function(object):
    """
    This class will store function parameters, body of the function,
    and environment in which the function was defined. It has a __call__()
    method to call the function with parameters.
    """
    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.parentEnv = environment
        
    def __call__(self, params):
        """
        Pass in params to the self Function object, evaluate its body, and return
        the output. Raise an Evaluation error if incorrect number of arguments is 
        passed in to the function.
        """
        if len(params) != len(self.parameters):
            raise EvaluationError("expected ", len(self.parameters), " parameters, but got ", len(params))
        else:
            self.env = Environment(self.parentEnv)
            for i in range(len(params)):
                self.env.define(self.parameters[i], params[i])
            return evaluate(self.body, env = self.env)
        
         
if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    #repl()
    pass
    
    
