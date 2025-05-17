class Counter:
    def __init__(self, value=0):
        self.value = value

    def up(self):
        self.value += 1

    def down(self):
        self.value -= 1

counter1 = Counter()
print(counter1.value)
counter1.up()
counter1.up()
counter1.up()
print(counter1.value)
counter1.down()
print(counter1.value)

counter2 = Counter(3)
counter2.up()
counter2.down()
counter2.down()
print(counter2.value)