import random
import numpy as np
import pandas as pd

with open('valid_solutions.csv') as f:
    valid_solutions = f.read().splitlines()[1:-1]


class GuesserInterface:
    def generate_guess(self, valid_sols):
        pass


class RandomGuesser(GuesserInterface):
    def generate_guess(self, valid_sols):
        return random.choice(valid_sols)


class Game:

    def __init__(self, word, valid_sols, strategy, debug=False):
        self.word = word
        self.strategy = strategy
        self.debug = debug
        self.valid_sols = valid_sols

    def play_game(self):
        guess_num = 1
        while guess_num != 7:
            guess = self.strategy.generate_guess(self.valid_sols)
            if self.debug:
                print("after guess %s remaining solutions %s guessing now %s" % (guess_num, len(self.valid_sols), guess))
            self.valid_sols = filter_remaining(self.word, guess, self.valid_sols)
            if len(self.valid_sols) == 0:
                if self.debug:
                    print("guessed %s after %s guesses" % (self.word, guess_num))
                return guess_num
            guess_num += 1
        return -1


def get_first_word_statistics(valid_sols, fname, strategy='random'):
    df = pd.DataFrame(columns=['word', 'average', 'success_rate'])
    i = 0
    for word in valid_sols:
        i += 1
        if i % 100 == 0:
            print(i)
        average, success_rate = get_statistics(valid_sols, first_word=word, max_elements=5)
        df.loc[len(df)] = pd.Series({"word": word, "average": average, "success_rate": success_rate})
    df.to_csv(fname)


def getGuesser(strategy):
    if strategy == 'random':
        return RandomGuesser()
    else:
        raise Exception("invalid strategy %s", strategy)


def get_statistics(valid_sols, first_word='', max_elements=-1, debug=False, strategy='random', word_dist_fname='', num_iterations=1):
    total_successes = 0
    dist = [0, 0, 0, 0, 0, 0]
    i = 0
    num_tries = 0
    word_distribution = {}
    words_to_iter = valid_sols if max_elements == -1 else random.sample(valid_sols, max_elements)
    for word in words_to_iter*num_iterations:
        if word not in word_distribution:
            word_distribution[word] = 0
        game = Game(word, valid_sols, getGuesser(strategy), debug)
        guess_num = game.play_game()
        if guess_num != -1:
            total_successes += 1
            dist[guess_num - 1] += 1
            word_distribution[word] += 1
        i += 1
        num_tries += 1
        if i % 100 == 0:
            print(i)

    # print("distribution is %s" % dist)
    success_rate = total_successes / num_tries
    average = np.sum([dist[i] * (i + 1) for i in range(0, 6)]) / num_tries
    # print("average for strategy %s is %s with success_rate of %s" % (strategy, average, success_rate))
    if word_dist_fname != '':
        sorted_words = {k: v for k, v in sorted(word_distribution.items(), key=lambda item: item[1], reverse=True)}
        df = pd.DataFrame.from_dict(sorted_words, orient='index')
        df.to_csv(word_dist_fname)
    return average, success_rate


# def simulate_game(sol, remaining, first_word, strategy='random', debug=False):
#     guess_num = 1
#     while guess_num != 7:
#         guess = generate_guess(remaining, strategy)
#         if debug:
#             print("after guess %s remaining solutions %s guessing now %s" % (guess_num, len(remaining), guess))
#         remaining = filter_remaining(sol, guess, remaining)
#         if len(remaining) == 0:
#             if debug:
#                 print("guessed %s after %s guesses" % (sol, guess_num))
#             return guess_num
#         guess_num += 1
#     # print("failed to guess %s" % sol)
#     return -1


# def generate_guess(remaining, strategy):
#     if strategy == 'random':
#         return
#     else:
#         print("invalid strategy")


def filter_remaining(sol, guess, remaining):
    if sol == guess:
        return []
    eval = get_eval(sol, guess)
    new_remaining = []
    for word in remaining:
        if get_eval(word, guess) == eval:
            new_remaining.append(word)
    return new_remaining


def get_eval(sol, guess):
    res = [-1, -1, -1, -1, -1]
    # first fill in greens
    temp_sol = ''
    temp_guess = ''
    for i in range(0, 5):
        if guess[i] == sol[i]:
            res[i] = 1
            temp_guess += '$'
            temp_sol += '$'  # will be needed for yellow calculation
        else:
            temp_sol += sol[i]
            temp_guess += guess[i]

    # now fill in yellows, needed to do separately to take into account duplicates
    for i in range(0, 5):
        if temp_guess[i] != '$':
            if temp_guess[i] in temp_sol and temp_sol.count(temp_guess[i]) > temp_guess[0:i].count(temp_guess[i]):
                res[i] = 0
    return res


game = Game('slate', valid_solutions, RandomGuesser(), True)
print(game.play_game())

# get the distribution for random guess
# print(get_statistics(valid_solutions, strategy='random', num_iterations=5)) # (3.9522039757994816, 0.9815038893690579)

# get the random guess distribution
# print(get_statistics(valid_solutions*5, strategy='random', word_dist_fname='word_success_rate_random.csv', num_iterations=10))

# get_first_word_statistics(valid_solutions, "random_first_word_stats.csv")
