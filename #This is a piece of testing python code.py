#This is a piece of testing python code
# 两数之和

def two_sum(li, target):
    d = dict()
    for ind, i in enumerate(li):
        d[i] = ind 
        if target - i in d:
            return [d[target - i], d[i]]
    return -1

print(two_sum([2,7, 11, 15], 9))