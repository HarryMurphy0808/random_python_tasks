import random 
rng = random.randint(0,100)
count = 0
guess = 0
while guess != 45:
    count = count+1
    guess = int(input('guess the number'))
    if guess < 45:
        print('guess is lower')
    elif guess > 45:
        print('guess is higher')

