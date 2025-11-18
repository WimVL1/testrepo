import random
import csv

class Batch:
    """
    Representeert een enkele batch van een product in de voorraad.
    Elke batch heeft een bepaalde hoeveelheid en een inkoopprijs per eenheid.
    """
    def __init__(self, quantity, cost_per_unit):
        """
        Initialiseert een Batch-object.
        :param quantity: De hoeveelheid producten in deze batch.
        :param cost_per_unit: De inkoopkosten per product in deze batch.
        """
        self.quantity = quantity
        self.cost_per_unit = cost_per_unit

    def __str__(self):
        return f"Batch(quantity={self.quantity}, cost_per_unit={self.cost_per_unit})"

class Product:
    """
    Representeert een product, inclusief de voorraad die wordt beheerd als een stack van batches.
    Past het LIFO (Last-In-First-Out) principe toe.
    """
    def __init__(self, product_name, holding_cost, stockout_penalty):
        self.product_name = product_name
        self.holding_cost = holding_cost
        self.stockout_penalty = stockout_penalty
        self.batches = []

    def add_batch(self, quantity, cost_per_unit):
        new_batch = Batch(quantity, cost_per_unit)
        self.batches.append(new_batch)

    def fulfill_demand(self, demand):
        fulfilled = 0
        while fulfilled < demand and self.batches:
            last_batch = self.batches[-1]
            if last_batch.quantity >= (demand - fulfilled):
                last_batch.quantity -= (demand - fulfilled)
                fulfilled = demand
                if last_batch.quantity == 0:
                    self.batches.pop()
            else:
                fulfilled += last_batch.quantity
                self.batches.pop()
        if fulfilled < demand:
            unfulfilled_amount = demand - fulfilled
            return unfulfilled_amount * self.stockout_penalty
        return 0

    def calculate_holding_cost(self):
        total_holding_cost = 0
        for batch in self.batches:
            total_holding_cost += batch.quantity * self.holding_cost
        return total_holding_cost

    def __str__(self):
        product_info = f"Product {self.product_name}:\n"
        if not self.batches:
            product_info += "  No batches in stock.\n"
        else:
            for batch in reversed(self.batches):
                product_info += f"  {batch}\n"
        return product_info

class InventoryManager:
    """
    Beheert de volledige voorraad voor meerdere producten.
    """
    def __init__(self):
        self.products = {}

    def add_product(self, product_name, holding_cost, stockout_penalty):
        if product_name in self.products:
            print(f"Product {product_name} already exists.")
        else:
            self.products[product_name] = Product(product_name, holding_cost, stockout_penalty)
            print(f"Product {product_name} added.")

    def restock_product(self, product_name, quantity, cost_per_unit):
        if product_name not in self.products:
            print(f"Product {product_name} not found")
        else:
            self.products[product_name].add_batch(quantity, cost_per_unit)
            print(f"Restocked {product_name} with {quantity} units.")

    def simulate_demand(self, min_demand=0, max_demand=20):
        demand_dict = {}
        for product_name in self.products:
            demand = random.randint(min_demand, max_demand)
            demand_dict[product_name] = demand
        return demand_dict

    def simulate_day(self, demand):
        total_holding_costs = 0
        total_stockout_costs = 0
        for product in self.products.values():
            total_holding_costs += product.calculate_holding_cost()
        for product_name, demand_amount in demand.items():
            if product_name in self.products:
                stockout_cost = self.products[product_name].fulfill_demand(demand_amount)
                total_stockout_costs += stockout_cost
        return total_holding_costs, total_stockout_costs

    def save_to_csv(self, filename):
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['product_name', 'batch_quantity', 'batch_cost_per_unit'])
                for product in self.products.values():
                    for batch in product.batches:
                        writer.writerow([product.product_name, batch.quantity, batch.cost_per_unit])
            print(f"Inventory successfully saved to {filename}")
        except IOError:
            print(f"Error: Could not write to file {filename}")

    def load_from_csv(self, filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    product_name, quantity, cost_per_unit = row
                    if product_name in self.products:
                        self.products[product_name].add_batch(int(quantity), float(cost_per_unit))
                    else:
                        print(f"Warning: Product '{product_name}' not found in manager. Batch from CSV not loaded.")
            print(f"Inventory successfully loaded from {filename}")
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except Exception as e:
            print(f"An error occurred while reading {filename}: {e}")

    def print_inventory(self):
        print("Current Inventory:")
        print("--------------------")
        if not self.products:
            print("Inventory is empty.")
        else:
            for product in self.products.values():
                print(product)
        print("--------------------")

def main():
    manager = InventoryManager()
    manager.add_product(product_name="Laptop", holding_cost=0.5, stockout_penalty=50)
    manager.add_product(product_name="Smartphone", holding_cost=0.2, stockout_penalty=30)
    print("\n")
    manager.restock_product("Laptop", 10, 800.0)
    manager.restock_product("Laptop", 15, 820.0)
    manager.restock_product("Smartphone", 30, 450.0)
    manager.restock_product("Smartphone", 25, 460.0)
    print("\n")
    manager.print_inventory()
    daily_demand = manager.simulate_demand(min_demand=10, max_demand=25)
    print(f"Simulated Demand: {daily_demand}\n")
    holding_costs, stockout_costs = manager.simulate_day(daily_demand)
    print(f"Total Holding Costs for the day: {holding_costs:.2f}")
    print(f"Total Stockout Costs for the day: {stockout_costs:.2f}\n")
    print("Inventory after fulfilling demand:")
    manager.print_inventory()
    manager.save_to_csv("inventory_status.csv")

if __name__ == "__main__":
    main()