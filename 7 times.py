correctpassword = 'yes'
maxattempts = 3
attempts = 0
while attempts < maxattempts:
    password = input("Enter the password: ")
    if password == correctpassword:
        print("Access granted.")
        break
    else:
        attempts += 1
        print(f"Incorrect password. {maxattempts - attempts} attempts remaining.")
        if attempts == maxattempts:
            print("Access denied. Too many incorrect attempts.")

