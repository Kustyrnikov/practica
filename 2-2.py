candidates = list(map(int, input("Введите кандидатов через запятую: ").split(',')))
target = int(input("Цель: "))
candidates.sort()
result = []

def find(start, path, s):
    if s == target:
        result.append(path.copy())
        return
    for i in range(start, len(candidates)):
        if i > start and candidates[i] == candidates[i-1]:
            continue
        if s + candidates[i] > target:
            continue
        path.append(candidates[i])
        find(i+1, path, s + candidates[i])
        path.pop()

find(0, [], 0)
print(result)