#!/usr/bin/env python3
"""6.009 Lab 7: carlae Interpreter. Part II """

import doctest
import sys
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
        

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
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
        else:
            # print("tree:", tree)
            raise NameError("tree object is not defined")
    elif isinstance(tree, Pair):
        print('tree:', tree)
        return tree
    elif tree == None:
        return tree
    
    elif isinstance(tree, list):
        if len(tree) == 0:
            raise EvaluationError
        
        # checking for special methods
        elif tree[0] == 'define': 
            if len(tree) != 3:
                raise EvaluationError
            elif isinstance(tree[1], list):
                return env.define(tree[1][0], Function(tree[1][1:], tree[2], env))
            else:
                return env.define(tree[1], evaluate(tree[2], env))
        elif tree[0] == 'lambda': 
            return Function(tree[1], tree[2], env)
        elif tree[0] == 'and':
            return env._and(tree[1:])
        elif tree[0] == 'or':
            return env._or(tree[1:])
        elif tree[0] == 'if': # (if COND TRUEEXP FALSEEXP)
            if evaluate(tree[1], env) == True:
                return evaluate(tree[2], env)
            else:
                return evaluate(tree[3], env)
        elif tree[0] == 'cons':
            if len(tree[1:]) != 2:
                raise EvaluationError
            car = evaluate(tree[1], env)
            cdr = evaluate(tree[2], env)
            return Pair(car, cdr)
        elif tree[0] == 'let': # (let ((Var1 Val1) (Var2 Val2)...) BODY)
            return env.let([[[i[0], evaluate([i[1]], env)] for i in tree[1]], tree[2]], env)
        elif tree[0] == 'set!': # (set! var exp)
            return env.set_(tree[1], evaluate(tree[2], env))
        
        # checking for function calls for user defined functions
        elif isinstance(tree[0], str): # if you omit this step, it can give a TypeError: unhashable type: 'list'
            if tree[0] in env:
                return env[tree[0]]([evaluate(i, env) for i in tree[1:]])
            else:
                raise NameError("function is not defined")
        
        # checking for function calls for in-line define functions
        else: 
            if isinstance(tree[0], list):
                func = evaluate(tree[0], env)
                if len(tree) == 1:
                    return func
                else:
                    return func([evaluate(i, env) for i in tree[1:]])
            elif isinstance(tree[0], int) or isinstance(tree[0], float):
                raise EvaluationError
    else:
        raise EvaluationError
        

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
        env = Environment()
        
    result = evaluate(tree, env)
    return (result, env)


def evaluate_file(file_address, env = None):
    """
    file_address: directory for a file containing a carlae expression
    env: Environment object
    
    open the file, read the contents, and save them in a variable called
    expression. tokenize and parse the expression. Finally, evaluate the 
    expression in env (if passed in) and return the result.
    """
    
    with open(file_address, 'r') as f:
        expression = f.read()
        f.close()
    print("expression:", expression)
    tree = parse(tokenize(expression))
    print(tree)
    return evaluate(tree, env)


def repl(env = None):
    """
    take an expression from the user, tokenize and parse it, and finally evaluate it.
    print an error message if an exception is raised during the evaluation process.
    execute the program if user types QUIT
    """
    inp = input("Type the expression you want to evaluate in carlae: ")
    if env == None:
        env = Environment()
    
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
    '*': self.multiply,
    '/': self.divide,
    "define": self.define,
    '#t': True,
    '#f': False,
    '=?': self.is_equal,
    '>': self.is_decreasing,
    '>=': self.is_nonincreasing,
    '<': self.is_increasing,
    '<=': self.is_nondecreasing,
    'not': self._not,
    'and': self._and,
    'or': self._or,
    'nil': None,
    'car': self.car,
    'cdr': self.cdr,
    'list': self._list,
    'length': self.length,
    'elt-at-index': self.elt_at_index,
    'concat': self.concat,
    'map': self.map_,
    'filter': self.filter_,
    'reduce': self.reduce,
    'begin': self.begin,
    'let': self.let,
    'set!': self.set_,
    
}
    def define(self, var, exp):
        """
        This function takes an Environment object self, and updates its variables
        dictionary with a mapping from var to exp.
        """
        self.variables[var] = exp
        return exp
    
    def multiply(self, args):
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
    
    def divide(self, args):
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
        
    def is_equal(self, args):
        """
        args: list of numbers
        return True if all numbers are equal, else False.
        """
        for i in range(len(args)-1):
            if args[i] != args[i+1]:
                return False
        return True
    
    def is_decreasing(self, args):
        """
        args: list of numbers
        return True if arguments are in decreasing order, else False.
        """
        for i in range(len(args)-1):
            if args[i] <= args[i+1]:
                return False
        return True
    
    def is_nonincreasing(self, args):
        """
        args: list of numbers
        return True if arguments are in nonincreasing order, else False.
        """
        for i in range(len(args)-1):
            if args[i] < args[i+1]:
                return False
        return True
    
    def is_increasing(self, args):
        """
        args: list of numbers
        return True if arguments are in increasing order, else False.
        """
        for i in range(len(args)-1):
            if args[i] >= args[i+1]:
                return False
        return True
    
    def is_nondecreasing(self, args):
        """
        args: list of numbers
        return True if arguments are in nondecreasing order, else False.
        """
        for i in range(len(args)-1):
            if args[i] > args[i+1]:
                return False
        return True
    
    def _not(self, arg):
        """
        if the argument is True, return False. Else, return True
        """
        if arg[0] == True:
            return False
        elif arg[0] == False:
            return True
        else:
            raise EvaluationError
            
    def _and(self, args):
        """
        return True if all arguments are True, else return False. Evaluate arguments
        in in order, if any of the argument returns False, return False without
        evaluating remainder of the arguments list (short circuiting).
        
        self: an Environment object
        args: List of arguments form the tokenize(parse(expression))
        
        return: True if ALL of the arguments evaluates to True. Else return False.
        """
        for i in args:
            if evaluate(i, self) != True:
                return False
        return True
    
    def _or(self, args):
        """
        return True if at least one of the arguments is True, else return False.
        Evaluate arguments in order, if evaluation of any of the argument returns 
        True, return True without evaluating remainder of the arguments list 
        (short circuiting).
        
        self: an Environment object
        args: List of arguments form the tokenize(parse(expression))
        
        return: True if ANY of the arguments evaluates to True. Else return False.
        """
        for i in args:
            if evaluate(i, self) == True:
                return True
        return False
    
    def car(self, arg):
        """
        Takes a Pair object as input, and returns the can attribute of the Pair object.
        If arg is not an istance of the Pair class, raises Evaluation error.
        """
        arg = arg[0] # arg is given as a list of Pair
        if not isinstance(arg, Pair):
            raise EvaluationError
        else:
            return arg.car
   
    def cdr(self, arg):
        """
        Takes a Pair object as input, and returns the cdr attribute of the Pair object.
        If arg is not an istance of the Pair class, raises Evaluation error.
        """
        arg = arg[0] # arg is given as a list of Pair
        if not isinstance(arg, Pair):
            raise EvaluationError
        else:
            return arg.cdr
    
    def _list(self, args):
        """
        create a list of args. (list) evaluates to the same thing as nil
        (list 1) evaluates to (cons 1 nil)
        (list 1 2) evaluates to (cons 1 (cons 2 nil)), etc...
        """
        if len(args) == 0:
            return None
        else:
            return Pair(args[0], self._list(args[1:]))
        
    def length(self, arg, beginning = True):
        """
        Takes a Pair object (representing list) as input, and returns the length of the list.
        If arg is not an istance of the Pair class, raises Evaluation error.
        """
        if beginning:
            arg = arg[0] # arg is given as a list of a Pair object
        if arg == None:
            return 0
        if not isinstance(arg, Pair):
            raise EvaluationError
        else:
            return 1 + self.length(arg.cdr, beginning=False)
        
    def find(self, cons, index):
        """
        given a cons (Pair object), and an index, return the pair object at the index.
        if index is negative or the argument is not a Pair object, raise evaluation error.
        """
        if index < 0:
            raise EvaluationError
        if not isinstance(cons, Pair):
            raise EvaluationError
        if not isinstance(cons.cdr, Pair):
            if index == 0:
                return cons
            else:
                raise EvaluationError
        if index == 0:
            return cons
        else:
            return self.find(cons.cdr, index-1)
        
    def elt_at_index(self, args): # (elt-at-index LIST index)
        """
        given a list as [LIST, index], return the car value of the Pair object at the index.
        if index is negative or any argument is not a Pair object, raise evaluation error.
        """
        cons = args[0]
        index = args[1]
        return self.find(cons, index).car
    
    def copy(self, arg):
        """
        given a list, return a copy of it without mutating the original list.
        """
        l = self.length(arg, beginning = False)
        arg_copy = Pair(arg.car, None)
        for i in range(l-1):
            self.find(arg_copy, i).cdr = Pair(self.elt_at_index([arg, i+1]), None)
        return arg_copy
        
    def concat(self, args):
        """
        (concat LIST1 LIST2 LIST3 ...) should take an arbitrary number of 
        lists as arguments and should return a new list representing the 
        concatenation of these lists. If exactly one list is passed in, 
        it should return a copy of that list. If concat is called with 
        no arguments, it should produce an empty list. Calling concat on 
        any elements that are not lists should result in an EvaluationError.
        """
        if len(args) == 0:
            return None

        else:
            if args[0] == None:
                return self.concat(args[1:])
            elif isinstance(args[0], Pair):
                first = self.copy(args[0])
                l = self.length(first, beginning=False)
                ending = self.find(first, l-1)
                ending.cdr = self.concat(args[1:])
                return first
            else:
                raise EvaluationError
                
    def map_(self, args):
       """ 
       carlae syntax: (map FUNCTION LIST)
       
       given a function and a list, apply the function to each element of list,
       and return the new list.
       """
       function = args[0]
       input_list = args[1]
       l = self.length(input_list, beginning = False)
       if l == 0:
           return None
       output = Pair(function([input_list.car]), None)
       for i in range(l-1):
           self.find(output, i).cdr = Pair(function([self.elt_at_index([input_list, i+1])]), None)
       return output
   
    def filter_(self, args):
      """  
        carlae syntax: (filter FUNCTION LIST)
        
        apply the function to each element in the LIST. For each element in the list,
        if this application of the function results in True, include the element in the output list.
        Otherwise, move to the next element and continue the process.
      """
      function = args[0]
      input_list = args[1]
      l = self.length(input_list, beginning=False)
      if l == 0:
          return None
      else:
          output = None
          index = 0
          for i in range(l):
              if function([self.elt_at_index([input_list, i])]):
                  if output == None:
                      output = Pair(self.elt_at_index([input_list, i]), None)
                  else:
                      self.find(output, index).cdr = Pair(self.elt_at_index([input_list, i]), None)
                      index += 1
      return output
  
    def reduce(self, args):
        """
        carlae syntax: (reduce FUNCTION LIST INITVALUE)
        
        function takes INITVALUE and the first element of the list to compute 
        an intermediate result, which, then is used along with the second element of
        the list as arguments to the FUNCTION. The FUNCTION then produces the next 
        intermediate result, which is used in a similar way to produce all 
        intermediate results. When all finished iterating through the list, the 
        final result is returned. 
        
        Consider (reduce * (list 9 8 7) 1). The function in this case is *, which
        computes the first intermediate result by taking the INITVALUE = 1 and 9, 
        resulting in 1*9 = 9. Then, THIS result, along with the next element in the
        list, are given as inputs to the * function. So, the nexg computation would be 9*8 = 72.
        We continue this computation until we have gone through each element in 
        the list. Intermediate results we obtain are, in succession, 1*9=9, 9*8=72,
        and 72*7=504. The final result 504 is returned as the output.
        """
        function = args[0] # FUNCTION
        input_list = args[1] # LIST
        sofar = args[2] # initializes with the INITVALUE
        l = self.length(input_list, beginning=False)
        if l == 0:
            return sofar
        for i in range(l):
            sofar = function([sofar, self.elt_at_index([input_list, i])])
        return sofar
    
    def begin(self, args):
        """
        given a list, return the last element of the list. Even thought this function
        returns only the last element, it is very useful structure because it allows 
        us to run arbitrarily many number of expressions sequentially. For example,
        
        (begin (define x 7) (define y 8) (- x y))
        
        evaluates to -1.
        
        return: return the last element of the arguments list.
        """
        if len(args) == 0:
            return EvaluationError
        else:
            return args[-1]
        
    def let(self, args, env): # (let ((Var1 Val1) (Var2 Val2)...) BODY)
        """
        args: [[[Var1, Val1], [Var2, Val2], ...], BODY]
        env: Environment Object.
        
        Create an Environment object whose parent is ENV. In this new 
        environment, bind Var1, Var2, ... to Val1, Val2, ...., respectively.
        Then, evaluate the BODY in this new environment, and return the result.
        """
        env_new = Environment(env)
        bindings = args[0]
        body = args[1]
        for binding in bindings:
            env_new.define(binding[0], binding[1]) # Environment().define(Var, Val)
        return evaluate(body, env_new)
    
    def set_(self, var, val):
        """
        if var is present in self.variables, change the value of that variable
        to val. Else, if parent is None, return NameError. If parent is not None,
        call the set_ method with the parent. This function will only be used by
        the children of Builtins class, that is, only by an Environment objects.
        This function was implemented here just to be consistent in implementing
        all builtins functions in the same place.
        """
        if var in self.variables:
            self.variables[var] = val
            return self.variables[var]
        else:
            if self.parent == None:
                raise NameError("object could not be found")
            else:
                return self.parent.set_(var, val)
    
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
        elif var in self.builtins:
            return True
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
            elif self.parent != None:
                return self.parent.__getitem__(key)
            elif key in self.builtins:
                return self.builtins[key]
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
        
 
class Pair(object):
    """
    This class is used to represent a cons cell. Each cons cell has two values,
    referred to as car and cdr.
    """
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
        
if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    # env = Environment()
    # for file_address in sys.argv[1:]:
    #     evaluate_file(file_address, env)
    # repl(env)
    pass
    
    
