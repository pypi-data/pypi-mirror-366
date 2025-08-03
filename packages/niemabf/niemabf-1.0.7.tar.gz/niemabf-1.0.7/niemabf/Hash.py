#! /usr/bin/env python3
'''
Things related to hash functions
'''

# standard imports
from hashlib import sha256, sha512

# non-standard imports
try:
    from mmh3 import hash as mmh3_hash # https://mmh3.readthedocs.io/en/stable/api.html#mmh3.hash
except Exception as e:
    import_error_mmh3 = e; mmh3_hash = None

# === BloomFilter Stuff ===
def mmh3_hash_bloomfilter(key, seed):
    '''
    Wrapper for `mmh3.hash`, which returns a signed `int` by default (we want unsigned)

    Args:
        key (str): The input string to hash
        seed (int): The seed value of the hash function

    Returns:
        int: The hash value
    '''
    if mmh3_hash is None:
        raise import_error_mmh3
    return mmh3_hash(key=key, seed=seed, signed=False)

def mmh3_hash_bloomfilter_int(key, seed):
    '''
    Wrapper to compute `mmh3.hash` on an `int` by converting it to `str` first

    Args:
        key (int): The input `int` to hash
        seed (int): The seed value of the hash function

    Returns:
        int: The hash value
    '''
    return mmh3_hash_bloomfilter(str(key), seed)

def mmh3_hash_bloomfilter_iterable(key, seed):
    '''
    Wrapper to compute `mmh3.hash` on iterable data

    Args:
        key (iterable): The input iterable data to hash
        seed (int): The seed value of he hash function

    Returns:
        int: The hash value
    '''
    return mmh3_hash_bloomfilter(''.join(str(HASH_FUNCTIONS_BLOOMFILTER[DEFAULT_HASH_FUNCTION_BLOOMFILTER[type(x)]](x,seed)) for x in key), seed)

# BloomFilter hash functions
HASH_FUNCTIONS_BLOOMFILTER = {
    'mmh3':          mmh3_hash_bloomfilter,
    'mmh3_int':      mmh3_hash_bloomfilter_int,
    'mmh3_iterable': mmh3_hash_bloomfilter_iterable,
}

# default BloomFilter hash function for each type
DEFAULT_HASH_FUNCTION_BLOOMFILTER = {
    int:  'mmh3_int',
    list: 'mmh3_iterable',
    set:  'mmh3_iterable',
    str:  'mmh3',
}

# === HashSet Stuff ===
def mmh3_hash_hashset(key):
    '''
    Wrapper for `mmh3.hash`, which returns a signed `int` by default (we want unsigned)

    Args:
        key (str): The input string to hash

    Returns:
        int: The hash value
    '''
    if mmh3_hash is None:
        raise import_error_mmh3
    return mmh3_hash(key=key, seed=0, signed=False)

def mmh3_hash_hashset_int(key):
    '''
    Wrapper to compute `mmh3.hash` on an `int` by converting it to `str` first

    Args:
        key (int): The input `int` to hash

    Returns:
        int: The hash value
    '''
    return mmh3_hash_hashset(str(key))

def mmh3_hash_hashset_iterable(key):
    '''
    Wrapper to compute `mmh3.hash` on iterable data

    Args:
        key (iterable): The input iterable data to hash
        seed (int): The seed value of he hash function

    Returns:
        int: The hash value
    '''
    return mmh3_hash_hashset(''.join(str(HASH_FUNCTIONS_HASHSET[DEFAULT_HASH_FUNCTION_HASHSET[type(x)]](x)) for x in key))

def sha256_hashset_str(key):
    '''
    Wrapper to computer `hashlib.sha256` on a `str`

    Args:
        key (str): The input string to hash

    Returns:
        int: The hash value
    '''
    return sha256(key.encode()).digest()

def sha256_hashset_int(key):
    '''
    Wrapper to compute `hashlib.sha256` on an `int` by converting it to `str` first

    Args:
        key (int): The input `int` to hash

    Returns:
        int: The hash value
    '''
    return sha256_hashset_str(str(key))

def sha256_hashset_iterable(key):
    '''
    Wrapper to compute `hashlib.sha256` on iterable data

    Args:
        key (iterable): The input iterable data to hash
        seed (int): The seed value of he hash function

    Returns:
        int: The hash value
    '''
    tmp = sha256()
    for x in key:
        tmp.update(DEFAULT_HASH_FUNCTION_HASHSET[type(x)](x))
    return tmp.digest()

def sha512_hashset_str(key):
    '''
    Wrapper to computer `hashlib.sha512` on a `str`

    Args:
        key (str): The input string to hash

    Returns:
        int: The hash value
    '''
    return sha512(key.encode()).digest()

def sha512_hashset_int(key):
    '''
    Wrapper to compute `hashlib.sha512` on an `int` by converting it to `str` first

    Args:
        key (int): The input `int` to hash

    Returns:
        int: The hash value
    '''
    return sha512_hashset_str(str(key))

def sha512_hashset_iterable(key):
    '''
    Wrapper to compute `hashlib.sha512` on iterable data

    Args:
        key (iterable): The input iterable data to hash
        seed (int): The seed value of he hash function

    Returns:
        int: The hash value
    '''
    tmp = sha512()
    for x in key:
        tmp.update(DEFAULT_HASH_FUNCTION_HASHSET[type(x)](x))
    return tmp.digest()

# HashSet hash functions
HASH_FUNCTIONS_HASHSET = {
    'mmh3':            mmh3_hash_hashset,
    'mmh3_int':        mmh3_hash_hashset_int,
    'mmh3_iterable':   mmh3_hash_hashset_iterable,
    'sha256_int':      sha256_hashset_int,
    'sha256_iterable': sha256_hashset_iterable,
    'sha256_str':      sha256_hashset_str,
    'sha512_int':      sha512_hashset_int,
    'sha512_iterable': sha512_hashset_iterable,
    'sha512_str':      sha512_hashset_str,
}

# default HashSet hash function for each type (all need to return `bytes`)
DEFAULT_HASH_FUNCTION_HASHSET = {
    int:  'sha512_int',
    list: 'sha512_iterable',
    set:  'sha512_iterable',
    str:  'sha512_str',
}
