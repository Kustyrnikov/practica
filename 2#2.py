import sqlite3

conn = sqlite3.connect('bar.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS drinks 
             (id INTEGER PRIMARY KEY, 
             name TEXT, 
             type TEXT, 
             strength REAL, 
             volume REAL, 
             price REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS cocktails 
             (id INTEGER PRIMARY KEY, 
             name TEXT, 
             strength REAL, 
             price REAL,
             total_volume REAL NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS cocktail_parts 
             (cocktail_id INTEGER, 
             drink_id INTEGER, 
             amount REAL)''')

conn.commit()


def add_drink():
    name = input("Название напитка: ")
    type = input("Тип (алкоголь/другой): ")
    strength = 0
    if type == "алкоголь":
        strength = float(input("Крепость (%): "))
    volume = float(input("Объем (мл): "))
    price = float(input("Цена: "))

    c.execute('''INSERT INTO drinks 
                 (name, type, strength, volume, price) 
                 VALUES (?,?,?,?,?)''',
              (name, type, strength, volume, price))
    conn.commit()
    print("Добавлено!")


def show_drinks():
    print("\nСписок напитков:")
    for row in c.execute('SELECT * FROM drinks'):
        print(f"{row[0]}. {row[1]} ({row[4]}мл) - {row[3]}%")


def show_cocktails():
    print("\nСписок коктейлей:")
    cocktails = c.execute('SELECT * FROM cocktails').fetchall()

    if not cocktails:
        print("Коктейлей еще нет")
        return

    for cocktail in cocktails:
        print(f"\n{cocktail[0]}. {cocktail[1]}")
        print(f"Крепость: {cocktail[2]}%")
        print(f"Цена: {cocktail[3]}р")
        print(f"Общий объем: {round(cocktail[4])}мл")
        print("Состав:")

        components = c.execute('''SELECT drinks.name, cocktail_parts.amount 
                               FROM cocktail_parts 
                               JOIN drinks ON cocktail_parts.drink_id = drinks.id 
                               WHERE cocktail_id = ?''', (cocktail[0],)).fetchall()

        for component in components:
            print(f"  - {component[0]}: {component[1]}мл")


def add_cocktail():
    name = input("Название коктейля: ")
    price = float(input("Цена: "))

    parts = []
    while True:
        show_drinks()
        drink_id = input("Выберите напиток (0 - закончить): ")
        if drink_id == "0":
            break
        amount = float(input("Сколько мл добавить: "))
        parts.append((int(drink_id), amount))

    total_strength = 0
    total_volume = sum(amount for _, amount in parts)

    for drink_id, amount in parts:
        c.execute('SELECT strength FROM drinks WHERE id=?', (drink_id,))
        strength = c.fetchone()[0]
        total_strength += strength * amount

    avg_strength = total_strength / total_volume if total_volume > 0 else 0

    c.execute('''INSERT INTO cocktails (name, strength, price, total_volume) 
                 VALUES (?,?,?,?)''', (name, avg_strength, price, total_volume))
    cocktail_id = c.lastrowid

    for drink_id, amount in parts:
        c.execute('''INSERT INTO cocktail_parts 
                     VALUES (?,?,?)''', (cocktail_id, drink_id, amount))

    conn.commit()
    print("Коктейль добавлен!")


def sell():
    print("1 - Коктейль")
    print("2 - Напиток")
    choice = input("Что продать? ")

    if choice == "1":
        show_cocktails()
        cocktail_id = int(input("Номер коктейля: "))
        c.execute('SELECT * FROM cocktail_parts WHERE cocktail_id=?', (cocktail_id,))
        for part in c.fetchall():
            c.execute('UPDATE drinks SET volume = volume - ? WHERE id=?',
                      (part[2], part[1]))
        conn.commit()
        print("Продано!")

    elif choice == "2":
        show_drinks()
        drink_id = int(input("Номер напитка: "))
        amount = float(input("Сколько мл продать: "))
        c.execute('UPDATE drinks SET volume = volume - ? WHERE id=?',
                  (amount, drink_id))
        conn.commit()
        print("Продано!")


def restock():
    show_drinks()
    drink_id = int(input("Номер напитка: "))
    amount = float(input("Сколько мл добавить: "))
    c.execute('UPDATE drinks SET volume = volume + ? WHERE id=?',
              (amount, drink_id))
    conn.commit()
    print("Пополнено!")


while True:
    print("\n1. Добавить напиток")
    print("2. Все напитки")
    print("3. Добавить коктейль")
    print("4. Все коктейли")
    print("5. Продать")
    print("6. Пополнить")
    print("0. Выход")

    choice = input("Выберите: ")

    if choice == "1":
        add_drink()
    elif choice == "2":
        show_drinks()
    elif choice == "3":
        add_cocktail()
    elif choice == "4":
        show_cocktails()
    elif choice == "5":
        sell()
    elif choice == "6":
        restock()
    elif choice == "0":
        conn.close()
        break
    else:
        print("Неверный выбор!")