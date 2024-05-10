import csv
import sys


def get_filtered_data(filenames: list[str]):
    data = []
    for filename in enumerate(filenames):
        with open(filename, 'r') as file:
            lines = file.readlines()
        filtered_lines = [line for line in lines if 'value total' in line or 'time total' in line]
        data.append(filtered_lines)
    return data

def main(result_filename: str, input_filename: str, output_filenames: list[str]):
    output_data = get_filtered_data(output_filenames)

    filename = '..\\..\\documentation\\comparsion_cp_x_ilp.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['name', ' ', 'details', ' ']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        fieldnames = ['first_name', 'last_name', 'age', 'phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'first_name': 'Baked', 'last_name': 'Beans', 'age': '20', 'phone': '777888999'})
        writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam', 'age': '20', 'phone': '777888999'})
        writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam', 'age': '20', 'phone': '777888999'})


    # with open('..\\outputs\\logs\\output_test_n035_w4_cplex.txt', 'r') as file:
    # with open('..\\outputs\\logs\\output_test_n035_w4_docplex.txt', 'r') as file:

if __name__ == "__main__":
    result_filename = int(sys.argv[1])
    input_filename = int(sys.argv[2])
    output_filenames = sys.argv[3:]
    main(result_filename, input_filename, output_filenames)