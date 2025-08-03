#! /usr/bin/env python3
'''
Things related to Hash Set
'''

# NiemaBF imports
from niemabf.common import open_file, NIEMABF_VERSION
from niemabf.Hash import HASH_FUNCTIONS_HASHSET

# standard imports
from pickle import dump as pdump, load as pload

# useful constants
DUMP_KEYS = ['niemabf_version', 'hashes', 'hash_func_key']

class HashSet:
    '''Hash Set class (only stores hash values, not actual elements)'''
    def __init__(self, hash_func='sha512_str'):
        '''
        Initialize a new Hash Set

        Args:
            hash_func (str): The hash function to use in this Hash Set
        '''
        if hash_func not in HASH_FUNCTIONS_HASHSET:
            raise ValueError("Invalid hash function (%s). Options: %s" % (hash_func, ', '.join(sorted(HASH_FUNCTIONS_HASHSET.keys()))))
        self.niemabf_version = NIEMABF_VERSION
        self.hashes = set()
        self.hash_func_key = hash_func
        self.hash_func = HASH_FUNCTIONS_HASHSET[hash_func]

    def __len__(self):
        '''
        Return the total number of elements in this Hash Set (hash collisions will be treated as a single element)

        Returns:
            int: The total number of elements in this Hash Set
        '''
        return len(self.hashes)

    def __getstate__(self):
        '''
        Get the state (core instance variables) of this Hash Set

        Returns:
            dict: The state (core instance variables) of this Hash Set
        '''
        state = dict()
        for k in DUMP_KEYS:
            state[k] = getattr(self, k)
        return state

    def insert(self, x):
        '''
        Insert an element into this Hash Set

        Args:
            x (object): The element to insert
        '''
        self.hashes.add(self.hash_func(x))

    def find(self, x):
        '''
        Find an element in this Hash Set

        Args:
            x (object): The element to find

        Returns:
            bool: `False` if `x` definitely does not exist in this Hash Set, otherwise `True`
        '''
        return self.hash_func(x) in self.hashes

    def __contains__(self, x):
        '''
        Overload the `in` operator (just call `find`)

        Args:
            x (object): The element to find

        Returns:
            bool: `False` if `x` definitely does not exist in this Hash Set, otherwise `True`
        '''
        return self.find(x)

    def dump(self, fn):
        '''
        Dump this Hash Set into a given file

        Args:
            fn (str): The name of the file into which this Hash Set should be dumped
        '''
        with open_file(fn, mode='wb') as f:
            pdump(self, f)

    def load(fn):
        '''
        Load a Hash Set from a given file

        Args:
            fn (str): The name of the file from which to load a Hash Set

        Returns:
            HashSet: The loaded Hash Set
        '''
        with open_file(fn, mode='rb') as f:
            hs = pload(f)
        hs.hash_func = HASH_FUNCTIONS_HASHSET[hs.hash_func_key]
        return hs
