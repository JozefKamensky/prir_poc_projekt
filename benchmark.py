import math
import pandas as pd
from ais import AIS
import numpy.random as npr
import random
import matplotlib.pyplot as plt

colors = [
    '#000000',
    '#55415f',
    '#646964',
    '#d77355',
    '#508cd7',
    '#64b964',
    '#e6c86e',
    '#dcf5ff',
]


def euclidean(a, b):
    return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))


CUSTOMERS = {}
NUM_OF_CUSTOMERS = 25
NUM_OF_VEHICLES = 8
MAX_CAPACITY = 200


def generate_solution():
    customers = list(range(1, NUM_OF_CUSTOMERS + 1))
    while True:
        customer_order = list(npr.permutation(customers))
        used_vehicles = random.randint(1, NUM_OF_VEHICLES)
        # first vehicle needs to be first in array
        customer_order.insert(0, 0)
        used_vehicles -= 1
        possible_indices = list(range(2, len(customer_order)))
        for j in range(0, used_vehicles):
            selected_index = possible_indices[random.randint(0, len(possible_indices) - 1)]
            for index, val in enumerate(possible_indices):
                if val >= selected_index:
                    possible_indices[index] = val + 1
            possible_indices.remove(selected_index + 1)
            customer_order.insert(selected_index, 0)
        if is_solution_viable(customer_order):
            return customer_order


def is_solution_viable(solution):
    total_capacity = 0
    for val in solution:
        if val == 0:
            if total_capacity > MAX_CAPACITY:
                return False
            else:
                total_capacity = 0
        else:
            total_capacity += CUSTOMERS[val]["DEMAND"]
    return True


def calculate_fitness(solution):
    total_distance = 0
    total_penalty = 0

    distance_so_far = 0
    time_so_far = 0
    prev_val = None

    for val in solution:
        if val == 0:
            prev_val = 0
            distance_so_far = 0
        else:
            d = euclidean(
                (CUSTOMERS[prev_val]['X'], CUSTOMERS[prev_val]['Y']),
                (CUSTOMERS[val]['X'], CUSTOMERS[val]['Y']),
            )
            total_distance += d
            distance_so_far += d

            time_so_far += d
            windows_start = CUSTOMERS[val]['WINDOW_START']
            windows_end = CUSTOMERS[val]['WINDOW_END']
            if time_so_far < windows_start:
                total_penalty += windows_start - time_so_far
            elif time_so_far > windows_end:
                total_penalty += time_so_far - windows_end

            prev_val = val
    return total_distance + total_penalty


def mutate_solution(solution):
    s = random.randint(1, len(solution) - 1)
    if s == 1:
        e = 2
    else:
        e = s - 1

    val_s = solution[s]
    val_e = solution[e]

    solution[e] = val_s
    solution[s] = val_e

    return solution


def mutate_solution_2(solution):
    s = random.randint(1, len(solution) - 1)
    e = random.randint(1, len(solution) - 1)

    val_s = solution[s]
    val_e = solution[e]

    solution[e] = val_s
    solution[s] = val_e

    return solution


def mutate_solution_3(solution):
    s = random.randint(1, len(solution) - 1)
    e = random.randint(1, len(solution) - 1)

    if e < s:
        e, s = s, e

    solution[s:e] = npr.permutation(solution[s:e])

    return solution


data = pd.read_csv('./data/r101.csv')
for index, row in data.iterrows():
    CUSTOMERS[int(row[0])] = {
        "X": int(row[1]),
        "Y": int(row[2]),
        "DEMAND": int(row[3]),
        "WINDOW_START": int(row[4]),
        "WINDOW_END": int(row[5]),
        "SERVICE_TIME": int(row[6]),
    }
asf = AIS(generate_solution, calculate_fitness, [mutate_solution, mutate_solution_2, mutate_solution_3], 0.7, 200)
for i in range(0, 100):
    asf.next_generation()

    best = asf.get_best_solution()
    plt.close('all')
    plt.figure(figsize=(10, 10))
    prev = None
    c = -1
    clr = colors[0]
    for val in best:
        if prev is not None:
            x = (CUSTOMERS[prev]['X'], CUSTOMERS[val]['X'])
            y = (CUSTOMERS[prev]['Y'], CUSTOMERS[val]['Y'])
            plt.plot(x, y, marker='o', color=clr)
        if val == 0:
            c += 1
            clr = colors[c]
        prev = val
    plt.savefig('./gif/' + str(i) + '.png', dpi=50)


