import os
import re
import pandas as pd
from config import *
import openpyxl
import csv
from fuzzywuzzy import process

# def fill(right_format_file, right_order):
#     def read_csv(file_path):
#         with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#             reader = csv.reader(file)
#             data = list(reader)
#         return data
#
#     def write_csv(file_path, data):
#         with open(file_path, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             writer.writerows(data)
#
#     def modify_cell(data, row_index, col_index, new_value):
#         if row_index < len(data) and col_index < len(data[row_index]):
#             data[row_index][col_index] = new_value
#         else:
#             print("Invalid row or column index.")
#
#     data = read_csv(csv_path)
#
#     # Modify a specific cell
#     row_index = 1  # Change to the correct row index
#     col_index = 0  # Change to the correct column index
#     new_value = 'New Value'
#     modify_cell(data, row_index, col_index, new_value)
#
#     # Write the modified data back to the CSV file
#     write_csv(csv_path, data)
#
#     print(f"Modified cell ({row_index}, {col_index}) to '{new_value}' in {csv_path}")



def find_employee_index(right_format_file,employee):
    employees_from_csv_list = get_employees_from_csv(right_format_file)
    best_match, best_score = process.extractOne(employee, employees_from_csv_list)
    if best_score > 0:  # Adjust the threshold score as needed
        # Find the index of the best match
        best_index = employees_from_csv_list.index(best_match)
        return best_index

def get_employees_from_csv(full_path):
    non_empty_values = []
    try:
        # Attempt to read the CSV file with different encodings
        with open(full_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Iterate over each row in the CSV
            for row in reader:
                # Check if the row has at least two columns
                if len(row) > 1:
                    value = row[1].strip()  # Read the second column (index 1)
                    if value:  # Check if the value is not empty
                        non_empty_values.append(value)

    except UnicodeDecodeError:
        try:
            with open(full_path, mode='r', newline='', encoding='latin1') as file:
                reader = csv.reader(file)

                # Iterate over each row in the CSV
                for row in reader:
                    # Check if the row has at least two columns
                    if len(row) > 1:
                        value = row[1].strip()  # Read the second column (index 1)
                        if value:  # Check if the value is not empty
                            non_empty_values.append(value)

        except Exception as e:
            pass
            # print(f"Error reading {full_path}: {e}")

        except FileNotFoundError as e:
            pass
            # print(f'file was moved {full_path}')

    return non_empty_values[2:]  # Move return statement outside of the try-except blocks

def find_file_with_all_employeees(employees,csv_path):
    if os.path.isdir(csv_path):
        for filename in os.listdir(csv_path):
            full_path = os.path.join(csv_path, filename)
            if filename.startswith('.') or not filename.lower().endswith('.csv'):
                continue
            # print(f'this is the full path {full_path}')
            employees_from_csv_list = get_employees_from_csv(full_path)
            # print(f'this is employees from csv {employees_from_csv_list}')
            use_file = check_employees_in_list(employees_from_csv_list,employees)
            if use_file:
                # print(f'this is the right file to use: {full_path}')
                # print(f'these are all the employees{employees}')
                return True, full_path
            else:
                pass
            message = 'No file with all the employees was found'
        return False, message
    else:
        return False, f'The path {csv_path} is not a directory'
        # print(f"The path {csv_path} is not a directory. / no files were found")


def create_word_list(employee_to_csv_list):
    # Create a list of all individual words from the employee names
    # word_list = []
    # for employee in employee_to_csv_list:
    #     words = employee.lower().split()
    #     words = words.strip()
    #     word_list.extend(words)
    word_list = [word.strip().lower() for item in employee_to_csv_list for word in item.split()]
    return word_list

def check_employees_in_list(employee_to_csv_list, employees):
    # Generate list of individual words
    word_list = create_word_list(employee_to_csv_list)
    word_list_set = set(word_list)  # Convert to set for faster lookups
    # print(f'this is the word list set {word_list}')

    for employee in employees:
        # print(f'employee {employee}')
        employee_words = [word.strip() for word in employee.lower().split()]
        # print(f'these are the employee words {employee_words}')
        if len(employee_words) > 1:
            # Check if at least one word from multi-word names is in the word_list
            if any(word in word_list_set for word in employee_words):
                continue
            else:
                # print(f'Employee "{employee}" is missing.')
                return False
        else:
            # Check if single word names are in the word_list
            if employee.strip().lower() in word_list_set:
                continue
            else:
                # print(f'Employee "{employee}" is missing.')
                return False
    return True
