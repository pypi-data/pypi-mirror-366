from collections import Counter

class english:
  @staticmethod

  def info():
    print("| extra_chars(word, terms)")
    print("> func: detects the term that cannot be made up of letters in the word")
    print("> word: the main word that makes up terms")
    print("> terms: list of terms in the question")
    print()
    print("| word_value(values, term)")
    print("> func: calculate the sum of all letters in term")
    print("> values: list of letters and their value in the form LETTER:VALUE")
    print("> term: the term to find the value of")
    print()
    print("| substitution(word, code, type, inpt)")
    print("> func: a substitution cipher")
    print("> word: the word/decoded version to map each letter to a symbol")
    print("> code: the code/encoded version that maps onto each letter of the word")
    print("> type: encode (0) or decode (1)")
    print("> inpt: list of words or codes to encode or decode")

  def extra_chars(word, terms):
    word_count = Counter(word)
    for term in terms:
      term_count = Counter(term)
      if any(term_count[char] > word_count.get(char, 0) for char in term_count):
        print(term)

  def word_value(values, term):
      letter_values = {}
      for item in values:
          letter, value = item.split(":")
          letter = letter.strip().lower()
          value = int(value.strip())
          letter_values[letter] = value

      term_lower = term.lower()
      total = sum(letter_values.get(char, 0) for char in term_lower)
      print(f"{term}: {total}")

  def substitution(word, code, type, inpt):
      if len(word) != len(code):
          raise ValueError("word and code must be the same length")

      encode_map = {w: c for w, c in zip(word, code)}
      decode_map = {c: w for w, c in zip(word, code)}

      output = []
      if type == 0:  # encode
          for item in inpt:
              encoded = ''.join(encode_map.get(ch, ch) for ch in item)
              output.append(f"{item}: {encoded}")
      elif type == 1:  # decode
          for item in inpt:
              decoded = ''.join(decode_map.get(ch, ch) for ch in item)
              output.append(f"{item}: {decoded}")
      else:
          raise ValueError("type must be 0 (encode) or 1 (decode)")
      return output

import re, sympy
from sympy import symbols, Eq, solve, sqrt

class math:
  @staticmethod

  def inverse(function):
    expr = function.replace('^', '**')
    expr = re.sub(r'cbrt\(([^)]+)\)', r'(\1)**(1/3)', expr)
    
    match = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\(x\)\s*=\s*(.+)', expr)
    if match:
        funcname, rhs = match.groups()
        x = symbols('x')
        y = symbols(funcname)
        lhs = y
    else:
        match2 = re.match(r'\s*y\s*=\s*(.+)', expr)
        if not match2:
            print("Input must be of the form 'f(x) = ...' or 'y = ...'")
            return
        funcname = 'f'
        rhs = match2.group(1)
        x = symbols('x')
        y = symbols('y')
        lhs = y

    rhs_sym = sympy.sympify(rhs, locals={'sqrt': sqrt})
    equation = Eq(lhs, rhs_sym)
    sol = solve(equation, x)
    if not sol:
        print("Could not find inverse.")
        return
    inv = sol[0]

    inv_str = str(inv)
    inv_str = inv_str.replace('**(1/2)', '^0.5')
    inv_str = inv_str.replace('**(1/3)', '^0.3333333333')
    inv_str = re.sub(r'\*\*([0-9]+)', r'^\1', inv_str)
    inv_str = re.sub(r'\b%s\b' % re.escape(funcname), 'x', inv_str)

    print(f"{funcname}\u207B\u00B9(x) = {inv_str}")

class util:
  @staticmethod

  def clean(x=None):
    if x is None:
      for i in range(0, 100):
        print(" " * i)
    else:
      for i in range(0, x):
        print(" " * i)