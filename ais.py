import random
import copy


class AIS:
    def __init__(self, generate_antibody, calculate_fitness, calculate_affinity, mutation_chance, mutations,
                 best_ratio, replace_ratio, newcomer_ratio, population_size):
        self.best_ratio = best_ratio
        self.replace_ratio = replace_ratio
        self.newcomer_ratio = newcomer_ratio
        self.population_size = population_size
        self.num_of_best_solutions_to_keep = int(self.population_size * self.best_ratio)
        self.num_of_solutions_to_generate = int(self.population_size * self.newcomer_ratio)
        self.num_of_worst_solutions_to_discard = int(self.population_size * self.replace_ratio)
        self.generate_antibody = generate_antibody
        self.calculate_fitness = calculate_fitness
        self.calculate_affinity = calculate_affinity
        self.mutations = mutations
        self.mutation_chance = mutation_chance
        self.minimal_num_of_diffs = 2

        self.out_file = open('log.txt', 'w')
        self.log_columns = ['fitness', 'pick_chance', 'mutation_chance']

        self.num_of_generation = 0
        self.current_population = []
        self.next_population = []
        self.best_solution = []
        for i in range(0, population_size):
            self.current_population.append(generate_antibody())

    def evaluate_solutions(self, paths):
        evaluated_solutions = []

        for path in paths:
            f = self.calculate_fitness(path)
            a = self.calculate_affinity(f['fitness'])
            solution = {
                'fitness': f['fitness'],
                'affinity': a,
                'distance': f['distance'],
                'time_penalty': f['time_penalty'],
                'path': path
            }
            evaluated_solutions.append(solution)
        evaluated_solutions.sort(key=lambda x: x['affinity'], reverse=True)
        return evaluated_solutions

    def calc_pick_chances(self, solutions):
        total_affinity = 0
        for solution in solutions:
            total_affinity += solution['affinity']
        for solution in solutions:
            solution['pick_chance'] = solution['affinity'] / total_affinity

    def pick_n_by_roullete(self, n, pick_from):
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

    def clone_solution(self, solutions):
        solution = self.pick_n_by_roullete(1, solutions)[0]
        return copy.deepcopy(solution['path'])

    def mutate_solution(self, solution):
        if random.random() < self.mutation_chance:
            return self.mutations[random.randint(0, len(self.mutations) - 1)](solution)
        else:
            return solution

    def is_solution_similar_to_another(self, solution, solutions):
        for s in solutions:
            num_of_diffs = 0
            for i in range(0, len(s)):
                if s[i] != solution[i]:
                    num_of_diffs += 1
            if num_of_diffs < self.minimal_num_of_diffs:
                return True
        return False

    def log_population(self, solutions):
        for sol in solutions:
            self.out_file.write(str(sol) + '\n')
        self.out_file.write('\n')

    def next_generation(self):
        self.num_of_generation += 1
        self.out_file.write('------------- GENERATION ' + str(self.num_of_generation) + ' -------------\n')
        # print('------------- GENERATION ' + str(self.num_of_generation) + ' -------------')

        evaluated_solutions = self.evaluate_solutions(self.current_population)
        self.calc_pick_chances(evaluated_solutions)
        self.log_population(evaluated_solutions)
        print(evaluated_solutions[0])
        self.out_file.write(str(evaluated_solutions[0]) + '\n')
        self.best_solution = evaluated_solutions[0]

        cloned_solutions = []
        while len(cloned_solutions) < self.population_size:
            cloned_solution = self.clone_solution(evaluated_solutions)
            mutated_solution = self.mutate_solution(cloned_solution)
            if not self.is_solution_similar_to_another(mutated_solution, cloned_solutions):
                cloned_solutions.append(mutated_solution)
        evaluated_cloned_solutions = self.evaluate_solutions(cloned_solutions)

        next_population = []
        for i in range(0, self.num_of_solutions_to_generate):
            next_population.append(self.generate_antibody())

        for i in range(0, self.num_of_best_solutions_to_keep):
            next_population.append(evaluated_solutions[i]['path'])

        for i in range(0,self.num_of_worst_solutions_to_discard):
            evaluated_solutions.pop()

        solution_pool = evaluated_solutions + evaluated_cloned_solutions
        # print(len(solution_pool))
        self.calc_pick_chances(solution_pool)
        free_slots = self.population_size - self.num_of_best_solutions_to_keep - self.num_of_solutions_to_generate
        # print(str(free_slots))

        picked = self.pick_n_by_roullete(free_slots, solution_pool)
        # print(len(picked))

        next_population += list(map(lambda s: s['path'], picked))
        self.current_population = next_population
        self.log_population(self.current_population)

    def get_best_solution(self):
        return self.best_solution
