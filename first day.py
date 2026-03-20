name = input("What is your name? ")
print(f"Hello, {name}!")

def print_recipt(items):
    print("Receipt:")
    for item, price in items.items():
        print(f"{item}: ${price:.2f}")
    total = sum(items.values()) + 0.15 * sum(items.values()) 
    print(f"Total: ${total:.2f}")
items = {
    "Apple": 0.99,
    "Bread": 2.50,
    "Milk": 1.99
}
print_recipt(items)
