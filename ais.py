import random
import copy


def pick_n_by_roulette(n, pick_from):
    picked = []
    for i in range(0, n):
        t = 0
        r = random.random()
        for solution in pick_from:
            t += solution['pick_chance']
            if r <= t:
                picked.append(solution)
                break
    return picked


def calc_pick_chances(solutions):
    total_affinity = 0
    for solution in solutions:
        total_affinity += solution['affinity']
    for solution in solutions:
        solution['pick_chance'] = solution['affinity'] / total_affinity


def clone_solution(solutions):
    solution = pick_n_by_roulette(1, solutions)[0]
    return copy.deepcopy(solution['path'])


def remove_repeating_zeros(solution):
    edited_solution = [0]
    for val in solution:
        if val == 0 and edited_solution[-1] == 0:
            continue
        else:
            edited_solution.append(val)
    return edited_solution


class AIS:
    def __init__(self, generate_antibody, calculate_fitness, calculate_affinity, mutation_chance, mutations,
                 replace_ratio, newcomer_ratio, population_size, is_viable):
        self.replace_ratio = replace_ratio
        self.newcomer_ratio = newcomer_ratio
        self.population_size = population_size
        self.num_of_solutions_to_generate = int(self.population_size * self.newcomer_ratio)
        self.num_of_worst_solutions_to_discard = int(self.population_size * self.replace_ratio)
        self.generate_antibody = generate_antibody
        self.calculate_fitness = calculate_fitness
        self.calculate_affinity = calculate_affinity
        self.mutations = mutations
        self.mutation_chance = mutation_chance
        self.minimal_num_of_diffs = 2
        self.is_viable = is_viable

        self.num_of_generation = 0
        self.current_population = []
        self.next_population = []
        self.best_solution = {
            'distance': 100000
        }
        for i in range(0, population_size):
            self.current_population.append(generate_antibody())

    def evaluate_solutions(self, paths):
        evaluated_solutions = []

        for path in paths:
            f = self.calculate_fitness(path)
            a = self.calculate_affinity(f['distance'])
            solution = {
                'affinity': a,
                'distance': f['distance'],
                'vehicles': f['vehicles'],
                'path': path
            }
            evaluated_solutions.append(solution)
        evaluated_solutions.sort(key=lambda x: x['affinity'], reverse=True)
        return evaluated_solutions

    def mutate_solution(self, solution):
        if random.random() < self.mutation_chance:
            s = self.mutations[random.randint(0, len(self.mutations) - 1)](solution)
        else:
            s = solution
        return remove_repeating_zeros(s)

    def is_solution_similar_to_another(self, solution, solutions):
        for s in solutions:
            num_of_diffs = 0
            if len(s) != len(solution):
                continue
            for i in range(0, len(s)):
                if s[i] != solution[i]:
                    num_of_diffs += 1
            if num_of_diffs < self.minimal_num_of_diffs:
                return True
        return False

    def next_generation(self):
        self.num_of_generation += 1

        evaluated_solutions = self.evaluate_solutions(self.current_population)
        calc_pick_chances(evaluated_solutions)

        if evaluated_solutions[0]['distance'] < self.best_solution['distance']:
            self.best_solution = evaluated_solutions[0]
        print(self.best_solution)

        cloned_solutions = []
        while len(cloned_solutions) < self.population_size:
            cloned_solution = clone_solution(evaluated_solutions)
            mutated_solution = self.mutate_solution(cloned_solution)
            if self.is_viable(mutated_solution):
                cloned_solutions.append(mutated_solution)
        evaluated_cloned_solutions = self.evaluate_solutions(cloned_solutions)

        next_population = []
        for i in range(0, self.num_of_solutions_to_generate):
            next_population.append(self.generate_antibody())

        for i in range(0, self.num_of_worst_solutions_to_discard):
            evaluated_solutions.pop()

        solution_pool = evaluated_solutions + evaluated_cloned_solutions
        calc_pick_chances(solution_pool)
        free_slots = self.population_size - self.num_of_solutions_to_generate

        picked = []
        while free_slots > 0:
            possible_solution = pick_n_by_roulette(1, solution_pool)[0]['path']
            if not self.is_solution_similar_to_another(possible_solution, picked):
                picked.append(possible_solution)
                free_slots -= 1

        next_population += list(picked)
        self.current_population = next_population

    def get_best_solution(self):
        return self.best_solution
