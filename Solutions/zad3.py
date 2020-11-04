import sys


def sortAsc(args):
    try:
        lista = list(map(int, args))
        lista.sort()
        print(lista)
        return lista
    except ValueError:
        print("Nieprawidłowy argument!")
        return


if __name__ == "__main__":
    sortAsc(sys.argv[1:])
    
