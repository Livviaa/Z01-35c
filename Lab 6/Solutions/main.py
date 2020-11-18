import math
from tkinter import *


class Vertex:
    def __init__(self, value):
        self.left = None
        self.value = value
        self.right = None

    def __str__(self):
        return str(self.value)


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, element):
        self.stack.append(element)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            return None

    def isEmpty(self):
        if not self.stack:
            return True
        else:
            return False

    def top(self):
        if self.stack:
            return self.stack[-1]
        else:
            return None

    def clear(self):
        self.stack = []


def isOperand(char):
    if char in '0123456789.':
        return True
    else:
        return False


def operatorPriority(char):
    if char == '(':
        return 0
    elif char == '+' or char == '-' or char == ')':
        return 1
    elif char == '*' or char == '/' or char == '%':
        return 2
    elif char == '^' or char =='sqrt':
        return 3
    elif char == '!' or char == 'log':
        return 4


def grow(expression):
    postfix = ''
    stack = Stack()
    string = ''

    for token in expression:
        if isOperand(token):
            postfix += token
        elif token in '+-*/^%!':
            postfix += ' '
            while (not stack.isEmpty()) and operatorPriority(token) <= operatorPriority(stack.top()):
                postfix += stack.pop() + " "
            stack.push(token)
        elif token == '(':
            stack.push(token)
        elif token == ')':
            try:
                while (stack.top() is not None) and stack.top() != '(':
                    postfix += ' ' + stack.pop()
                stack.pop()
            except IndexError:
                print('Źle umieszczono nawiasy!')
                exit()
        elif token == 't':
            stack.push('sqrt')
        elif token == 'g':
            stack.push('log')
    postfix += ' '

    while not stack.isEmpty():
        string = stack.pop()
        if string is not None and string in "()":
            if string in '()':
                print('Źle umieszczono nawiasy!')
                exit()
        elif string is not None:
            postfix += " " + string
            string = ""

    for token in postfix:
        if token in "0123456789.":
            string += token
        elif token == " ":
            if string != "":
                node = Vertex(float(string))
                stack.push(node)
            string = ""
        else:
            if token in 'sqrlo':
                continue
            right = stack.pop()
            if token not in '!tg':
                left = stack.pop()
            else:
                left = Vertex(0)
            if token not in 'tg':
                parent = Vertex(token)
            elif token == 't':
                parent = Vertex('sqrt')
            elif token == 'g':
                parent = Vertex('log')
            parent.left = left
            parent.right = right
            stack.push(parent)

    root = stack.pop()
    print(expression + " = ")
    # print(postfix)
    return root


def evaluate(tree_root):
    if tree_root is None:
        return 0
    if tree_root.left is None and tree_root.right is None:
        return tree_root.value

    result_left = evaluate(tree_root.left)
    result_right = evaluate(tree_root.right)

    if tree_root.value == '+':
        return result_left + result_right
    elif tree_root.value == '-':
        return result_left - result_right
    elif tree_root.value == '*':
        return result_left * result_right
    elif tree_root.value == '/':
        return result_left / result_right
    elif tree_root.value == '^':
        return pow(result_left, result_right)
    elif tree_root.value == '%':
        return result_left % result_right
    elif tree_root.value == '!':
        return math.gamma(result_right+1)
    elif tree_root.value == 'log':
        return math.log10(result_right)
    elif tree_root.value == 'sqrt':
        return math.sqrt(result_right)

def tree_visualization(root, level=0):
    if root is not None:
        tree_visualization(root.left, level + 1)
        print(level * '\t ' + '->', root.value)
        tree_visualization(root.right, level + 1)


def addToExp(character):
    current = entry.get()
    entry.delete(0, END)
    entry.insert(0, current + character)


def clear():
    entry.delete(0, END)


def evalBtn():
    try:
        tree = grow(entry.get())
        tree_visualization(tree)
        entry.delete(0, END)
        result = evaluate(tree)
        entry.insert(0, result)
    except:
        entry.delete(0, END)
        entry.insert(0, 'ERROR')


def delete():
    current = entry.get()
    entry.delete(0, END)
    entry.insert(0, current[:-1])


def absolute_val():
    current = entry.get()
    tree = grow(current)
    tree_visualization(tree)
    res = evaluate(tree)
    if current != 'ERROR':
        entry.delete(0, END)
        entry.insert(0, abs(float(res)))


calcUI = Tk()
calcUI.title('Kalkulator')
entry = Entry(calcUI, borderwidth=2, font=('Calibri', 20), justify='right')
entry.grid(row=0, column=0, columnspan=4, pady=10)


clearBtn = Button(calcUI, text='C', height=2, width=7, command=clear).grid(row=7, column=0, padx=2, pady=2)
btn0 = Button(calcUI, text='0', height=2, width=7, command=lambda: addToExp('0')).grid(row=7, column=1, padx=2, pady=2)
decimal = Button(calcUI, text='.', height=2, width=7, command=lambda: addToExp('.')).grid(row=7, column=2, padx=2, pady=2)
equals = Button(calcUI, text='=', height=2, width=7, command=evalBtn).grid(row=7, column=3, padx=2, pady=2)
btn1 = Button(calcUI, text='1', height=2, width=7, command=lambda: addToExp('1')).grid(row=6, column=0, padx=2, pady=2)
btn2 = Button(calcUI, text='2', height=2, width=7, command=lambda: addToExp('2')).grid(row=6, column=1, padx=2, pady=2)
btn3 = Button(calcUI, text='3', height=2, width=7, command=lambda: addToExp('3')).grid(row=6, column=2, padx=2, pady=2)
plus = Button(calcUI, text='+', height=2, width=7, command=lambda: addToExp('+')).grid(row=6, column=3, padx=2, pady=2)
btn4 = Button(calcUI, text='4', height=2, width=7, command=lambda: addToExp('4')).grid(row=5, column=0, padx=2, pady=2)
btn5 = Button(calcUI, text='5', height=2, width=7, command=lambda: addToExp('5')).grid(row=5, column=1, padx=2, pady=2)
btn6 = Button(calcUI, text='6', height=2, width=7, command=lambda: addToExp('6')).grid(row=5, column=2, padx=2, pady=2)
minus = Button(calcUI, text='−', height=2, width=7, command=lambda: addToExp('-')).grid(row=5, column=3, padx=2, pady=2)
btn7 = Button(calcUI, text='7', height=2, width=7, command=lambda: addToExp('7')).grid(row=4, column=0, padx=2, pady=2)
btn8 = Button(calcUI, text='8', height=2, width=7, command=lambda: addToExp('8')).grid(row=4, column=1, padx=2, pady=2)
btn9 = Button(calcUI, text='9', height=2, width=7, command=lambda: addToExp('9')).grid(row=4, column=2, padx=2, pady=2)
multiply = Button(calcUI, text='✕', height=2, width=7, command=lambda: addToExp('*')).grid(row=4, column=3, padx=2, pady=2)
left_bracket = Button(calcUI, text='(', height=2, width=7, command=lambda: addToExp('(')).grid(row=3, column=0, padx=2, pady=2)
right_bracket = Button(calcUI, text=')', height=2, width=7, command=lambda: addToExp(')')).grid(row=3, column=1, padx=2, pady=2)
sqrt = Button(calcUI, text='sqrt(x)', height=2, width=7, command=lambda: addToExp('sqrt(')).grid(row=3, column=2, padx=2, pady=2)
div = Button(calcUI, text='/', height=2, width=7, command=lambda: addToExp('/')).grid(row=3, column=3, padx=2, pady=2)
absBtn = Button(calcUI, text='|x|', height=2, width=7, command=absolute_val).grid(row=2, column=0, padx=2, pady=2)
rev = Button(calcUI, text='1/x', height=2, width=7, command=lambda: addToExp('1/(')).grid(row=2, column=1, padx=2, pady=2)
log10 = Button(calcUI, text='log(x)', height=2, width=7, command=lambda: addToExp('log(')).grid(row=2, column=2, padx=2, pady=2)
modulo = Button(calcUI, text='mod(x)', height=2, width=7, command=lambda: addToExp('%')).grid(row=2, column=3, padx=2, pady=2)
power = Button(calcUI, text='x^y', height=2, width=7, command=lambda: addToExp('^')).grid(row=1, column=0, padx=2, pady=2)
factorial = Button(calcUI, text='x!', height=2, width=7, command=lambda: addToExp('!')).grid(row=1, column=1, padx=2, pady=2)
delBtn = Button(calcUI, text='⌫', height=2, width=17, command=delete).grid(row=1, column=2, columnspan=2, padx=2, pady=2)
calcUI.mainloop()
