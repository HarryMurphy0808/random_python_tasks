import time 
num = int(input("Enter a number: "))
while num > 0:
    print(num)
    num -= 1
    time.sleep(1)
    if num%2 == 0:
        print("Even")
    else:
        print("Odd")
