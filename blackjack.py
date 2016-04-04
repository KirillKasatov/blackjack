# -*- coding: utf-8 -*-

import random

from flask import Flask, render_template, session, request, url_for, redirect
from flask.ext.session import Session

import settings

app = Flask(__name__)
app.config.from_object(settings)

Session(app)

weights = (
    ('2', 2), ('3', 3), ('4', 4), ('5', 5),
    ('6', 6), ('7', 7), ('8', 8), ('9', 9),
    ('10', 10), ('J', 10), ('Q', 10), ('K', 10),
    ('T', 11)
)


class Card(object):
    def __init__(self, rank, weight):
        self.rank = rank
        self.weight = weight

    def __unicode__(self):
        return self.rank

    def __int__(self):
        return self.weight

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.rank == other.rank and self.weight == other.weight
        return self == other


class Game(object):
    ACE = Card('T', 11)

    def __init__(self):
        self.deck = [Card(r, w) for r, w in weights * 4]
        self.hand = []
        random.shuffle(self.deck)

    def last_taken(self):
        return self.hand[-1] if self.hand else None

    def take_card(self):
        card = self.deck.pop()

        if sum(self.score()) + card.weight > 21:
            try:
                i = self.hand.index(self.ACE)
                self.hand[i].weight = 1
            except ValueError:
                pass

        self.hand.append(card)

    def score(self):
        return [int(i) for i in self.hand]

    def total(self):
        return sum(self.score())

    def status(self):
        total = self.total()
        if total > 21:
            return 'lose'
        elif total == 21:
            return 'win'
        # elif dealers_total
        return 'unknown'

    @classmethod
    def current(cls):
        session['game'] = session.get('game', cls())
        return session['game']

    @classmethod
    def refresh(cls):
        session.pop('game', None)


@app.route('/', methods=['GET', 'POST'])
def index():
    Game.refresh()
    return render_template('index.html')


@app.route('/game/', methods=['GET', 'POST'])
def game():

    if 'new' in request.args:
        Game.refresh()
        return redirect(url_for('game'))

    current_game = Game.current()
    if request.method == 'POST':
        current_game.take_card()
        return redirect(url_for('game'))
    return render_template('game.html', game=current_game)

if __name__ == '__main__':
    app.run(debug=True)
