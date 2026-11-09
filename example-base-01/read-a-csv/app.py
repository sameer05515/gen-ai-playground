import csv

data = []

with open("employees.csv", "r") as file:
    reader = csv.reader(file)

    for row in reader:
        data.append(tuple(row))

# Convert list of tuples into nested tuple
nested_tuple = tuple(data)

print(nested_tuple)