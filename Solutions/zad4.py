from random import randint

args = ['p', 'k', 'n']
results = [0, 0, 0]


def judge(player, comp):
    if player == comp:
        print("REMIS")
        results[1] += 1
    elif player == "p":
        if comp == "k":
            print("RUNDA WYGRANA")
            results[0] += 1
        else:
            print("RUNDA PRZEGRANA")
            results[2] += 1
    elif player == "k":
        if comp == "n":
            print("RUNDA WYGRANA")
            results[0] += 1
        else:
            print("RUNDA PRZEGRANA")
            results[2] += 1
    else:
        if comp == "p":
            print("RUNDA WYGRANA")
            results[0] += 1
        else:
            print("RUNDA PRZEGRANA")
            results[2] += 1


def game(games):
    for i in range(games):
        while True:
            print("Dokonaj wyboru p-papier, k-kamień czy n-nożyce: ", end="")
            player = input()
            if player != "p" and player != "k" and player != "n":
                print("Nieprawidłowy wybór!")
                continue
            else:
                break
        comp: str = args[randint(0, 2)]
        print("Komputer wybrał: " + comp)

        judge(player, comp)

    print("Statystyki:")
    print("Gier: " + str(games))
    print("Wygranych: " + str(results[0]))
    print("Przegranych: " + str(results[2]))
    print("Remisów: " + str(results[1]))

    if results[0] > results[2]:
        print("WYGRAŁEŚ!")
    elif results[2] > results[0]:
        print("PRZEGRAŁEŚ!")
    else:
        print("ZREMISOWAŁEŚ!")


if __name__ == "__main__":
    print("Zagraj w papier, kamień, nożyce")
    try:
        print("Podaj liczbę rund: ", end="")
        rounds = int(input())
        game(rounds)
    except ValueError:
        print("Podano złą wartość!")
        exit()
        
