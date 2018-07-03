import itertools

def is_two_pow(check):
    return check > 0 and not (check & (check - 1))

def count_call(f):
    count = {}
    name = f.__name__
    count[name] = 0
    def new_func():
        count[name] += 1
        print(count[name])
        return f()
    return new_func

def all_subsets(s):
    subsets = []
    for i in range(len(s) + 1):
        for comb in list(itertools.combinations(s, i)):
            subsets += list(itertools.permutations(comb))
    return subsets

def hemming(s1, s2):
    count = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            count += 1
    return count

def heminng1(s1, s2):
    return len([1 for x,y in zip(s1,s2) if x!=y])

def vector_mult(a, b):
    return (a[1]*b[2] - a[2]*b[1], -(a[0]*b[2] - a[2]*b[0]), a[0]*b[1] - a[1]*b[0])

print('abcd' > 'abc')