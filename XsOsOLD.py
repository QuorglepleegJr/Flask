from flask import Flask, redirect, url_for, request
app = Flask(__name__)

from random import choice

def check_board(board):

    if board[0] == board[4] and board[4] == board[8] and board[0] != "N": # Leading diagonal

        return board[0]
    
    if board[2] == board[4] and board[4] == board[6] and board[2] != "N": # Other diagonal

        return board[2]

    for x in range(3):

        if board[3*x] == board[3*x+1] and board[3*x+1] == board[3*x+2] and board[3*x] != "N": # Horizontal

            return board[x]

        if board[x] == board[x+3] and board[x+3] == board[x+6] and board[x] != "N": # Vertical

            return board[x]
        
    if len(board.replace("N", "")) == 9:

        return "Draw"
    
    return "None"

def assess_board(board, player, lookup_table=None):

    global out

    players = ["X","O"]

    if lookup_table is None:

        lookup_table = {}

    # Recursively generate all possible moves, analyse each one
    # Base case is an end, returns 0 for draws, 1 for wins, -1 for losses
    # Each non-base takes the minimum of the previous ones

    result = check_board(board)

    if result != "None":

        if result == players[player]:
            
            lookup_table[board] = 1
            return 1, lookup_table
        
        if result == "Draw":

            lookup_table[board] = 0
            return 0, lookup_table

        lookup_table[board] = -1
        return -1, lookup_table

    scores = [None] * 9
    
    for move in [x for x in range(len(board)) if board[x] == "N"]:

        if board[:move] + players[player] + board[move+1:] in lookup_table:

            scores[move] = lookup_table[board[:move] + \
                players[player] + board[move+1:]]
        
        else:

            scores[move], lookup_table = assess_board(board[:move] + players[player] + \
                board[move+1:], (player+1)%2, lookup_table)

        scores[move] *= -1
    
    score = max([s for s in scores if s is not None])
    lookup_table[board] = score

    return score, lookup_table

def get_ai_moved_board(board, difficulty):

    if check_board(board) != "None":

        return board

    picked_moves = []
    potentials = [x for x in range(len(board)) if board[x] == "N"]
    player = len(board.replace("N", ""))%2

    if int(difficulty) < 2:

        picked_moves.append(choice(potentials))

    if int(difficulty) > 0:

        scores = [None] * 9

        for move in potentials:

            print(potentials, move, scores, board, player)

            scores[move] = assess_board(board[:move] + ["X","O"][player] + \
                board[move+1:], (player+1)%2)[0]

            scores[move] *= -1

            print(move, scores[move])

        high = max([x for x in scores if x is not None])

        print(high, [x for x in scores if x == high])

        picked_moves.append(choice([x for x in range(9) if scores[x] == high]))

    move = choice(picked_moves)

    print(picked_moves)

    print(move, ["X","O"][player])

    return board[:move] + ["X","O"][player] + board[move+1:]

def display_board(board, win_check=True):

    html = f'''
    <p style="font-family:'Courier'">{board[0]} | {board[1]} | {board[2]}<br>
    --+---+-- <br>
    {board[3]} | {board[4]} | {board[5]}<br>
    --+---+-- <br>
    {board[6]} | {board[7]} | {board[8]}</p>
    '''

    if win_check:

        win = check_board(board)

        if win != "None":

            html = f"<h1>Winner: {win}!</h1>" + html
        
        else:

            next_to_play = ["X","O"][len(board.replace("N", ""))%2]

            html += f"<p>Next: {next_to_play}</p>"

    return html


@app.route('/')
def home():

    return f'''
    <h1>Naughts and Crosses</h1>
    <p>Go to /new to begin <br>
    Attach ?ai=diff to /new to set play against ai's difficulty, 0 is easiest, 2 is hardest <br>
    Attach ?starto=anything if you wish to start as Os against the ai. Does nothing on 2p <br>
    Attach ?move=num to a preexisting game to add your symbol in position num, given by:
    {display_board("012345678", False)} <br>
    N means no symbol is there yet</p>
    '''

@app.route('/new')
def new_game():

    args = request.args

    try:

        ai = args["ai"]
    
    except KeyError:

        return redirect(url_for('continue_2pgame', board="NNNNNNNNN"))
    
    else:

        if "starto" in list(args.keys()):

            return redirect(url_for('continue_ai_game', board = "NNNNNNNNN", difficulty = ai))

        return redirect(url_for('continue_human_game', board = "NNNNNNNNN", difficulty = ai))


@app.route('/play/<board>')
def continue_2pgame(board):

    try:

        move = request.args["move"]

        if move in ["0","1","2","3","4","5","6","7","8"]:

            move = int(move)

            if board[move] == "N":

                board = board[:move] + \
                    ["X","O"][len(board.replace("N", ""))%2] + board[move+1:]

                return redirect(url_for('continue_2pgame', board = board))
        
        return "<h1>Invalid Move</h1>" + display_board(board)

    except KeyError:

        return display_board(board)

@app.route('/playai/<difficulty>/<board>')
def continue_ai_game(board, difficulty):

    return redirect(url_for('continue_human_game', board=get_ai_moved_board(board, difficulty), difficulty=difficulty))

@app.route('/playhuman/<difficulty>/<board>')
def continue_human_game(board, difficulty):

    try:

        move = request.args["move"]

        if move in ["0","1","2","3","4","5","6","7","8"]:

            move = int(move)

            if board[move] == "N":

                board = board[:move] + \
                    ["X","O"][len(board.replace("N", ""))%2] + board[move+1:]

                return redirect(url_for('continue_ai_game', board = board, difficulty = difficulty))
        
        return "<h1>Invalid Move</h1>" + display_board(board)

    except KeyError:

        return display_board(board)