# models.py
#version 1.3
#added review folder and error messages
import pandas as pd
import re
from dataformat import *
import os
import datetime
from config import *
from transform import *
from rewrite import *
import time
import sys
#
class Employee:
    def __init__(self, name, work_time=0, holiday_hours=0, absent_hours=0, sick_hours=0, vacation_hours=0, overtime_week1=0,overtime_week2=0, message = '', file_message = ''):
        self.name = name
        self.work_time = work_time
        self.holiday_hours = holiday_hours
        self.absent_hours = absent_hours
        self.sick_hours = sick_hours
        self.vacation_hours = vacation_hours
        self.overtime_week1 = overtime_week1
        self.overtime_week2 = overtime_week2
        self.hours_minutes_format = "0:00"
        self.message = message
        self.file_message = file_message

    def __str__(self):
        return (f"\nEmployee(name={self.name}, work_time={self.work_time}, hours_minutes_format={self.hours_minutes_format}, "
                f"holiday_hours={self.holiday_hours}, absent_hours={self.absent_hours}, sick_hours={self.sick_hours}, "
                f"vacation_hours={self.vacation_hours}, overtime_week1={self.overtime_week1})")

    def print_work_hours(self):
        #HARD PRINT
        print(f"TOTAL HOURLY: {self.work_time}\nOVERTIME: {self.overtime_week1}"
              f"\nVACATION {self.vacation_hours}\nSICK {self.sick_hours}\nHOLIDAY {self.holiday_hours}\n")

def extract_employee_names(df):
    employee_names = []

    for index, row in df.iterrows():
        # Check if the current row is followed by "TIME IN"
        if index + 1 < len(df):
            next_row = df.iloc[index + 1]
            # print(f'Next row{next_row.iloc[0]}')
            if pd.notna(next_row.iloc[0]) and isinstance(next_row.iloc[0], str) and next_row.iloc[0].strip().lower() == 'time in':
                # The current row contains the employee name
                if pd.notna(row.iloc[0]) and row.iloc[0] != '':
                    employee_names.append(row.iloc[0])

    return employee_names

def create_employees(employee_names):
    employees = [Employee(name) for name in employee_names]
    return employees

def rows_to_keep(employee_names,df):
    employees = employee_names
    repeated_index = [name for name in employees for _ in range(5)]
    num_rows_to_keep = len(employee_names)*5
    df = df.iloc[:num_rows_to_keep]
    df.index = repeated_index
    # print(df.to_string())
    return df

def get_employee_df(df,employee_name):
    filtered_df = df.loc[employee_name]
    return filtered_df

def get_valid_columns(df):
    subset_df = df.iloc[1:4, :]
    subset_df = subset_df.iloc[:, 1:14]
    valid_columns = subset_df.columns[subset_df.notna().all(axis=0)]
    filtered_df = subset_df[valid_columns]
    return filtered_df

def get_hours(df):
    # print(df.to_string())
    def convert_to_time(time):
        time = time.strip()
        # print('time')
        # print(time)

        # Correct regex patterns
        pattern_hh_mm_ss = r'(\d{1,2}):(\d{2}):(\d{2})'  # Matches HH:MM:SS
        pattern_hh_mm = r'(\d{1,2}):(\d{2})'  # Matches HH:MM

        match_3 = re.match(pattern_hh_mm_ss, time)
        match_2 = re.match(pattern_hh_mm, time)

        if match_3:
            # print('match HH:MM:SS')
            hour = int(match_3.group(1))  # Extract the hour
            minute = int(match_3.group(2))  # Extract the minute
            second = int(match_3.group(3))  # Extract the second
            # print(f"Hour: {hour}, Minute: {minute}, Second: {second}")
            total = float(hour * 60 + minute)
            # print('total minutes')
            # print(total)
            return total

        elif match_2:
            # print('match HH:MM')
            hour = int(match_2.group(1))  # Extract the hour
            minute = int(match_2.group(2))  # Extract the minute
            total = float(hour * 60 + minute)
            # print('total minutes')
            # print(total)
            return total

        else:
            # print(f"{time} does not match any known time format.")
            return None


    sum_minutes = 0
    hours_by_week1 = 0
    hours_by_week2 = 0
    for column_name, column_data in df.items():
        week1 = ['MON', 'TUE', 'TUES', 'WED', 'THU', 'FRI','SAT','SUN']
        week2 = ['MON2', 'TUE2', 'TUES2', 'WED2', 'THU2', 'FRI2','SAT2','SUN2']
        values = []
        for value in column_data:
            value = convert_to_time(str(value))
            values.append(value)

        # values = [convert_to_time(str(value)) for value in column_data]
        start, end, bre = values[0], values[1], values[2]
        try:
            total = end - bre - start
        except TypeError:
            total = 0

        if column_name in week1:
            hours_by_week1 += total

        if column_name in week2:
            hours_by_week2 += total

        sum_minutes += total

    total_hours_by_week1 = hours_by_week1 / 60
    total_hours_by_week2 = hours_by_week2 / 60
    #overtime = check_overtime(total_hours_by_week1, total_hours_by_week2)
    total_hours = sum_minutes / 60
    minutes_format = int(sum_minutes % 60)
    hours_minutes_format = int(sum_minutes / 60)
    hours_minutes_format = f'{hours_minutes_format}.{str(minutes_format).zfill(2)}'
    hours_minutes_format = float(hours_minutes_format)

    return total_hours, hours_minutes_format, sum_minutes, total_hours_by_week1, total_hours_by_week2

# def pattern():
#     pattern = ["time in", "time out", "break", "total"]

def count_vacation_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'vacation')).sum().sum()
    return count

def count_absent_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'absent')).sum().sum()
    return count

def count_holiday_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'holiday')).sum().sum()
    return count
def count_sick_occurrences(df):
    count = (df.map(lambda x: isinstance(x, str) and x.lower() == 'sick')).sum().sum()
    return count

def check_same(df,days_row):
    df.columns = days_row
    df = df.dropna(axis =1, how='all')
    two_week_total = get_total_hours(df,days_row)
    return two_week_total

def get_total_hours(df,columns):
    # Find the index of the last column with '2'
    last_2_index = -1
    for idx, col in enumerate(columns):
        if isinstance(col, str) and '2' in col:
            last_2_index = idx
    index = last_2_index + 2
    # Check if the target index is within the bounds of the columns list
    if index < len(columns):
        check = df.iloc[:, index].dropna().tolist()
    else:
        return None  # or an appropriate message, if index out of bounds
    return check

def compare_list_details(list1, sum_minutes, list2, employee,all_correct,incorrect):
    #it is timedelta
    if isinstance(list2,datetime.timedelta):
        parts = list2.total_seconds()/60

    #it is HH.MM
    elif isinstance(list2, int | float):
        list2 = f"{list2:.2f}"
        parts = list2.split('.')
        list2 = float(list2)
        hours = parts[0]
        minutes = parts[1]
        parts = int(hours)*60+int(minutes)
    else:
        #HARD PRINT but nothing should be printed
        print(r'I can\'t figure out the week1+week2 total from Excel')
    # print(f'the sum minutes = {sum_minutes} and the list2 {list2} and the parts {parts} and the hours = {hours} and the minutes = {minutes}')
    if sum_minutes != parts:
        incorrect.append(employee)
        if isinstance(list2, datetime.timedelta):
            message = f"{employee} INCORRECT\nHH:MM value is {list1} but Excel sheet shows {parts}.\n"
        elif isinstance(list2, int | float):
            if list1 < 0:
                message = f"{employee} INCORRECT\nExcel is put in a format (in-out-in-out) that Savior does not understand.\n"

            else:    
                message = f"{employee} INCORRECT\nHH:MM value is {list1} but Excel sheet shows {list2}.\n"
        else:
            message = f"{employee} INCORRECT\nHH:MM value is {list1} but Excel sheet shows {list2}.\n"

        # print(f"{employee} INCORRECT\nHH:MM value is {list1} but Excel sheet shows {list2}.")
    else:
        message = f"{employee} CORRECT"
        all_correct = all_correct + 1
    return all_correct,message, incorrect

def error_check(file_path, directory, df):
    return True
    # days_row = df.iloc[0]
    # # print(days_row)
    # days_row = days_row.tolist()

    # #make sure that the workdays have MON and MON2 
    # days_row = set_workdays(days_row)

    # df.iloc[0] = days_row

    # #prints the first_columnm, the employee names, time in time out
    # first_column = df.iloc[:, 0]
    # # print(first_column)
    # first_column_list = first_column.tolist()
    # # print(first_column_list)
    # first_column_list = nan_none(first_column_list)
    # first_column_list = time_total(first_column_list)
    # # print(first_column_list)
    # df.iloc[:,0]=first_column_list
    # check_original = check_same(df,days_row)
    # df = merge_rows(df)
    # employee_names = extract_employee_names(df)
    # #HARD PRINT
    # if len(check_original) != len(employee_names):
    #     filename = os.path.basename(file_path)
    #     print(f'{filename} is missing values in the WEEK1 + WEEK2 Total column')
    # return len(check_original)==len(employee_names)

def main(file_path, directory, df):
    print_dict = {}
    #takes the first row of the dataframe where the dates and weekdays are
    days_row = df.iloc[0]
    # print(days_row)
    days_row = days_row.tolist()

    #make sure that the workdays have MON and MON2 
    days_row = set_workdays(days_row)

    df.iloc[0] = days_row

    #prints the first_columnm, the employee names, time in time out
    first_column = df.iloc[:, 0]
    # print(first_column)
    first_column_list = first_column.tolist()
    # print(first_column_list)
    first_column_list = nan_none(first_column_list)
    first_column_list = time_total(first_column_list)
    # print(first_column_list)
    df.iloc[:,0]=first_column_list
    check_original = check_same(df,days_row)
    # print(check_original)
    df = merge_rows(df)

    employee_names = extract_employee_names(df)
    # print(len(employee_names))

    df = rows_to_keep(employee_names, df)
    employees = create_employees(employee_names)

    all_employees_location = []
    all_correct = 0
    incorrect = []
    for index, employee in enumerate(employees):
        missing_total = False
        df_sub = get_employee_df(df, employee.name)
        vacation_count = count_vacation_occurrences(df_sub)
        absent = count_absent_occurrences(df_sub)
        holiday = count_holiday_occurrences(df_sub)
        sick = count_sick_occurrences(df_sub)

        df_sub.columns = days_row
        # print(df_sub.to_string())
        df_work_hours = get_valid_columns(df_sub)
        # print('final df')
        # print(df_work_hours.shape)
        # print(df_work_hours.to_string())
        # print('valid df')
        # print(df_work_hours.to_string())

        # print('good rows df')
        # print(df_work_hours.to_string())
        total_hours, hours_minutes_format, sum_minutes, total_hours_by_week1, total_hours_by_week2 = get_hours(df_work_hours)
        total_hours = float(total_hours)
        total_hours = f"{total_hours:.2f}"
        employee.work_time,employee.hours_minutes_format  = total_hours,hours_minutes_format
        check_computer = employee.hours_minutes_format
        employee.vacation_hours,employee.absent_hours,employee.holiday_hours,employee.sick_hours = vacation_count,absent,holiday,sick
        employee.overtime_week1,employee.overtime_week2  = total_hours_by_week1,total_hours_by_week2
        try:
            original = check_original[index]
        except IndexError:
            #HARD PRINT but nothing should be printed
            original = 0
            missing_total = True


        all_correct, message,incorrect = compare_list_details(check_computer, sum_minutes,original, employee.name, all_correct,incorrect)
        if employee.name.lower() == 'Lewis Anthony'.lower():
            all_employees_location.append('Luis Anthony')
        else:
            all_employees_location.append(employee.name)

        employee.message = message

        # write_file():
        # directory, filename = os.path.split(file_path)
        # print(f'File name used: {filename}')
        # employee.print_work_hours()
        # print('\n')

    status, right_format_file = find_file_with_all_employeees(all_employees_location,directory)
    move_check = ''
    if status and all_correct + len(incorrect) == len(employees):
        for employee in employees:
            if missing_total == True:
                move_check = 'Total Column has Missing Values'
            elif employee.name in incorrect:
                move_check = 'Savior and BLS Computed Different Values'

            else:
            #TEST
            # pass
                right_order = [employee.work_time, employee.overtime_week1, employee.overtime_week2,employee.vacation_hours,employee.sick_hours,employee.holiday_hours]
                len_csv_employees, index = find_employee_index(right_format_file,employee.name)
                fill_get_rename(right_format_file, right_order, index)
            # else: 
            #     right_format_file = 'Goldfine Timesheet has an extra employee'
        if move_check != '': 
            move_file_check(right_format_file,move_check)
            move_file_check(file_path,move_check)

        elif len_csv_employees == len(employees):
            move_file(right_format_file)
            move_file(file_path)
        elif len_csv_employees != len(employees):
            move_file_check(right_format_file,'BLS has new employee or fired someone')
            move_file_check(file_path,'BLS has new employee or fired someone')



    #counting if '-' values are there twice, otherwise can fill everything that is correct but not '-'

    
    # count_dash = 0
    # has_neg = False
    # count = 0
    # for employee in employees: 
    #     if '-' in employee.message:
    #         count_dash += 1
    #         has_neg = True
    # if status and all_correct+count_dash == len(employees) and has_neg == True:
    #     for employee in employees:
    #         #TEST
    #         # pass
    #         right_order = [employee.work_time, employee.overtime_week1, employee.overtime_week2,employee.vacation_hours,employee.sick_hours,employee.holiday_hours]
    #         len_csv_employees, index = find_employee_index(right_format_file,employee.name)
    #         if len_csv_employees == len(employees):
    #             # print(f'the index is {index}')
    #             fill_get_rename(right_format_file, right_order, index)
    #         # else: 
    #         #     right_format_file = 'Goldfine Timesheet has an extra employee'
    #     if len_csv_employees == len(employees):
    #         move_file_check(right_format_file)
    #         move_file_check(file_path)
    

    #this is where I am printing the errors
    if not status or all_correct != len(employees):
        for employee in employees:
            employee.file_message = right_format_file
            directory, filename = os.path.split(file_path)
            if 'There is one or more' in employee.file_message or 'No Goldfine Timesheet with all' in employee.file_message:
                if filename not in print_dict:
                    print_dict[filename] = []  # Initialize an empty list for this filename
                print_dict[filename].append('There is no corresponding Goldfine Timesheet')  # Append the message
                #HARD PRINT

                # print(f'\nFile name used: {filename}')
                # print(employee.file_message)
                # print('\n')
                break
            elif 'INCORRECT' in (employee.message):
                # if '-' in (employee.message):
                #     continue
                # hard print
                # if 'Total Column' in employee.file_message:
                #     break
                    # if filename not in print_dict:
                    #     print_dict[filename] = []
                    # print_dict[filename].append("A value is missing in the week1+week2 total column.")

                    # print(f'\nFile name used: {filename}')
                    # print("A value is missing in the week1+week2 total column.")
                # else: 

                if filename not in print_dict:
                    print_dict[filename] = []
                print_dict[filename].append(f'{employee.message}')  # Append the employee message
                    # print(f'\nFile name used: {filename}')
                    # print(employee.message)

        skip_print = []
        for filename in print_dict:
            for value in print_dict[filename]: 
                if 'Excel sheet shows 0.0' in value: 
                    skip_print.append(filename)

        for filename, messages in print_dict.items():
            if filename in skip_print:
                continue
            else:
                print(f"\n*******************************************")
                print({filename})
                for message in messages:
                    # Replace '\n' with a newline for clarity in messages
                    formatted_message = message.replace('\\n', '\n')
                    print(formatted_message)

def models(file_path):
    do_your_thing(file_path)

    # Define the end date
    end_date = datetime.datetime(2025, 1, 1)  # Example: 5th August 2024

    # Get the current date
    current_date = datetime.datetime.now()

    # Check if the current date is past the end date
    if current_date > end_date:
        # def delete_file(file_path):
        #     """Delete the file at file_path."""
        #     try:
        #         os.remove(file_path)
        #         #HARD PRINT
        #         # print(f"{file_path} has been deleted.")
        #     except Exception as e:
        #         #HARD PRINT
                # print(f"Failed to delete {file_path}: {e}")
        #HARD PRINT
        print(f"This script is no longer allowed to run after the specified date: {end_date}")
        # print(f"The application will be deleted in 10 seconds")
        # time.sleep(10)
        # delete_file(sys.argv[0])
        return  # Exit the script

    # The rest of your script
    # HARD PRINT
    print(f"Running script... Deadline to renew is: {end_date}\n")

    if os.path.isfile(file_path):
        pass
        # main(file_path)
    elif os.path.isdir(file_path):

        #uncomment below ***
        # error_occured = False
        # for filename in os.listdir(file_path):
        #     # Construct full file path
        #     full_path = os.path.join(file_path, filename)
        #     directory, x = os.path.split(full_path)

        #     if filename.lower().endswith('.xls'):
        #         #HARD PRINT
        #         print('You need to change the format of a file from xls to xlsx.\n')
        #         return
        #     # Check if it's an Excel file and not a hidden file
        #     if filename.startswith('.') or not filename.lower().endswith('.xlsx'):
        #         continue

        #     # Call main with the full file path
        #     try:
        #         df = read_excel_ignore_hidden(full_path)

        #     except Exception as e:
        #         #HARD PRINT
        #         print(f'\nI could not read this file: {full_path}\n')
        #         continue

        #     try:
        #         check_passed = error_check(full_path, directory,df)
        #         if check_passed == False:
        #             error_occured = True

        #     except Exception as e:
        #         df = pd.read_excel(full_path)
        #         check_passed = error_check(full_path, directory,df)
        #         if check_passed == False:
        #             error_occured = True
        # if error_occured: 
        #     return
        #uncomment below ***

        for filename in os.listdir(file_path):
             # Construct full file path
            full_path = os.path.join(file_path, filename)
            directory, x = os.path.split(full_path)

            # Check if it's an Excel file and not a hidden file
            if filename.startswith('.') or not filename.lower().endswith('.xlsx'):
                continue

            # Call main with the full file path
            try:
                df = read_excel_ignore_hidden(full_path)

            except Exception as e:
                #HARD PRINT
                print(f'\nI could not read this file: {full_path}\n')
                continue

            try:
                main(full_path, directory,df)
            except Exception as e:
                df = pd.read_excel(full_path)
                main(full_path, directory,df)
        #HARD PRINT
        print('Whew I am done running <3')


def do_your_thing(csv_path):
    rename_all(csv_path)

models('/Users/jinhe/Downloads/Total Column has Missing Values')