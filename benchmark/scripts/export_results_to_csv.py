import csv


# filename = '..\\..\\documentation\\comparsion_cp_x_ilp.csv'
# with open(filename, 'w', newline='') as csvfile:
#     fieldnames = ['name', ' ', 'details', ' ']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     fieldnames = ['first_name', 'last_name', 'age', 'phone']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     writer.writerow({'first_name': 'Baked', 'last_name': 'Beans', 'age': '20', 'phone': '777888999'})
#     writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam', 'age': '20', 'phone': '777888999'})
#     writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam', 'age': '20', 'phone': '777888999'})


with open('..\\outputs\\logs\\output_test_n035_w4_cplex.txt', 'r') as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if 'value total' in line or 'time total' in line]

print("ILP")
for line in filtered_lines:
    print(line.strip())
print("----------------------------------------------------------------")

with open('..\\outputs\\logs\\output_test_n035_w4_docplex.txt', 'r') as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if 'value total' in line or 'time total' in line]

print("CP")
for line in filtered_lines:
    print(line.strip())
print("----------------------------------------------------------------")