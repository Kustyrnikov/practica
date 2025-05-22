import sqlite3
from datetime import datetime


class BarManager:
    def __init__(self, db_name='bar.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        queries = [
            '''CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT CHECK(type IN ('alcohol', 'other')) NOT NULL,
                strength REAL,
                volume REAL NOT NULL,
                price REAL NOT NULL
            )''',

            '''CREATE TABLE IF NOT EXISTS cocktails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                total_volume REAL NOT NULL,
                price REAL NOT NULL,
                strength REAL
            )''',

            '''CREATE TABLE IF NOT EXISTS cocktail_components (
                cocktail_id INTEGER,
                ingredient_id INTEGER,
                quantity REAL NOT NULL,
                FOREIGN KEY(cocktail_id) REFERENCES cocktails(id),
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
            )''',

            '''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT CHECK(type IN ('sale', 'restock')) NOT NULL,
                item_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )'''
        ]

        for query in queries:
            self.conn.execute(query)
        self.conn.commit()

    # Ingredients management
    def add_ingredient(self, name, ingredient_type, strength, volume, price):
        if ingredient_type == 'alcohol' and strength is None:
            raise ValueError("Alcohol must have strength value")

        self.conn.execute('''INSERT INTO ingredients 
                          (name, type, strength, volume, price)
                          VALUES (?, ?, ?, ?, ?)''',
                          (name, ingredient_type, strength, volume, price))
        self.conn.commit()

    def update_ingredient_stock(self, ingredient_id, quantity):
        self.conn.execute('''UPDATE ingredients 
                           SET volume = volume + ? 
                           WHERE id = ?''', (quantity, ingredient_id))
        self.conn.commit()

    def get_ingredient(self, ingredient_id):
        return self.conn.execute('''SELECT * FROM ingredients 
                                 WHERE id = ?''', (ingredient_id,)).fetchone()

    # Cocktails management
    def create_cocktail(self, name, components, price):
        total_volume = sum(qty for _, qty in components)
        alcohol_volume = 0
        total_strength = 0

        for ing_id, qty in components:
            ingredient = self.get_ingredient(ing_id)
            if not ingredient:
                raise ValueError(f"Ingredient {ing_id} not found")
            if ingredient[2] == 'alcohol':
                alcohol_volume += qty
                total_strength += ingredient[3] * qty

        strength = total_strength / total_volume if alcohol_volume > 0 else 0

        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO cocktails 
                        (name, total_volume, price, strength)
                        VALUES (?, ?, ?, ?)''',
                       (name, total_volume, price, strength))
        cocktail_id = cursor.lastrowid

        for ing_id, qty in components:
            cursor.execute('''INSERT INTO cocktail_components 
                           VALUES (?, ?, ?)''',
                           (cocktail_id, ing_id, qty))
        self.conn.commit()
        return cocktail_id

    # Operations
    def sell_item(self, item_type, item_id, quantity):
        if item_type == 'cocktail':
            components = self.conn.execute('''SELECT ingredient_id, quantity 
                                            FROM cocktail_components 
                                            WHERE cocktail_id = ?''',
                                           (item_id,)).fetchall()
            for ing_id, qty in components:
                current_volume = self.get_ingredient(ing_id)[4]
                if current_volume < qty * quantity:
                    raise ValueError("Not enough ingredients in stock")

            for ing_id, qty in components:
                self.update_ingredient_stock(ing_id, -qty * quantity)
        else:
            self.update_ingredient_stock(item_id, -quantity)

        self.record_transaction('sale', item_id, quantity)

    def restock(self, ingredient_id, quantity):
        self.update_ingredient_stock(ingredient_id, quantity)
        self.record_transaction('restock', ingredient_id, quantity)

    def record_transaction(self, transaction_type, item_id, quantity):
        self.conn.execute('''INSERT INTO transactions 
                          (type, item_id, quantity, timestamp)
                          VALUES (?, ?, ?, ?)''',
                          (transaction_type, item_id, quantity, datetime.now()))
        self.conn.commit()

    # Reporting
    def list_ingredients(self):
        return self.conn.execute('''SELECT * FROM ingredients''').fetchall()

    def list_cocktails(self):
        return self.conn.execute('''SELECT * FROM cocktails''').fetchall()

    def get_cocktail_components(self, cocktail_id):
        return self.conn.execute('''SELECT i.name, cc.quantity 
                                 FROM cocktail_components cc
                                 JOIN ingredients i ON cc.ingredient_id = i.id
                                 WHERE cocktail_id = ?''',
                                 (cocktail_id,)).fetchall()


class BarInterface:
    def __init__(self):
        self.manager = BarManager()

    def show_main_menu(self):
        while True:
            print("\n=== Bar Management System ===")
            print("1. Manage Ingredients")
            print("2. Manage Cocktails")
            print("3. Perform Operations")
            print("4. View Reports")
            print("5. Exit")

            choice = input("Select option: ")

            if choice == '1':
                self.manage_ingredients()
            elif choice == '2':
                self.manage_cocktails()
            elif choice == '3':
                self.perform_operations()
            elif choice == '4':
                self.view_reports()
            elif choice == '5':
                self.manager.conn.close()
                break
            else:
                print("Invalid choice!")

    def manage_ingredients(self):
        while True:
            print("\n=== Ingredients Management ===")
            print("1. Add New Ingredient")
            print("2. View All Ingredients")
            print("3. Restock Ingredient")
            print("4. Back to Main Menu")

            choice = input("Select option: ")

            if choice == '1':
                self.add_ingredient()
            elif choice == '2':
                self.view_ingredients()
            elif choice == '3':
                self.restock_ingredient()
            elif choice == '4':
                break
            else:
                print("Invalid choice!")

    def add_ingredient(self):
        try:
            name = input("Ingredient name: ")
            ingredient_type = input("Type (alcohol/other): ").lower()
            strength = None
            if ingredient_type == 'alcohol':
                strength = float(input("Alcohol strength (%): "))
            volume = float(input("Initial volume (ml): "))
            price = float(input("Price per unit: "))

            self.manager.add_ingredient(name, ingredient_type, strength, volume, price)
            print("Ingredient added successfully!")
        except Exception as e:
            print(f"Error: {e}")

    def view_ingredients(self):
        ingredients = self.manager.list_ingredients()
        for ing in ingredients:
            print(f"\nID: {ing[0]}")
            print(f"Name: {ing[1]}")
            print(f"Type: {ing[2]}")
            if ing[3]: print(f"Strength: {ing[3]}%")
            print(f"Volume: {ing[4]}ml")
            print(f"Price: ${ing[5]:.2f}")

    def restock_ingredient(self):
        try:
            self.view_ingredients()
            ing_id = int(input("\nEnter ingredient ID to restock: "))
            quantity = float(input("Enter restock quantity (ml): "))
            self.manager.restock(ing_id, quantity)
            print("Restock successful!")
        except Exception as e:
            print(f"Error: {e}")

    def manage_cocktails(self):
        while True:
            print("\n=== Cocktails Management ===")
            print("1. Create New Cocktail")
            print("2. View All Cocktails")
            print("3. View Cocktail Recipe")
            print("4. Back to Main Menu")

            choice = input("Select option: ")

            if choice == '1':
                self.create_cocktail()
            elif choice == '2':
                self.view_cocktails()
            elif choice == '3':
                self.view_cocktail_recipe()
            elif choice == '4':
                break
            else:
                print("Invalid choice!")

    def create_cocktail(self):
        try:
            name = input("Cocktail name: ")
            price = float(input("Cocktail price: $"))

            components = []
            while True:
                self.view_ingredients()
                ing_id = input("\nEnter ingredient ID (or 'done' to finish): ")
                if ing_id.lower() == 'done':
                    break
                quantity = float(input("Enter quantity (ml): "))
                components.append((int(ing_id), quantity))

            if not components:
                raise ValueError("Cocktail must have at least one ingredient")

            self.manager.create_cocktail(name, components, price)
            print("Cocktail created successfully!")
        except Exception as e:
            print(f"Error: {e}")

    def view_cocktails(self):
        cocktails = self.manager.list_cocktails()
        for cocktail in cocktails:
            print(f"\nID: {cocktail[0]}")
            print(f"Name: {cocktail[1]}")
            print(f"Volume: {cocktail[2]}ml")
            print(f"Price: ${cocktail[3]:.2f}")
            print(f"Strength: {cocktail[4]:.1f}%")

    def view_cocktail_recipe(self):
        try:
            self.view_cocktails()
            cocktail_id = int(input("\nEnter cocktail ID to view recipe: "))
            components = self.manager.get_cocktail_components(cocktail_id)
            print("\nCocktail Recipe:")
            for name, qty in components:
                print(f"- {name}: {qty}ml")
        except Exception as e:
            print(f"Error: {e}")

    def perform_operations(self):
        while True:
            print("\n=== Operations ===")
            print("1. Sell Cocktail")
            print("2. Sell Ingredient")
            print("3. Back to Main Menu")

            choice = input("Select option: ")

            if choice == '1':
                self.sell_cocktail()
            elif choice == '2':
                self.sell_ingredient()
            elif choice == '3':
                break
            else:
                print("Invalid choice!")

    def sell_cocktail(self):
        try:
            self.view_cocktails()
            cocktail_id = int(input("\nEnter cocktail ID to sell: "))
            quantity = int(input("Enter quantity: "))
            self.manager.sell_item('cocktail', cocktail_id, quantity)
            print("Sale completed successfully!")
        except Exception as e:
            print(f"Error: {e}")

    def sell_ingredient(self):
        try:
            self.view_ingredients()
            ing_id = int(input("\nEnter ingredient ID to sell: "))
            quantity = float(input("Enter quantity (ml): "))
            self.manager.sell_item('ingredient', ing_id, quantity)
            print("Sale completed successfully!")
        except Exception as e:
            print(f"Error: {e}")

    def view_reports(self):
        print("\n=== Reports ===")
        print("1. Current Stock")
        print("2. Transaction History")
        choice = input("Select report: ")

        if choice == '1':
            self.view_ingredients()
        elif choice == '2':
            self.view_transactions()
        else:
            print("Invalid choice!")

    def view_transactions(self):
        transactions = self.manager.conn.execute('''SELECT * FROM transactions''').fetchall()
        for t in transactions:
            print(f"\nID: {t[0]}")
            print(f"Type: {t[1]}")
            print(f"Item ID: {t[2]}")
            print(f"Quantity: {t[3]}")
            print(f"Timestamp: {t[4]}")


if __name__ == "__main__":
    interface = BarInterface()
    interface.show_main_menu()