import random
def number(var):
   if var == 0:
      raise ValueError("munber most be more or less than 0")
   if isinstance(var, (list, str, bool)):
      raise ValueError("input can't be a list or a string or a bool, int only")
   var_str = str(var)
   digits = list(var_str)
   E = 0
   times = len(digits) * 2
   while E < times:
      pos = random.randint(0, len(digits) - 1)
      digits[pos] = random.choice("0123456789")
      corrupted = "".join(digits)
      try: 
         var = int(corrupted)
      except ValueError:
         var = 0
      E += 1
   return var
