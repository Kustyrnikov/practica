class Numbers:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def show(self):
        print(f"Числа: {self.a} и {self.b}")

    def set(self, a, b):
        self.a, self.b = a, b

    def sum(self):
        return self.a + self.b

    def max(self):
        return self.a if self.a > self.b else self.b

n = Numbers(15, 25)
n.show()
print(f"Сумма: {n.sum()}, Наибольшее значение: {n.max()}")

n.set(33, 17)
n.show()
print(f"Сумма: {n.sum()}, Наибольшее значение: {n.max()}")

n.set(53, -23)
n.show()
print(f"Сумма: {n.sum()}, Наибольшее значение: {n.max()}")