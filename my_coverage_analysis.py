import coverage
import matplotlib.pyplot as plt

# Load coverage data
cov = coverage.Coverage()
cov.load()

# Get coverage data as a dictionary
data = cov.get_data()
covered = {file: data.line_counts(fullpath=True)[file] for file in data.measured_files()}

# Plot data
files = list(covered.keys())
counts = list(covered.values())

plt.figure(figsize=(10, 5))
plt.bar(files, counts, color='green')
plt.xlabel('Files')
plt.ylabel('Lines Covered')
plt.title('Coverage Report')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
