import pandas as pd
import random

# use this UDF to handle yes/no queries
# (we only need it twice but still worth it)

# "prompt" will be a fully written question, the UDF will add a new line before it
def yesno(prompt):
    validity = False
    while validity == False:
        print('\n' + prompt + ' (Y/N)')
        response = input('> ')
        if response.upper() not in ['Y','N']:
            print('\nThat is not a valid input. Please enter "Y" or "N".')
        else:
            validity = True
    return response.upper()

# This UDF is the meat and potatoes of our prediction model, the CPU's turn!
def predict(boardstate,turn,targvar):

    # "state_col" is the column label for the previous turn's boardstate as in the game logs
    state_col = 'Boardstate_' + str(turn - 1)
    # "moves_col" is the column label for the moves chosen at this turn from previous games
    moves_col = 'Turn_' + str(turn)

    # "state_count" is the number of times this boardstate appears in the game logs
    state_count = len(df[df[state_col] == boardstate])

    # What if this has never happened in the database?
    if state_count == 0:
        #!!!!! CODE THIS TO RETURN A NONE VALUE
        print('Interesting. I\'ve never seen this board state before.')
        return 'new'

    # If there is a move the CPU has not tried, it is curious to see what happens.
    else:

        # "choices" are all the moves the CPU has previously tried at this board state.
        choices = df[df[state_col] == boardstate][moves_col].unique().tolist()
        # "choices_len" is the count of "choices".
        choices_len = len(choices)

        if (turn + choices_len) < 10:
            print('Curious. I think I\'ll try something new here.')
            return choices
        else:

            # "df_opts" is a dataframe that shows each available move for the current boardstate, ranked by mean
            # NOTE: "mean" = (X wins - O wins)/games
            df_opts = df[df[state_col] == boardstate].groupby(moves_col).mean()

            # Best moves for X -> 1, best moves for O -> -1
            if targvar == 1:
                targ_odds = df_opts['Winner'].max()
            else:
                targ_odds = df_opts['Winner'].min()

            # Choose the set of moves with the highest win-loss ratio
            move_opts = df_opts[df_opts['Winner'] == targ_odds].index.to_list()

            # Choose a move at random from the options. Very easy if only one move
            move = random.choice(move_opts)

            print(f'\nI shall play to square {move}.')

            # calculate odds based on database
            win_odds = len(df[(df[state_col] == boardstate) & (df[moves_col] == move) & (
                df['Winner'] == targvar)]) * 100 / len(df[(df[state_col] == boardstate) & (
                df[moves_col] == move)])

            print(f'Based on my experience, my chances of winning are %.1f%%.' % (win_odds))
            return move

print('\nLet\'s play Tic-Tac-Toe!')

# Load the games database (change ths when not using simulator)
df = pd.read_csv('game_data.csv')

replay = 'Y'

targvar = yesno('Would you like to go first in the first game?')

# If the player wants to go first, the CPU wants O to win, represented by -1 in the data
# Otherwise, the CPU is trying to win for X, which is represented by 1
if targvar == 'Y':
    targvar = -1
else:
    targvar = 1

# Let's have some fun and make this thing a little self-aware
exp = len(df.index)
if exp < 100:
    print('\nI have almost no experience with this game. I hope that\'s okay with you.')
elif exp < 1000:
    print('\nI\'m still learning tic-tac-toe strategy, but I\'ll do my best!')
elif exp < 10000:
    print('\nI\'m not the best player, but I know my way around a board. Let\'s have a good game!')
elif exp < 100000:
    print('\nGood luck to you! I\'m pretty confident that I won\'t lose!')
else:
    print('\nI have to warn you, I\'ve played way too much of this game. I don\'t think you can outfox me!')

# VERY IMPORTANT to associate "targvar = -1" with player going first

###########################
##### BEGIN GAME LOOP #####
###########################

while replay == 'Y':

    # Use a string as a visual representation of the board

    # Visual reference:
    # A1 | A2 | A3
    # ------------
    # B1 | B2 | B3
    # ------------
    # C1 | C2 | C3

#    gameboard = '   1   2   3 \n |-----------\nA|   |   |   \n |-----------\nB|   |   |   \n |-----------\nC|   |   |   '
    gameboard = '   1   2   3 \n             \nA    |   |   \n  -----------\nB    |   |   \n  -----------\nC    |   |   '
    # Well, this looks like shit
    # But I couldn't figure out how to put gridlines on a dataframe
    # Map the coordinates to the positions on the board with a dictionary
    gamedict = {
        'A1': 31, 'A2': 35, 'A3': 39,
        'B1': 59, 'B2': 63, 'B3': 67,
        'C1': 87, 'C2': 91, 'C3': 95
        }

    # Establish available moves and win conditions
    moves = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
    Ax = Bx = Cx = x1 = x2 = x3 = FS = BS = 0

    # create game log and board state
    gamelog = []
    boardstate = '---|---|---'

    # append initial board state to game log
    gamelog.append(boardstate)

    # Draw by default
    winner = 0

    # establish turn order
    turn = 1

    while turn < 10:

        # If the player goes first (targvar = -1), the player plays on odd turns
        if (targvar == -1 and turn % 2 == 1) or (targvar == 1 and turn % 2 == 0):
            # Force the player to enter the coordinates of an available position
            move = False
            print('\nYour turn!')
            print('Here is the board:')
            print('\n' + gameboard)
            while move not in moves:
                print('\nPlease type the coordinates of your move, letter first.')
                move = input('> ').upper()
                if move not in moves:
                    print('\nThat is not a valid move.')

        else:
            move = predict(boardstate, turn, targvar)
            if type(move) is list:
                moves_lim = moves.copy()
                for item in move:
                    moves_lim.remove(item)
                move = random.choice(moves_lim)
                print(f'I shall play to square {move}.')
            elif move == 'new':
                move = random.choice(moves)
                print(f'I think I shall try square {move}.')

        # Append the move to the game log and remove the move from the list
        gamelog.append(move)
        moves.remove(move)

        # Map the position within "boardstate" of the move.
        move_pos = int(move[1]) - 1
        if move[0] == 'B':
            move_pos += 4
        elif move[0] == 'C':
            move_pos += 8

        # "X" wins when a row, column, diagonal reaches a value of 3.
        # "X" plays on odd turns, so turn / 2 has a remainder of 1.
        if turn % 2 == 1:
            win_incr = 1
            boardstate = boardstate[:move_pos] + 'X' + boardstate[move_pos + 1:]
            gameboard = gameboard[:gamedict[move]] + 'X' + gameboard[gamedict[move] + 1:]

        # "O" wins when a row, column, diagonal reaches a value of -3.
        else:
            win_incr = -1
            boardstate = boardstate[:move_pos] + 'O' + boardstate[move_pos + 1:]
            gameboard = gameboard[:gamedict[move]] + 'O' + gameboard[gamedict[move] + 1:]

        # Add board state to game log.
        gamelog.append(boardstate)

        # Increase by 1 or -1 accordingly.
        if move in ['A1', 'A2', 'A3']:
            Ax += win_incr
        if move in ['B1', 'B2', 'B3']:
            Bx += win_incr
        if move in ['C1', 'C2', 'C3']:
            Cx += win_incr
        if move in ['A1', 'B1', 'C1']:
            x1 += win_incr
        if move in ['A2', 'B2', 'C2']:
            x2 += win_incr
        if move in ['A3', 'B3', 'C3']:
            x3 += win_incr
        if move in ['A1', 'B2', 'C3']:
            FS += win_incr
        if move in ['A3', 'B2', 'C1']:
            BS += win_incr
            # Foreslash and backslash for the diagonals. Me so clever.

        # Check for a win for each side.
        if (Ax == 3 or Bx == 3 or Cx == 3 or
            x1 == 3 or x2 == 3 or x3 == 3 or FS == 3 or BS == 3
            ):
            winner = 1
            break
        elif (Ax == -3 or Bx == -3 or Cx == -3 or
            x1 == -3 or x2 == -3 or x3 == -3 or FS == -3 or BS == -3
            ):
            winner = -1
            break

        # Go to next turn
        turn += 1

    # Report the game results
    if winner == targvar:
        print('\nI win! Better luck next time!')
    elif winner == targvar * -1:
        print('\nYou win! Congratulations!')
    else:
        print('\nIt\'s a draw!')
    print('Final board:')
    print('\n' + gameboard)

    # Add the winner to the first position of the game log
    # (since games can be of varying lengths, this is consistent)
    gamelog.insert(0, winner)

    # Add game to data file
    with open('game_data.csv', 'a') as f:
        f.write(','.join(map(str, gamelog)))
        f.write('\n')
        f.close()

    # Offer another game
    if targvar == 1:
        player1 = 'You'
    else:
        player1 = 'I'
    replay = yesno(f'Play again? {player1}\'ll go first next time.')

    # Update the dataframe with new game data
    if replay == 'Y':
        print('\nGreat! Just give me a moment to think about how that last game played out...')
        df = pd.read_csv('game_data.csv')
        print('Done! Ready for another round!')


    # Switch who is X and who is O
    targvar *= -1

print('\nThanks for playing! Let\'s play again sometime!\n')
