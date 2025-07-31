import random

class StringFuncs:

    @staticmethod
    def change(var):
        letters = [char for char in var if char.isalpha()]
        times = len(letters) * 4
        if isinstance(var, (list, int, bool)):
         raise ValueError("input can't be a list or a int or a bool, string only ")
        E = 0
        letter_cap = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        letter_nonCAP = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                 "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        while E < times:
         var = var.lower().replace(random.choice(letter_nonCAP), random.choice(letter_nonCAP))
         var = var.lower().replace(random.choice(letter_cap), random.choice(letter_cap))
         var = var.lower().replace(random.choice(letter_cap), random.choice(letter_nonCAP))
         E += 1   
        return var
    @staticmethod
    def symbols(var):
        letters = [char for char in var if char.isalpha()]
        times = len(letters) * 4
        if isinstance(var, (list, int, bool)):
         raise ValueError("input can't be a list or a int or a bool, string only ")
        E = 0
        all_linguistic_letters = [  "ʔ", "ʕ", "ʘ", "ǀ", "ǃ", "ǂ", "ǁ", "ɬ", "ɮ", 
    "ɹ", "ɻ", "ɽ", "ɾ", "ɢ","ʜ", "ʢ", "ʡ", "ɺ", "ʍ", "ɥ", "ɧ", "ɕ", "ʑ", "ʈ", "ɖ",
    "ʂ", "ʐ","ɟ", "ɡ", "ɲ", "ɳ", "ɴ", "ɸ", "β", "θ", "ð", "ɣ", "χ", "ʀ", "ʁ",
    "ʃ", "ʒ", "ʉ", "ɨ", "ʊ", "ɯ", "ɤ", "ʌ", "ə", "ɚ", "ɝ","ꜧ",  "ʮ",  "ʯ",  "ʍ", 
    "ʭ",  "ʮ", "ʰ",  "ʷ",  "ˠ",  "ˤ",  "ᵻ",  "ᵶ",  "ᶣ",  "ᶭ",  "᷈",  "᷉",  "᷊",  
    "᷋","᷌","᷍","᷎","᷏","᷐","᷑","ʗ","ʘ"
]
        letter_cap = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        letter_nonCAP = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                 "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        while E < times:
            var = var.lower().replace(random.choice(letter_nonCAP), random.choice(all_linguistic_letters))
            var = var.lower().replace(random.choice(letter_cap), random.choice(all_linguistic_letters))
            var = var.lower().replace(random.choice(numbers), random.choice(all_linguistic_letters))
            E += 1
        return var        


    @staticmethod
    def move(var):
        
        letters = [char for char in var if char.isalpha()]
        times = len(letters) * 4
        if isinstance(var, (list, int, bool)):
            raise ValueError("input can't be a list or a int or a bool, string only ")
        var = var_list = list(var)
        random.shuffle(var_list)
        shuffled = ''.join(var_list)
        var = shuffled
        return var

string = StringFuncs()