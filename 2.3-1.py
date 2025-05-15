class Worker:
    def __init__(self, name, surname, rate, days):
        self.name = name
        self.surname = surname
        self.rate = rate
        self.days = days

    def getsalary(self):
        return self.rate * self.days

worker = Worker("Арнольд", "Борисович", 2300, 23)

print(f"Зарплата работника {worker.name} {worker.surname}: {worker.getsalary()} руб.")