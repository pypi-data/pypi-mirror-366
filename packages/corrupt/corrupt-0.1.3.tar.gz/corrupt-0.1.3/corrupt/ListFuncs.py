import random
from stringfuncs import string
from number import number

class ListFuncs:

    @staticmethod
    def move(var_list=[], times=0):
        if not isinstance(var_list, list):
            raise ValueError("corrupt.list.move(-->VAR<-- must be a list, times)")
        
        if not isinstance(times, int) or times < 0:
            raise ValueError("corrupt.list.move(VAR, --->times<--- must be a non-negative integer)")
        
        if times == 0:
            times = len(var_list) * 2

        temp = var_list.copy()
        for _ in range(times):
            random.shuffle(temp)
        
        return temp

    @staticmethod
    def change(var_list=[], times=0):
        if not isinstance(var_list, list):
            raise ValueError("corrupt.list.change(-->VAR<-- list only, times)")

        if not isinstance(times, int) or times < 0:
            raise ValueError("corrupt.list.change(VAR, --->times<--- must be a non-negative integer)")

        if times == 0:
            times = len(var_list) * 2

        O = ''.join(str(i) for i in var_list)

        if O.isdigit():
            result = number.change(O, times)
        else:
            result = string.change(O, times)

        return list(result)
list = ListFuncs()
