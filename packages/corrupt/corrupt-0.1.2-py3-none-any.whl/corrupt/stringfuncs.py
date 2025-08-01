import random

class StringFuncs:

    @staticmethod
    def change(var, times=0):
        letters = [char for char in var if char.isalpha()]
        if times == 0:
           times = len(letters) * 4

        if isinstance(var, (list, int, bool)):
         raise ValueError("corrupt.string.change(-->VAR<-- string only,times)")
        
        if isinstance(times, (list, str, bool)):
            raise ValueError("corrupt.string.change(VAR, --->times<--- must be a integer)")
        
        if not isinstance(times, int) or times < 0:
            raise ValueError("corrupt.string.change(VAR, --->times<--- must be a non-negative integer)")
        
        letter_cap = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        
        letter_nonCAP = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                 "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        for _ in range(times):
         var = var.lower().replace(random.choice(letter_nonCAP), random.choice(letter_nonCAP))
         var = var.lower().replace(random.choice(letter_cap), random.choice(letter_cap))
         var = var.lower().replace(random.choice(letter_cap), random.choice(letter_nonCAP))
        return var
    @staticmethod
    def symbols(var, times=0):
        letters = [char for char in var if char.isalpha()]
        if times == 0:
           times = len(letters) * 4

        if isinstance(times, (list, str, bool)):
            raise ValueError("corrupt.string.symbols(VAR, --->times<--- must be a integer)")
        
        if not isinstance(times, int) or times < 0:
            raise ValueError("corrupt.string.symbols(VAR, --->times<--- must be a non-negative integer)")
        
        if isinstance(var, (list, int, bool)):
         raise ValueError("corrupt.string.symbols(-->VAR<-- string only,times)")
        
        symbols_letters = [ "?",",","!","#","@","$","%","&","(",")","]","[","|",";",":",">","<"]

        letter_cap = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        letter_nonCAP = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                 "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        for _ in range(times):
            var = var.lower().replace(random.choice(letter_nonCAP), random.choice(symbols_letters))
            var = var.lower().replace(random.choice(letter_cap), random.choice(symbols_letters))
            var = var.lower().replace(random.choice(numbers), random.choice(symbols_letters))
        return var        


    @staticmethod
    def move(var, times=0):
        letters = [char for char in var if char.isalpha()]
        if times == 0:
            times = len(letters) * 4

        if isinstance(times, (list, str, bool)):
            raise ValueError("corrupt.string.move(VAR, --->times<--- must be a integer)")
        
        if not isinstance(times, int) or times < 0:
            raise ValueError("corrupt.string.move(VAR, --->times<--- must be a non-negative integer)")
        
        if isinstance(var, (list, int, bool)):
            raise ValueError("corrupt.string.move(-->VAR<-- string only,times)")
        
        for _ in range(times):
                   var = var_list = list(var)
                   random.shuffle(var_list)
                   shuffled = ''.join(var_list)
                   var = shuffled
                   
        return var        
string = StringFuncs()