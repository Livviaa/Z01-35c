import os
import sys


def dirTree(path, spaces):
    if spaces == 0:
        print(path)

    for file in os.listdir(path):
        filepath = os.path.join(path, file)

        for i in range(spaces):
            if (i == spaces-1):
                print("|    ", end="")
            else:
                print("|\t", end="")

        print("|--" + file)

        if os.path.isdir(filepath):
            dirTree(filepath, spaces+1)


if __name__ == "__main__":
    dirTree(sys.argv[1], 0)
