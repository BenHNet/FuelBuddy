import coverage
import matplotlib.pyplot as plt

# Load coverage data
cov = coverage.Coverage()
cov.load()

# Access coverage data
covered = {}
for filename in cov.get_data().measured_files():
    # Get the analysis for each file
    analysis = cov.analysis2(filename)
    # analysis2 returns a tuple where the first element is the list of executable lines
    # and the second element is the list of missed lines
    total_lines = len(analysis[1])
    missed_lines = len(analysis[2])
    covered_lines = total_lines - missed_lines
    covered[filename] = covered_lines

# Plotting the data
filenames = list(covered.keys())
counts = list(covered.values())

plt.figure(figsize=(10, 5))
plt.barh(filenames, counts, color='green')
plt.xlabel('Lines Covered')
plt.title('Coverage Report')
plt.tight_layout()
plt.show()