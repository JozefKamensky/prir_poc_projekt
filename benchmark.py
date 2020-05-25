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
    '#20B2AA',
    '#FFA07A',
    '#9932CC',
    '#FF1493',
    '#48D1CC',
    '#CD5C5C',
    '#4169E1',
    '#0000CD',
    '#483D8B',
    '#FFA500',
    '#F4A460',
    '#3CB371',
    '#8FBC8F',
    '#ADFF2F',
    '#DAA520',
    '#A0522D',
]


def euclidean(a, b):
    return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))


def distance_of_customers(c1, c2):
    return euclidean(
        (CUSTOMERS[c1]['X'], CUSTOMERS[c1]['Y']),
        (CUSTOMERS[c2]['X'], CUSTOMERS[c2]['Y']),
    )


CUSTOMERS = {}
NUM_OF_CUSTOMERS = 25
NUM_OF_VEHICLES = 25

# change before run
MAX_CAPACITY = 200


def generate_solution():
    customers = list(range(1, NUM_OF_CUSTOMERS + 1))
    while True:
        customer_order = list(npr.permutation(customers))

        possible_solution = []
        c = 1
        i = 0
        for j in range(0, NUM_OF_CUSTOMERS):
            if c == 1:
                possible_solution.append(0)
                c = 0
            c += 1
            possible_solution.append(customer_order[i])
            i += 1

        if is_solution_viable(possible_solution):
            # insert 0 to end to correctly calculate last route with return to depot
            possible_solution.append(0)
            return possible_solution


# called after creation of new solution or mutations - only viable solutions are part of population
def is_solution_viable(solution):
    total_capacity = 0
    time = 0
    prev = None
    for val in solution:
        if prev is None:
            prev = val
            continue

        total_capacity += CUSTOMERS[val]["DEMAND"]
        # time is equal to distance
        time += distance_of_customers(val, prev)
        # van cannot arrive later than customer expects
        if time > CUSTOMERS[val]['WINDOW_END']:
            return False
        # if van arrives before customer time window, it has to wait to start of time window
        if time < CUSTOMERS[val]['WINDOW_START']:
            time = CUSTOMERS[val]['WINDOW_START']
        time += CUSTOMERS[val]['SERVICE_TIME']

        # after each route check capacity constraint and reset counters
        if val == 0:
            if total_capacity > MAX_CAPACITY:
                return False
            total_capacity = 0
            time = 0
        prev = val
    return True


def calculate_fitness(solution):
    total_distance = 0
    time_so_far = 0
    prev_val = None
    number_of_used_vehicles = 0

    for val in solution:
        if prev_val is None:
            prev_val = val
            continue

        d = distance_of_customers(val, prev_val)
        # time is equal to distance
        time_so_far += d
        total_distance += d
        # if van arrives before customer time window, it has to wait to start of time window
        if time_so_far < CUSTOMERS[val]['WINDOW_START']:
            time_so_far = CUSTOMERS[val]['WINDOW_START']
        time_so_far += CUSTOMERS[val]['SERVICE_TIME']

        if val == 0:
            time_so_far = 0
            number_of_used_vehicles += 1
        prev_val = val
    return {
        'distance': total_distance,
        'vehicles': number_of_used_vehicles
    }


def calculate_affinity(fitness):
    return 1/fitness


def mutate_exchange_adjacent(solution):
    s = random.randint(1, len(solution) - 2)
    if s == 1:
        e = 2
    elif s == len(solution) - 2:
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


def mutate_exchange_two_values(solution):
    s = random.randint(1, len(solution) - 2)
    e = random.randint(1, len(solution) - 2)

    val_s = solution[s]
    val_e = solution[e]

    solution[e] = val_s
    solution[s] = val_e

    return solution


def mutate_permutation_range(solution):
    s = random.randint(1, len(solution) - 2)
    e = random.randint(1, len(solution) - 2)

    if e < s:
        e, s = s, e

    solution[s:e] = npr.permutation(solution[s:e])

    return solution


def mutate_reverse_range(solution):
    s = random.randint(1, len(solution) - 2)
    e = random.randint(1, len(solution) - 2)

    if e < s:
        e, s = s, e

    solution[s:e] = solution[s:e][::-1]
    return solution


def mutate_join_two_routes(solution):
    while True:
        index_1 = random.randint(1, len(solution) - 2)
        if solution[index_1] == 0:
            break
    solution.pop(index_1)
    return solution


def mutate_split_route(solution):
    index_1 = random.randint(1, len(solution) - 2)
    solution.insert(index_1, 0)
    return solution


def mutate_move_value(solution):
    s = random.randint(1, len(solution) - 2)
    e = random.randint(1, len(solution) - 2)
    val = solution[s]
    solution.pop(s)
    solution.insert(e, val)
    return solution


random.seed()
data = pd.read_csv('./data/c101_25.csv')
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
ratio_replace_worst = 0
ratio_generate_new = 0
num_of_iterations = 1000
pop_size = 100
ais = AIS(
    generate_solution,
    calculate_fitness,
    calculate_affinity,
    1,
    [mutate_exchange_adjacent, mutate_exchange_two_values, mutate_join_two_routes, mutate_reverse_range, mutate_permutation_range, mutate_move_value],
    ratio_replace_worst,
    ratio_generate_new,
    pop_size,
    is_solution_viable)
for i in range(0, num_of_iterations):
    ais.next_generation()
    best = ais.get_best_solution()

# plot best solution
plt.figure(figsize=(10, 10))
prev = None
c = -1
clr = colors[0]
order = 0
for val in best['path']:
    if prev is not None:
        x = (CUSTOMERS[prev]['X'], CUSTOMERS[val]['X'])
        y = (CUSTOMERS[prev]['Y'], CUSTOMERS[val]['Y'])
        plt.plot(x, y, marker='o', color=clr, lw=2)
        plt.text(CUSTOMERS[val]['X'], CUSTOMERS[val]['Y'] + 0.5, str(order), color=clr)
        order += 1
    if val == 0:
        order = 1
        c += 1
        clr = colors[c]
    prev = val
plt.savefig('solution.png', dpi=50)


