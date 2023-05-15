from flask import Flask, redirect, url_for, request
app = Flask(__name__)

from random import choice

def get_ai_moved_board(board, difficulty):

    picked_moves = []
    potentials = [x for x in range(len(board)) if board[x] == "N"]

    if difficulty < 2:

        random_move = choice(potentials)

        picked_moves.append(random_move)

    if difficulty > 0:
        
        player = ["X","O"][len(board.replace("N", ""))%2]

        t = {}

def assess_board(board, player):

    players = ["X","O"]

    # Recursively generate all possible moves, analyse each one
    # Base case is an end, returns 0 for draws, 1 for wins, -1 for losses
    # Each non-base takes the minimum of the previous ones

    result = check_board(board)

    if result != "None":

        if result == players[player]:

            return 1
        
        if result == "Draw":

            return 0

        return -1

    scores = [None] * 10
    
    for move in [x for x in range(len(board)) if board[x] == "N"]:

        scores[move] = -assess_board(board[:move] + players[player] + \
            board[move+1:], (player+1)%2)
    
    return max([s for s in scores if s is not None])

def check_board(board):

    if board[0] == board[4] == board[8] != "N": # Leading diagonal

        return board[0]
    
    if board[2] == board[4] == board[6] != "N": # Other diagonal

        return board[2]

    for x in range(3):

        if board[x] == board[x+1] == board[x+2] != "N": # Horizontal

            return board[x]

        if board[x] == board[x+3] == board[x+6] != "N": # Vertical

            return board[x]
        
    if len(board.replace("N", "")) == 9:

        return "Draw"
    
    return "None"

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
    Attach ?starto=anything if you wish to start as Os against the ai, default difficulty 0
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

        start_o = "starto" in list(args.keys())


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

@app.route('/playai/<board>')
def continue_ai_game(board):

    return ''''''

@app.route('/playhuman/<board>')
def continue_human_game(board):

    return ''''''


print(assess_board("NNXNNNNNN", 1))