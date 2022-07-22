import time
import json
import pandas as pd
import tabula
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import chromedriver_autoinstaller

APPROVED_PDF = "Faculty-approved-HSS-list-as-of-July-7-2022.pdf"
TTB = "https://ttb.utoronto.ca/"
COURSES_INFO_JSON = "courses_info.json"
FILTERED_COURSES_INFO_JSON = "filtered_courses_info.json"
USER_SCHEDULE_CSV = "user_schedule.csv"

EMPTY_SLOT_CHAR = '0'

def retrieve_ttb_course_data(courses):
    #setup chrome and load page
    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome(options=webdriver.ChromeOptions())

    driver.get(TTB)

    driver.implicitly_wait(10)

    #wait to finish loading
    WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, "div[id=\"session\"]").find_element(By.CLASS_NAME, "ttb-pill"))

    courses_info = {}

    for course in courses:
        print("Processing", course)

        #reset site filters
        reset_button = driver.find_element(By.CLASS_NAME, "search-action").find_element(By.CLASS_NAME, "reset")
        WebDriverWait(driver, timeout=3).until(expected_conditions.element_to_be_clickable(reset_button)).send_keys(Keys.RETURN)

        WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, "div[id=\"session\"]").find_element(By.CLASS_NAME, "place-holder"))

        #select divisions
        division_selection = driver.find_element(By.CSS_SELECTOR, "div[id=\"division\"]")
        WebDriverWait(driver, timeout=3).until(expected_conditions.element_to_be_clickable(division_selection)).click()
        for ele_id in ["division-option-0-Faculty of Applied Science & Engineering", "division-option-1-John H. Daniels Faculty of Architecture, Landscape, & Design", "division-option-2-Faculty of Arts and Science"]:
            WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, ele_id)).click()

        #select session
        session_selection = driver.find_element(By.CSS_SELECTOR, "div[id=\"session\"]")
        WebDriverWait(driver, timeout=3).until(expected_conditions.element_to_be_clickable(session_selection)).click()
        for ele_id in ["session-option-2-Winter 2023  (S)"]:
            WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, ele_id)).click()

        #type course code
        course_search = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "courseSearch"))
        course_search_box = course_search.find_element(By.TAG_NAME, "input")
        course_search_box.send_keys(course)
        course_search_box.send_keys(Keys.DOWN)
        course_search_box.send_keys(Keys.RETURN)

        #search
        search_div = driver.find_element(By.CLASS_NAME, "search-action")
        search_button = search_div.find_element(By.CSS_SELECTOR, ".btn-primary:not(.reset)")
        WebDriverWait(driver, timeout=3).until(expected_conditions.element_to_be_clickable(search_button)).send_keys(Keys.RETURN)

        #check course offering
        results_header = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "resultsId"))

        if "(0 courses)" in results_header.text:
            courses_info[course] = None
            continue
        elif "(1 courses)" not in results_header.text:
            print("Found multiple ttb search results for course: " + course)

        course_results = driver.find_element(By.CLASS_NAME, "search-results-container").find_element(By.CLASS_NAME, "courses-section")

        course_title = course_results.find_element(By.CLASS_NAME, "course-title").text

        course_class_sections = course_results.find_elements(By.CLASS_NAME, "course-sections")

        course_classes = []

        for section in course_class_sections:
            label = section.find_element(By.CLASS_NAME, "label").text
            if any(class_type in label for class_type in ("Lectures", "Tutorials", "Practicals")):
                course_classes.extend(section.find_elements(By.CLASS_NAME, "course-section"))

        course_class_info = {}

        for course_class in course_classes:
            course_class_header = course_class.find_element(By.CLASS_NAME, "header").text
            course_class_info[course_class_header] = {}
            
            for info_name in ("day-time", "location", "instructor", "availability", "delivery-mode"):
                course_class_info[course_class_header][info_name] = course_class.find_element(By.CLASS_NAME, info_name).find_element(By.XPATH, "./following-sibling::*").text

        courses_info[course] = {}
        courses_info[course]["title"] = course_title
        courses_info[course]["class_info"] = course_class_info

    time.sleep(10)

    driver.quit()

    return courses_info

def extract_pdf_approved_courses():
    approved_courses_df_list = [df.iloc[:,0] for df in tabula.read_pdf(APPROVED_PDF, area=(0.75 * 72, 0.25 * 72, 10.25 * 72, 1.6 * 72), pages="all")]

    approved_courses_df = pd.concat(approved_courses_df_list, axis=0)

    return list(approved_courses_df[approved_courses_df.apply(lambda text: str(text)[0:3].isalpha() and str(text)[3:6].isnumeric())])

def prepare_courses_info_json():
    courses_info = retrieve_ttb_course_data(extract_pdf_approved_courses())

    courses_info_save_file = open(COURSES_INFO_JSON, "w")
    json.dump(courses_info, courses_info_save_file, indent=4)
    courses_info_save_file.close()

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

prepare_courses_info_json()

courses_info = load_courses_info_json()

prepare_filtered_courses_info_json(courses_info)