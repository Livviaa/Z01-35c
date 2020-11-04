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
    if char in "0123456789.":
        return True
    else:
        return False


def operatorPriority(char):
    if char == '(':
        return 0
    elif char == '+' or char == '-' or char == ')':
        return 1
    elif char == '*' or char == '/':
        return 2


def grow(expression):
    postfix = ""
    stack = Stack()
    string = ""

    for token in expression:
        if isOperand(token):
            postfix += token
        elif token in "+-*/":
            postfix += " "
            while (not stack.isEmpty()) and operatorPriority(token) <= operatorPriority(stack.top()):
                postfix += stack.pop() + " "
            stack.push(token)
        elif token == "(":
            stack.push(token)
        elif token == ")":
            try:
                while (stack.top() is not None) and stack.top() != "(":
                    postfix += " " + stack.pop()
                stack.pop()
            except IndexError:
                print("BŁĄD: W wyrażeniu źle umieszczono nawiasy!")
                exit()

    while not stack.isEmpty():
        string = stack.pop()
        if string is not None and string in "()":
            if string in "()":
                print("BŁĄD: W wyrażeniu źle umieszczono nawiasy!")
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
            right = stack.pop()
            left = stack.pop()
            parent = Vertex(token)
            parent.left = left
            parent.right = right
            stack.push(parent)

    root = stack.pop()
    print(expression + " = ", end="")
    return root


def evaluate(tree_root):
    if tree_root is None:
        return 0
    if tree_root.left is None and tree_root.right is None:
        return tree_root.value

    result_left = evaluate(tree_root.left)
    result_right = evaluate(tree_root.right)

    if tree_root.value == "+":
        return result_left + result_right
    elif tree_root.value == "-":
        return result_left - result_right
    elif tree_root.value == "*":
        return result_left * result_right
    elif tree_root.value == "/":
        return result_left / result_right


def tree_visualization(root, level):
    if root is not None:
        tree_visualization(root.left, level + 1)
        print(level * '\t ' + '->', root.value)
        tree_visualization(root.right, level + 1)


if __name__ == "__main__":
    tree = grow("12.2+2*(3*4-12.5/2.5)")
    print(evaluate(tree))
    print("\n")
    tree_visualization(tree, 0)
