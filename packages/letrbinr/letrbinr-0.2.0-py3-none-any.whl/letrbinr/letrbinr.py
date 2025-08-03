import random

class LetrBinr():
    def __init__(self):
        self.letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
                    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " "]
        self.math_list = ["+", "-", "^", "%", "/", "*"]
        self.python = {}
        self.place = {}
        self.variables = {}
        self.functions = {}
        self.exec = {}
    def unbin(self, binary):
        if type(binary) != list:
            binary = list(binary)
        binary.reverse()
        number = 0
        for i in range(len(binary)):
            try:
                number += int(binary[i])*2**i
            except ValueError:
                break
        return number
    def lexer(self):
        python = {"+": "+",
                "-": "-",
                "/": "/",
                "*": "*",
                "^": "^",
                "%": "%",
                "0": "0",
                "1": "1",
                "2": "2",
                "3": "3",
                "4": "4",
                "5": "5",
                "6": "6",
                "7": "7",
                "8": "8",
                "9": "9",
                "lb": "(",
                "rb": ")",
                "!cmpeq": "!=",
                "cmpeq": "==",
                "bg": ">",
                "ls": "<",
                "eq": "=",
                "end": "break",
                "True": "True",
                "False": "False",
                "&": "and",
                "||": "or",
                ":": ":",
                "inf": "float('inf')",
                "spc": " ",
                "say": "print",
                ";": ";",
                "ntr": "\n",
                "tab": "\t",
                "for": "for"}
        for i in range(len(self.letters)):
            python.update({self.letters[i]: self.letters[i]})
        return python
    def parser(self, line):
        self.python = self.lexer()
        line = line.split()
        correct = []
        name = 0
        var = 0
        value = []
        if_st = False
        say = False
        math = False
        fl = False
        talking = False
        math_var = False
        range_char = 0
        for i in range(len(line) - 1):
            if line[i] == "bin" and line[i + 1] != "lb" and "eq" not in line and fl == False and say == False and talking == False:
                correct.append(str(self.unbin(line[i + 1])))
            if line[i] == "ltr" and line[i + 1] != "lb" and "eq" not in line and fl == False and say == False and talking == False:
                correct.append(self.letters[self.unbin(line[i + 1])])
            if ((line[i + 1] in self.math_list and line[i] in self.variables) or math == True) and math_var == False:
                math = True
                if line[i] != ";":
                    if line[i] in self.variables:
                        correct.append(f"int({line[i]})")
                    elif line[i] == "lb":
                        correct.append("(")
                    elif line[i] == "rb":
                        correct.append(")")
                    else:
                        correct.append(self.python[line[i]])
            if line[i] == "true" and line[i + 1] == "lb" or if_st == True and math == False and say == False:
                if_st = True
                if line[i + 1] == "lb" and line[i] == "true":
                    correct.append("if (")
                    i += 2
                    while line[i] != "rb":
                        for key, value3 in self.variables.items():
                            if key == line[i]:
                                correct.append(f" {line[i]} ")
                        if line[i] not in self.variables:
                            for key, value1 in self.python.items():
                                if key == line[i]:
                                    correct.append(f" {self.python[line[i]]} ")
                        i += 1
                    if line[i] == "rb":
                        correct.append("):")
            if (line[i + 1][0] == "0" or line[i + 1][0] == "1") and line[i] == "lb" and line[i - 1] != "eq":
                if line[i - 1] == "ltr":
                    correct.append(self.letters[self.unbin(line[i + 1])])
                if line[i - 1] == "bin":
                    correct.append(str(self.unbin(line[i + 1])))
            if line[i] == "for" or fl == True:
                fl = True
                range_char = line[i]
                i += 1
                if len(line) > 2:
                    if line[i] == "bin":
                        i += 1
                        correct.append(f"for {range_char} in range({self.unbin(line[i])}):")
                if line[i] == "inf":
                    correct.append(f"while True:")
            if line[i] == "say" and line[i + 1] != "var" or say == True:
                say = True
                if line[i] == "say":
                    correct.append("print(f'")
                    if line[i + 1] == "lb":
                        i += 1
                    while line[i] != ";":
                        if line[i] == "bin":
                            correct.append(str(self.unbin(line[i + 1])))
                        if line[i] == "ltr":
                            correct.append(self.letters[(self.unbin(line[i + 1]))])
                        if line[i] in self.variables:
                            lb = "{"
                            rb = "}"
                            correct.append(f"{lb}{line[i]}{rb}")
                        if line[i] == "spc":
                            correct.append(" ")
                        if line[i] == "ntr":
                            correct.append("\n")
                        if line[i] == "tab":
                            correct.append(" "*4)
                        i += 1
                    if line[i] == ";":
                        correct.append("')")
            if line[i] == "talk" or talking == True:
                talking = True
                correct.append("input('")
                if line[i + 1] == "lb":
                    i += 2
                    while line[i] != ";":
                        if line[i] == "bin" and line[i + 1] != "lb":
                            correct.append(str(self.unbin(line[i + 1])))
                            i += 1
                        elif line[i] == "ltr" and line[i + 1] != "lb":
                            correct.append(self.letters[self.unbin(line[i + 1])])
                            i += 1
                        elif line[i] == "bin" and line[i + 1] == "lb":
                            k = 0
                            i += 1
                            while line[i][k] == "0" or line[i][k] == "1":
                                for k in range(len(line[i])):
                                    if k == len(line[i]) - 1:
                                        correct.append(str(self.unbin(line[i])))
                                    if line[i] == "rb":
                                        break
                                k = 0
                                i += 1
                        elif line[i] == "ltr" and line[i + 1] == "lb":
                            i += 1
                            k = 0
                            while line[i][k] == "0" or line[i][k] == "1":
                                for k in range(len(line[i])):
                                    if k == len(line[i]) - 1:
                                        correct.append(self.letters[self.unbin(line[i])])
                                    if line[i] == "rb":
                                        break
                                k = 0
                                i += 1
                        elif line[i] == "spc":
                            correct.append(" ")
                            i += 1
                        elif line[i] == "tab":
                            correct.append("\t")
                            i += 1
                        elif line[i] == "ntr":
                            correct.append("\n")
                            i += 1
                        else:
                            i += 1
                            continue
                    if line[i] == ";":
                        correct.append("')")
                        break
            if line[i][0] in self.letters and fl == False and talking == False and say == False and if_st == False:
                name = line[i]
                if line[i + 1] == "eq":
                    correct.append(f"{name} = ")
                    var = i + 2
                    values = []
                    for where in range(var, len(line) - 1):
                        if line[where] != ";":
                            if line[where] == "bin" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append(str(self.unbin(line[where + 1])))
                                value.append(str(self.unbin(line[where + 1])))
                            if line[where] == "ltr" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append("'")
                                correct.append(self.letters[self.unbin(line[where + 1])])
                                correct.append("'")
                            if line[where] == "True" or line[where] == "False":
                                correct.append(line[where])
                                value.append(line[where])
                            if line[where] == "talk":
                                talking == True
                                break
                            if line[where] in self.variables:
                                if self.variables[line[where]][0] not in self.letters:
                                    correct.append(f"int({line[where]})")
                                    value.append(self.variables[line[where]])
                                    math_var = True
                                else:
                                    correct.append(f"{self.variables[line[where]]}")
                                    value.append(self.variables[line[where]])
                            if line[where] in self.math_list:
                                correct.append(line[where])
                                value.append(line[where])
                                math_var = True
                        if len(values) > 0:
                            value = values
                            value.append(")")
                    self.variables.update({name: "".join(value)})
            if line[i] == "its":
                func_name = 0
                args = []
                i += 1
                correct.append(f"def {line[i]}")
                func_name = line[i]
                if line[i + 1] == "lb":
                    correct.append("(")
                    i += 2
                    while line[i] != "rb":
                        correct.append(line[i])
                        args.append(line[i])
                        if line[i + 1] != "rb":
                            correct.append(", ")
                            args.append(", ")
                        i += 1 
                if line[i] == "rb":
                    correct.append("):")
                self.functions.update({func_name: args})
            if line[i] == "do":
                func_name = line[i + 1]
                i += 1
                if line[i + 1] == "lb":
                    correct.append(func_name)
                    correct.append("(")
                    for arg in range(len(self.functions[func_name])):
                        if self.functions[func_name][arg] != ",":
                            correct.append(self.variables[self.functions[func_name][arg]])
                        else:
                            correct.append(",")
                    correct.append(")")
            if line[i] == "say" and line[i + 1] == "var":
                correct.append("print(self.variables)")
            for key, value2 in self.variables.items():
                if line[i - 1] == "bin" and line[i] == "var" and line[i + 1] == key:
                    value2 = int(eval(value2))
                    self.variables.update({key: value2})
                if line[i - 1] == "ltr" and line[i] == "var" and line[i + 1] == key:
                    value2 = str(eval(value2))
                    self.variables.update({key: value2}) 
            if line[i] == "end":
                correct.append("break")
            if line[i] == "spc":
                correct.append(" ")
            if line[i] == "ntr":
                correct.append("\n")
            if line[i] == "tab":
                correct.append(" "*4)
        correct.append("\n")
        correct = "".join(correct)
        return correct
    def code(self):
        codespace = []
        pycode = []
        start = "a"
        fixpy = ""
        while True:
            line = input(f'{"".join(codespace)}\n')
            start = line
            line = line.split()
            if line == "":
                codespace.append("\n")
                correct = ""
            if len(line) > 1:
                if line[0] == "fix":
                    codespace[int(line[1]) - 1] = ""
                    pycode[int(line[1]) - 1] = ""
                    for j in range(2, len(line)):
                        codespace[int(line[1]) - 1] += f" {line[j]}"
                        fixpy += f" {line[j]}"
                    pycode[int(line[1]) - 1] += f"{self.parser(fixpy)}"
                    fixpy = ""
                if line[0] == "end" and line[1] == "coding":
                    print("your code:", codespace)
                    break
                if line[0] == "run" and line[1] == "code":
                    try:
                        exec("".join(pycode))
                    except Exception as e:
                        print("ERROR!!! ERROR!!! ERROR!!! ERROR!!! ERROR!!!")
                        print("line:", pycode.index(correct) + 1)
                        print(codespace[pycode.index(correct)])
                if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding"):
                    line = start
                    correct = self.parser(line)
                    pycode.append(correct)
                    codespace.append(line)

class LetrBinRAND():
    def __init__(self):
        self.letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
                    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        self.math_list = ["+", "-", "^", "%", "/", "*"]
        self.what = ["for", "&", "||", "lb", "ls", "rb", "ltr", "bg", "bin", "its", "do", "!cmpeq", "cmpeq", 
                     "end", "+", "-", "^", "%", "spc", "*", "/", "tab", "ntr", ";", "eq", "true", "True", "False",
                     "say", "inf", "talk", "var"]
        self.why = ["for", "and", "or", "(", "<", ")", "str", ">", "int", "def", "call", "!=", "==",
                    "break", "+", "-", "**", "%", " ", "*", "/", "    ", "\n", ";", "=", "if", "True", "False", 
                    "print", "float('inf')", "input", "var"]
        self.python = {}
        self.place = {}
        self.variables = {}
        self.functions = {}
        self.exec = {}
    def unbin(self, binary):
        if type(binary) != list:
            binary = list(binary)
        binary.reverse()
        number = 0
        for i in range(len(binary)):
            try:
                number += int(binary[i])*2**i
            except ValueError:
                break
        return number
    def lexer(self):
        random.shuffle(self.what)
        random.shuffle(self.why)
        pairs = list(zip(self.what, self.why))
        random.shuffle(pairs)
        self.python = dict(pairs)
        for i in range(len(self.letters)):
            self.python.update({self.letters[i]: self.letters[i]})
        return self.python
    def parser(self, line):
        line = line.split()
        correct = []
        name = 0
        var = 0
        value = []
        if_st = False
        say = False
        math = False
        fl = False
        talking = False
        math_var = False
        range_char = 0 
        for i in range(len(line) - 1):
            if line[i + 1][0] != "0" and line[i + 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int" and self.python[line[i + 1]] != "(" and fl == False and say == False and talking == False:
                for key, value in self.python.items():
                    for ln in range(len(line)):
                        if self.python[line[ln]] != "=" and ln == len(line) - 1:
                            correct.append(str(self.unbin(self.python[line[i + 1]])))
            if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i]] == "str" and self.python[line[i + 1]] != "(" and fl == False and say == False and talking == False:
                for key, value in self.python.items():
                    for ln in range(len(line)):
                        if self.python[line[ln]] != "=" and ln == len(line) - 1:
                            correct.append(str(self.unbin(self.python[line[i + 1]])))
            if line[i + 1][0] != "0" and line[i + 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and ((self.python[line[i + 1]] in self.math_list and self.python[line[i]] in self.variables) or math == True) and math_var == False:
                math = True
                if self.python[line[i]] != ";":
                    if line[i] in self.variables:
                        correct.append(f"int({line[i]})")
                    else:
                        correct.append(self.python[line[i]])
            if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i]] == "if" and self.python[line[i + 1]] == "(" or if_st == True and math == False and say == False:
                if_st = True
                if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i + 1]] == "(" and self.python[line[i]] == "if":
                    correct.append("if (")
                    i += 2
                    while self.python[line[i]] != ")":
                        if line[i] in self.variables:
                            correct.append(f" {line[i]} ")
                        if line[i] not in self.variables:
                            for key, value1 in self.python.items():
                                if key == line[i]:
                                    correct.append(f" {self.python[line[i]]} ")
                        i += 1
                    if self.python[line[i]] == ")":
                        correct.append("):")
            if (line[i + 1][0] == "0" or line[i + 1][0] == "1") and self.python[line[i]] == "(" and self.python[line[i - 1]] != "=":
                if self.python[line[i - 1]] == "str":
                    correct.append(self.letters[self.unbin(line[i + 1])])
                if self.python[line[i - 1]] == "int":
                    correct.append(str(self.unbin(line[i + 1])))
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "for" or fl == True:
                fl = True
                range_char = line[i]
                i += 1
                if len(line) > 2:
                    if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int":
                        i += 1
                        correct.append(f"for {range_char} in range({self.unbin(line[i])}):")
                if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "float('inf')":
                    correct.append(f"while True:")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "print" and self.python[line[i + 1]] != "var" or say == True:
                say = True
                if self.python[line[i]] == "print":
                    correct.append("print(f'")
                    if self.python[line[i + 1]] == "(":
                        i += 1
                    while self.python[line[i]] != ";":
                        if self.python[line[i]] == "int":
                            correct.append(str(self.unbin(line[i + 1])))
                        if self.python[line[i]] == "str":
                            correct.append(self.letters[(self.unbin(line[i + 1]))])
                        if self.python[line[i]] in self.variables:
                            lb = "{"
                            rb = "}"
                            correct.append(f"{lb}{self.python[line[i]]}{rb}")
                        if self.python[line[i]] == " ":
                            correct.append(" ")
                        if self.python[line[i]] == "\n":
                            correct.append("\n")
                        if self.python[line[i]] == "    ":
                            correct.append(" "*4)
                        i += 1
                    if self.python[line[i]] == ";":
                        correct.append("')")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "input" or talking == True:
                talking = True
                if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i + 1]] == "(":
                    correct.append("input('")
                    i += 2
                    print(line[i])
                    if line[i][0] != "0" and line[i][0] != "1":
                        while True:
                            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == ";":
                                correct.append("')")
                                break
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int":
                                correct.append(str(self.unbin(line[i + 1])))
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "str":
                                correct.append(self.letters[self.unbin(line[i + 1])])
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == " ":
                                correct.append(" ")
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "    ":
                                correct.append("\t")
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "\n":
                                correct.append("\n")
                                i += 1
                            else:
                                i += 1
                                continue
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]][0] in self.letters and fl == False and talking == False and say == False and if_st == False:
                name = line[i]
                if line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i + 1]] == "=":
                    correct.append(f"{name} = ")
                    var = i + 2
                    values = []
                    for where in range(var, len(line) - 1):
                        if line[where][0] != "0" and line[where][0] != "1" and self.python[line[where]] != ";":
                            if self.python[line[where]] == "int" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append(str(self.unbin(line[where + 1])))
                                value.append(str(self.unbin(line[where + 1])))
                            if self.python[line[where]] == "str" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append("'")
                                correct.append(self.letters[self.unbin(line[where + 1])])
                                correct.append("'")
                            if self.python[line[where]] == "True" or self.python[line[where]] == "False":
                                correct.append(self.python[line[where]])
                                value.append(self.python[line[where]])
                            if self.python[line[where]] == "input":
                                talking == True
                                break
                            if line[where] in self.variables:
                                if self.variables[line[where][0]] not in self.letters:
                                    correct.append(f"int({line[where]})")
                                    value.append(self.variables[line[where]])
                                    math_var = True
                                else:
                                    correct.append(f"{line[where]}")
                                    value.append(self.variables[line[where]])
                            if self.python[line[where]] in self.math_list:
                                correct.append(self.python[line[where]])
                                value.append(self.python[line[where]])
                                math_var = True
                        if len(values) > 0:
                            value = values
                            value.append(")")
                    self.variables.update({name: "".join(value)})
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "def":
                func_name = 0
                args = []
                i += 1
                correct.append(f"def {self.python[line[i]]}")
                func_name = self.python[line[i]]
                if self.python[line[i + 1]] == "(":
                    correct.append("(")
                    i += 2
                    while self.python[line[i]] != ")":
                        correct.append(line[i])
                        args.append(line[i])
                        if self.python[line[i + 1]] != ")":
                            correct.append(", ")
                            args.append(", ")
                        i += 1 
                if self.python[line[i]] == ")":
                    correct.append("):")
                self.functions.update({func_name: args})
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "call":
                func_name = line[i + 1]
                i += 1
                if self.python[line[i + 1]] == "(":
                    correct.append(func_name)
                    correct.append("(")
                    for arg in range(len(self.functions[func_name])):
                        if self.functions[func_name][arg] != ",":
                            correct.append(self.variables[self.functions[func_name][arg]])
                        else:
                            correct.append(",")
                    correct.append(")")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "print" and self.python[line[i + 1]] == "var":
                correct.append("print(self.variables)")
            if line[i] in self.variables:
                if line[i - 1][0] != "0" and line[i - 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1":
                    if self.python[line[i - 1]] == "int" and self.python[line[i]] == "var" and self.python[line[i + 1]] == key:
                        value2 = int(eval(value2))
                        self.variables.update({key: value2})
                    if self.python[line[i - 1]] == "str" and self.python[line[i]] == "var" and self.python[line[i + 1]] == key:
                        value2 = str(eval(value2))
                        self.variables.update({key: value2})
            if line[i][0] != "0" and line[i][0] != "1":
                if self.python[line[i]] == "break":
                    correct.append("break")
                if self.python[line[i]] == " ":
                    correct.append(" ")
                if self.python[line[i]] == "\n":
                    correct.append("\n")
                if self.python[line[i]] == "    ":
                    correct.append(" "*4)
        correct.append("\n")
        correct = "".join(correct)
        return correct
    def code(self):
        codespace = []
        pycode = []
        start = "a"
        fixpy = ""
        while True:
            line = input(f'{"".join(codespace)}\n')
            start = line
            line = line.split()
            if line == "":
                codespace.append("\n")
                correct = ""
            if len(line) > 1:
                if line[0] == "fix":
                    codespace[int(line[1]) - 1] = ""
                    pycode[int(line[1]) - 1] = ""
                    for j in range(2, len(line)):
                        codespace[int(line[1]) - 1] += f" {line[j]}"
                        fixpy += f" {line[j]}"
                    pycode[int(line[1]) - 1] += f"{self.parser(fixpy)}"
                    fixpy = ""
                if line[0] == "end" and line[1] == "coding":
                    print("your code:", codespace)
                    break
                if line[0] == "run" and line[1] == "code":
                    try:
                        exec("".join(pycode))
                    except Exception as e:
                        print("ERROR!!! ERROR!!! ERROR!!! ERROR!!! ERROR!!!")
                        print("line:", pycode.index(correct) + 1)
                        print(codespace[pycode.index(correct)])
                if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding"):
                    line = start
                    correct = self.parser(line)
                    pycode.append(correct)
                    codespace.append(line)