from flask import Flask, render_template, request, redirect, url_for, jsonify
from model.game import Game, session

app = Flask(__name__, template_folder='../templates')


@app.route('/history', methods=['GET'])
def show_history_page():
    games = session.query(Game).order_by(Game.creation_date.desc()).all()
    return render_template('history.html', games=games)


@app.route('/new_game', methods=['POST'])
def start_new_game():
    new_game = Game()
    session.add(new_game)
    session.commit()
    return render_template('new_game.html', game=new_game)


@app.route('/old_game/<int:game_id>', methods=['GET'])
def show_old_game(game_id):
    old_game = session.query(Game).get(game_id)
    return render_template('old_game.html', game=old_game)


@app.route('/delete_game/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    game_to_delete = session.query(Game).get(game_id)
    session.delete(game_to_delete)
    session.commit()
    return redirect(url_for('show_history_page'))


@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('gameId')
    move_index = data.get('moveIndex')

    game = session.query(Game).get(game_id)
    if not game or game.outcome:
        return jsonify({'error': 'Invalid game or game already over'}), 400

    moves = list(game.moves)
    if moves[move_index] == '0':
        current_player = 'X' if moves.count('1') <= moves.count('2') else 'O'
        moves[move_index] = '1' if current_player == 'X' else '2'

        game.moves = ''.join(moves)
        session.commit()

        if check_winner(moves, current_player):
            game.outcome = f'Win for {current_player}'
            session.commit()
            return jsonify({'game_over': True, 'result': f'Win for {current_player}'})

        if '0' not in moves:
            game.outcome = 'Draw'
            session.commit()
            return jsonify({'game_over': True, 'result': 'Draw'})

        return jsonify({'game_over': False}), 200

    return jsonify({'error': 'Cell already taken'}), 400


def check_winner(moves, player):
    if player == 'X':
        player_sign = '1'
    elif player == 'O':
        player_sign = '2'

    i = 0
    if moves[i] == moves[i + 1] == moves[i + 2] == player_sign:
        return True
    i = 3
    if moves[i] == moves[i + 1] == moves[i + 2] == player_sign:
        return True
    i = 6
    if moves[i] == moves[i + 1] == moves[i + 2] == player_sign:
        return True

    for i in range(3):
        if moves[i] == moves[i + 3] == moves[i + 6] == player_sign:
            return True

    if moves[0] == moves[4] == moves[8] == player_sign or moves[2] == moves[4] == moves[6] == player_sign:
        return True

    return False


if __name__ == '__main__':
    app.run(host='0.0.0.0')
