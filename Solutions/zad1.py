import os
import sys


def printDirectory(path, extension):
    for file in os.listdir(path):
        if file.endswith(extension):
            print(file)


if __name__ == "__main__":
    printDirectory(sys.argv[1], sys.argv[2])
    
