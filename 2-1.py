J = input("Введите строку «драгоценности»: ")
S = input("Введите строку «камни»: ")

count = 0

for stone in S:
    if stone in J:
        count += 1

print(f"В строке {S} - {count} символа(ов) являются «драгоценностями»")