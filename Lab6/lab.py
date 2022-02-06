# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self):
        self.value = None
        self.children = {}
        self.type = None

    
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if self.type == None:
            self.type = type(key)
        
        else:
            if self.type != type(key):
                raise TypeError
        
        if len(key) == 0:
            self.value = value
            
        else:
            if key[0:1] not in self.children:
                self.children[key[0:1]] = Trie()
                self.children[key[0:1]].type = self.type
            self.children[key[0:1]].__setitem__(key[1:], value)


    def _find(self, key):
        """
        look through children of self until you find the node representing key, and 
        return it. If the given key is not in the trie, raise a KeyError.
        If the given key is of the wrong type, raise a TypeError.

        """
        if self.type != type(key):
            raise TypeError
        
        if len(key) == 0:
            return self
        
        else:
            if key[0:1] not in self.children:
                raise KeyError
            return self.children[key[0:1]]._find(key[1:])
    
    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        return self._find(key).value
            

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        node = self._find(key)
        
        if node.value == None:
            raise KeyError
        
        else:
            node.value = None

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        try:
            if self._find(key).value == None:
                return False
            else:
                return True
        
        except:
                return False

    def __iter__(self, sofar = None):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        if sofar == None:
            sofar = self.type()
            
        if self.value != None:
            yield (sofar, self.value)
        
        if self.children != {}:
            for k, v in self.children.items():
                yield from v.__iter__(sofar=sofar+k)
                
            


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    output = Trie()
    sentences = tokenize_sentences(text)
    
    for sentence in sentences:
        words = sentence.split()
        for word in words:
            if word in output:
                output[word] += 1
            else:
                output[word] = 1
    
    return output


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    output = Trie()
    sentences = tokenize_sentences(text)
    
    for sentence in sentences:
        
        sentence = tuple(sentence.split())
        
        if sentence in output:
            output[sentence] += 1
        else:
            output[sentence] = 1
            
    return output

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    try:
        node = trie._find(prefix)
        elements = sorted([e for e in node], key = lambda x: x[1], reverse = True)
        
        if max_count == None:
            return [prefix + i[0] for i in elements]
        elif max_count <= len(elements):
            return [prefix + i[0] for i in elements][0:max_count]
        else:
            return [prefix + i[0] for i in elements]
    
    except KeyError:
        return []    
    


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    ac = autocomplete(trie, prefix, max_count) # autocomplete
    e = edits(trie, prefix) # edits
    
    if max_count == None:
        return ac + e
    else:
        return ac + e[0:max_count-len(ac)]

def edits(trie, prefix):
    """
    given a prefix, make ONE of the following edits:
      a) A single-character insertion (add any one character in 
         the range "a" to "z" at any place in the word)
      b) A single-character deletion (remove any one character from the word)
      c) A single-character replacement (replace any one character 
         in the word with a character in the range a-z)
      d) A two-character transpose (switch the positions of any two 
         adjacent characters in the word) 
    
    A valid edit is an edit that results in a word that is in TRIE
    return a list of all possible edits of length LENGTH
    """
    letters = "abcdefghijklmnopqrstuvwxyz"
    output = []
    
    # insertion
    for letter in letters:
        for i in range(len(prefix)):
            edit = prefix[0:i] + letter + prefix[i:]
            if edit in trie and edit != prefix:
                edit = (edit, trie[edit])
                if edit not in output:
                    output.append(edit)

    # deletion
    for i in range(len(prefix)):
        edit = prefix[0:i] + prefix[i+1:]
        if edit in trie and edit != prefix:
            edit = (edit, trie[edit])
            if edit not in output:
                output.append(edit)
    
    # replacement
    for letter in letters:
        for i in range(len(prefix)):
            edit = prefix[0:i] + letter + prefix[i+1:]
            if edit in trie and edit != prefix:
                edit = (edit, trie[edit])
                if edit not in output:
                    output.append(edit)
    
    # transpose
    for i in range(len(prefix)):
        for j in range(i+1, len(prefix)):
            edit = prefix[0:i] + prefix[j] + prefix[i+1:j] + prefix[i] + prefix[j+1:] 
            if edit in trie and edit != prefix:
                edit = (edit, trie[edit])
                if edit not in output:
                    output.append(edit)
                
    output = sorted(output, key=lambda x: x[1], reverse = True)
    return [i[0] for i in output]           
    
def word_filter(trie, pattern, parent = ''):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    if len(pattern) == 0:
        if trie.value != None:
            return [(parent, trie.value)]
        else:
            return []
    
    else:
        ch = pattern[0]
        output = []
        if ch == "?":
            for k, v in trie.children.items():
                output = output + word_filter(v, pattern[1:], parent = parent+k)
        elif ch == "*":
            output = output + word_filter(trie, pattern[1:], parent=parent)
            for k, v in trie.children.items():
                for i in word_filter(v, pattern, parent = parent+k):
                    if i not in output:
                        output.append(i)
        else:
            if ch in trie.children:
                output = output + word_filter(trie.children[ch], pattern[1:], parent = parent+ch)
    
    return output


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    pass
