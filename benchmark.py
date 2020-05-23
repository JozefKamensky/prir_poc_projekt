import math
import pandas as pd
from ais import AIS
import numpy.random as npr
import random
import matplotlib.pyplot as plt

colors = [
    '#000000',
    '#FF0000',
    '#00FF00',
    '#0000FF',
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
        # used_vehicles = random.randint(1, NUM_OF_VEHICLES)
        used_vehicles = NUM_OF_VEHICLES
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
            time_so_far = 0
        else:
            try:
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
                time_so_far += CUSTOMERS[val]['SERVICE_TIME']
            except KeyError:
                print(solution)
            prev_val = val
    return {
        'distance': total_distance,
        'time_penalty': total_penalty,
        # 'fitness': total_distance
        'fitness': total_distance + total_penalty
    }


def calculate_affinity(fitness):
    return 15000 - fitness


def mutate_solution(solution):
    s = random.randint(1, len(solution) - 1)
    if s == 1:
        e = 2
    elif s == len(solution) - 1:
        e = s - 1
    else:
        r = random.random()
        if r < 0.5:
            e = s - 1
        else:
            e = s + 1

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


def mutate_solution_4(solution):
    s = random.randint(1, len(solution) - 1)
    e = random.randint(1, len(solution) - 1)

    if e < s:
        e, s = s, e

    solution[s:e] = solution[s:e][::-1]
    return solution


random.seed()
data = pd.read_csv('./data/r101.csv')
plt.figure(figsize=(10, 10))
for index, row in data.iterrows():
    x = int(row[1])
    y = int(row[2])
    CUSTOMERS[int(row[0])] = {
        "X": x,
        "Y": int(row[2]),
        "DEMAND": int(row[3]),
        "WINDOW_START": int(row[4]),
        "WINDOW_END": int(row[5]),
        "SERVICE_TIME": int(row[6]),
    }
    plt.plot(x, y, marker='o')
    plt.text(x, y + 0.5, str(int(row[4])) + ' - ' + str(int(row[5])))
plt.savefig('./problem.png', dpi=50)

asf = AIS(generate_solution, calculate_fitness, calculate_affinity, 1, [mutate_solution_2, mutate_solution_4], 0.05, 0.1, 0.2, 100)
for i in range(0, 400):
    asf.next_generation()

    best = asf.get_best_solution()
plt.close('all')
plt.figure(figsize=(10, 10))
prev = None
c = -1
clr = colors[0]
order = 0
for val in best['path']:
    if prev is not None:
        x = (CUSTOMERS[prev]['X'], CUSTOMERS[val]['X'])
        y = (CUSTOMERS[prev]['Y'], CUSTOMERS[val]['Y'])
        plt.plot(x, y, marker='o', color=clr)
        plt.text(CUSTOMERS[val]['X'], CUSTOMERS[val]['Y'] + 0.5, str(order), color=clr)
        order += 1
    if val == 0:
        order = 0
        c += 1
        clr = colors[c]
    prev = val
plt.savefig('./gif/' + str(i) + '.png', dpi=50)
t = 0
out_f = open('best.txt', 'w')
prev = None
for val in best['path']:
    if prev is not None:
        t += euclidean(
            (CUSTOMERS[prev]['X'], CUSTOMERS[prev]['Y']),
            (CUSTOMERS[val]['X'], CUSTOMERS[val]['Y']),
        ) + CUSTOMERS[prev]['SERVICE_TIME']
        out_f.write('time: ' + str(t) + ', ' + str(CUSTOMERS[val]['WINDOW_START']) + ' - ' + str(
            CUSTOMERS[val]['WINDOW_END']) + '\n')
    if val == 0:
        t = 0
    prev = val
out_f.close()
out_f = open('runs.txt', 'a')
out_f.write(str(best) + '\n')



