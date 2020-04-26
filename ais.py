import random
import pandas as pd
import copy


class AIS:
    def __init__(self, generate_antibody, calculate_fitness, mutations, clone_to_new_ratio, population_size):
        self.clone_to_new_ratio = clone_to_new_ratio
        self.population_size = population_size
        self.generate_antibody = generate_antibody
        self.calculate_fitness = calculate_fitness
        self.mutations = mutations

        self.out_file = open('log.txt', 'w')
        self.log_columns = ['fitness', 'clone_chance', 'mutation_chance']

        self.num_of_generation = 0
        self.current_population = []
        self.next_population = []
        self.best_solution = []
        for i in range(0, population_size):
            self.current_population.append(generate_antibody())

    def next_generation(self):
        self.next_population = []
        self.num_of_generation += 1
        print('Population size: ' + str(len(self.current_population)))
        solutions = []
        # calc fitness for solution
        for solution in self.current_population:
            fitness = self.calculate_fitness(solution)
            solutions.append({
                'fitness': fitness,
                'solution': solution
            })
        solutions = sorted(solutions, key=lambda s: s['fitness'])
        solutions = solutions[0:20]

        self.out_file.write('Best 10 solutions: \n')
        total_fitness = 0
        for solution in solutions:
            total_fitness += solution['fitness']
            self.out_file.write(str(solution['fitness']) + '\n')
            self.out_file.write(str(solution['solution']) + '\n')

        self.out_file.write('\n')

        for i in range(0, int(len(solutions) / 2) + 1):
            solutions[i]['mutation_chance'] = solutions[i]['fitness'] / total_fitness
            solutions[i]['clone_chance'] = solutions[-(i + 1)]['fitness'] / total_fitness

            solutions[-(i + 1)]['mutation_chance'] = solutions[-(i + 1)]['fitness'] / total_fitness
            solutions[-(i + 1)]['clone_chance'] = solutions[i]['fitness'] / total_fitness
        # df = pd.DataFrame(columns=self.log_columns)
        # for solution in solutions:
        #     df = df.append(pd.DataFrame([[solution['fitness'], solution['clone_chance'], solution['mutation_chance']]], columns=self.log_columns))
        # df.to_csv('./logs/' + str(self.num_of_generation) + '.csv')
        self.best_solution = solutions[0]['solution']
        print('  best fitness: ' + str(solutions[0]['fitness']))
        num_solutions_to_clone = int(self.population_size * self.clone_to_new_ratio)
        num_solutions_to_generate = self.population_size - num_solutions_to_clone
        for i in range(0, num_solutions_to_clone):
            t = 0
            # r = random.uniform(0, 1)
            r = random.random()
            for solution in solutions:
                t += solution['clone_chance']
                if r <= t:
                    m = random.uniform(0, 1)
                    sol = copy.deepcopy(solution['solution'])
                    if m < 0.9:
                        sol = self.mutations[random.randint(0, len(self.mutations) - 1)](sol)
                    # if m < solution['mutation_chance']:
                    #     self.out_file.write('cloned solution with mutation, fitness was ' + str(solution['fitness']) + '\n')
                    #     sol = self.mutate_solution(sol)
                    # else:
                    #     self.out_file.write('cloned solution with fitness ' + str(solution['fitness']) + '\n')
                    self.next_population.append(sol)
                    break
        for i in range(0, num_solutions_to_generate):
            self.out_file.write('generated new solution \n')
            self.next_population.append(self.generate_antibody())

        self.out_file.write('\n')
        for val in self.next_population:
            self.out_file.write(str(val) + '\n')
        self.current_population = self.next_population
        self.out_file.write('\n')
        self.out_file.write('\n')

    def get_best_solution(self):
        return self.best_solution
