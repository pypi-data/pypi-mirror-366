import csv
import itertools

class PipesimInputGenerator():
    MAX_ROWS = 1_000_000

    def generate(self, param_ranges, output_file):
        # Generate all combinations of parameters
        keys = list(param_ranges.keys())
        value_iterables = (param_ranges[key] for key in keys)

        # Open CSV and stream the combinations
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(keys)

            for combo in itertools.islice(itertools.product(*value_iterables), self.MAX_ROWS):
                writer.writerow(combo)
                
            # for combo in itertools.product(*value_iterables):
            #     writer.writerow(combo)