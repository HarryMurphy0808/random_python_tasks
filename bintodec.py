num = ""
while num != "exit":
    num = input("Enter a binary number (or 'exit' to quit): ")
    if num == "exit":
        print("Exiting the program.")
        break
    try:
        decimal_num = int(num, 2)
        print(f"The decimal equivalent of {num} is {decimal_num}.")
    except ValueError:
        print("Invalid binary number. Please try again.")
