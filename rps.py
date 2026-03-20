import random
import time
wincount = 0
def main():
    global wincount 
    player = input('pick between rock paper scissors: ')
    if player not in ['rock', 'paper', 'scissors']:
        print('invalid choice, try again')
        main()
        return
    choices = ['rock', 'paper', 'scissors']
    wins = {'rock': 'scissors','paper': 'rock','scissors': 'paper'}
    comps = random.choice(choices)
    time.sleep(1)
    sec = 3
    while sec > 0:
        print(sec)
        time.sleep(1)
        sec -= 1
    print(f'computer picked {comps}')
    if player == comps:
        print('tie')
    elif wins[player] == comps:
        print('you win')
        wincount += 1
    else:
        print('you lose')
    print(f'your win count is {wincount}')
    print('play again? (y/n)')
    if input() == 'y':
        main()
    else:
        print('goodbye')
main()
    