'''
Instructions for use:
Run in the same directory as courses_info.json [COURSES_INFO_JSON] and user_schedule.csv [USER_SCHEDULE_CSV]

Fill in user_schedule.csv [USER_SCHEDULE_CSV] with your timetable (0 [EMPTY_SLOT_CHAR] represents a currently free slot, and anything else represents a currently used slot)
This is easier if you use Excel or some other software that allows easy editing of .csv files, but any text editing software will do the job

Filtered course names will be printed in console, and detailed information will be saved in filtered_courses_info.json [FILTERED_COURSES_INFO_JSON]
Note that .json files can be opened by any text editing software (such as Notepad)
'''

import json

COURSES_INFO_JSON = "courses_info.json"
FILTERED_COURSES_INFO_JSON = "filtered_courses_info.json"
USER_SCHEDULE_CSV = "user_schedule.csv"

EMPTY_SLOT_CHAR = '0'

def load_courses_info_json():
    courses_info_save_file = open(COURSES_INFO_JSON, "r")
    courses_info_json = json.loads(courses_info_save_file.read())
    courses_info_save_file.close()

    return courses_info_json

def get_user_schedule():
    user_schedule_file = open(USER_SCHEDULE_CSV, "r")
    
    user_schedule = {}
    days = user_schedule_file.readline().strip().split(",")[1:]

    times = []
    availability = []
    while line_str := user_schedule_file.readline():
        line = line_str.strip().split(",")
        times.append(int(line[0].split(":")[0]))
        availability.append(line[1:])
    
    for i in range(len(days)):
        user_schedule[days[i]] = {}
    
        for j in range(len(times)):
            user_schedule[days[i]][times[j]] = availability[j][i]

    return user_schedule

def interpret_day_time(day_time_str):
    day, block = day_time_str.split(" ", 1)

    times = {}
    times["start"], times["end"] = block.split(" - ")

    for key in times:
        hour_minute, ampm = times[key].split(" ")
        hour, minute = hour_minute.split(":")
        hour, minute = int(hour), int(minute)

        if ampm.upper() == "AM":
            hour = hour - 12 if hour == 12 else hour
        elif ampm.upper() == "PM":
            hour = hour + 12 if hour != 12 else hour
        else:
            raise Exception("Invalid time AM/PM found: " + day_time_str)
        
        times[key] = [hour, minute]

    if times["end"][1] != 0:
        times["end"][0] += 1
    
    time_block_list = tuple(range(times["start"][0], times["end"][0]))
    
    return (day, time_block_list)

def determine_course_schedule_compatibility(schedule, course_info):
    attendable_course_class_codes_by_type = {"LEC": None, "TUT": None, "PRA": None}
    for course_class_code in course_info["class_info"]:
        try:
            interpreted_days_times = [interpret_day_time(day_time_str) for day_time_str in course_info["class_info"][course_class_code]["day-time"].split("\n")]
        except:
            interpreted_days_times = None
        
        for class_type in attendable_course_class_codes_by_type:
            if class_type == course_class_code[:3]:
                attendable_course_class_codes_by_type[class_type] = [] if attendable_course_class_codes_by_type[class_type] == None else attendable_course_class_codes_by_type[class_type]
                if interpreted_days_times == None:
                    attendable_course_class_codes_by_type[class_type].append(course_class_code)
                else:
                    if all([all([schedule[class_day_time[0]][hour] == EMPTY_SLOT_CHAR for hour in class_day_time[1]]) for class_day_time in interpreted_days_times]):
                        attendable_course_class_codes_by_type[class_type].append(course_class_code)
    
    attendable_course_class_codes = []
        
    for class_type in attendable_course_class_codes_by_type:
        if attendable_course_class_codes_by_type[class_type] == []:
            return None
        elif attendable_course_class_codes_by_type[class_type] != None:
            attendable_course_class_codes.extend(attendable_course_class_codes_by_type[class_type])
    
    return attendable_course_class_codes

def filter_courses_by_schedule(schedule, courses_info):
    filtered_courses_info = {}

    for course in courses_info:
        if courses_info[course] == None:
            continue
        
        attendable_course_class_codes = determine_course_schedule_compatibility(schedule, courses_info[course])

        if attendable_course_class_codes == None:
            continue

        filtered_courses_info[course] = {}
        filtered_courses_info[course]["title"] = courses_info[course]["title"]
        filtered_courses_info[course]["class_info"] = {}

        for class_code in attendable_course_class_codes:
            filtered_courses_info[course]["class_info"][class_code] = courses_info[course]["class_info"][class_code]
    
    return filtered_courses_info

def prepare_filtered_courses_info_json(courses_info):
    filtered_courses_info = filter_courses_by_schedule(get_user_schedule(), courses_info)

    filtered_courses_info_save_file = open(FILTERED_COURSES_INFO_JSON, "w")
    json.dump(filtered_courses_info, filtered_courses_info_save_file, indent=4)
    filtered_courses_info_save_file.close()

    print("Found", len(filtered_courses_info),"Courses:")

    for course in filtered_courses_info:
        print(filtered_courses_info[course]["title"])

prepare_filtered_courses_info_json(load_courses_info_json())