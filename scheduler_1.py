import csv
import os
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta

# Define the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALL_SEMESTERS = [1, 2, 3, 4]  # All semesters from batch file

def normalize_path(path):
    """Helper function to normalize file paths"""
    if not os.path.isabs(path):
        path = os.path.join(SCRIPT_DIR, path)
    return os.path.normpath(path)

class Course:
    def __init__(self, name, course_id, faculty_name, semester, l, t, p, s, c, 
                 registered_students, department):
        self.name = name
        self.course_id = course_id
        self.faculty_name = faculty_name
        self.semester = int(semester)
        self.ltpsc = {
            "L": int(l) if l else 0,
            "T": int(t) if t else 0,
            "P": int(p) if p else 0,
            "S": int(s) if s else 0,
            "C": int(c) if c else 0
        }
        self.registered_students = int(registered_students)
        self.department = department
        self.duration = self.calculate_duration()
        self.batches = []

    def calculate_duration(self):
        return (self.ltpsc["L"] + self.ltpsc["T"] + (self.ltpsc["P"] * 2)) / 3

class Room:
    def __init__(self, room_id, room_number, capacity, room_type):
        self.room_id = room_id
        self.room_number = room_number
        self.capacity = int(capacity)
        self.room_type = room_type
        self.schedule = {}

class Faculty:
    def __init__(self, name, department, course_code, preferred_slots):
        self.name = name
        self.department = department
        self.course_code = course_code
        self.preferred_slots = self._parse_time_slots(preferred_slots)
        self.max_hours_per_day = 6  # Default value
        self.schedule = {}

    def _parse_time_slots(self, slots_str):
        if not slots_str:
            return []
        return [slot.strip() for slot in slots_str.strip('"').split(',')]

class BatchConfig:
    def __init__(self, department, semester, total_students, sections, lab_batch_size):
        self.department = department
        self.semester = int(semester)
        self.total_students = int(total_students)
        self.sections = int(sections)
        self.batch_size = int(lab_batch_size)

class TimetableScheduler:
    def __init__(self):
        self.courses: Dict[str, Course] = {}
        self.rooms: Dict[str, Room] = {}
        self.faculty: Dict[str, Faculty] = {}
        self.batch_configs: Dict[str, BatchConfig] = {}
        self.time_slots = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00',
            '12:00-13:00', '14:00-15:00', '15:00-16:00',
            '16:00-17:00'
        ]
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.faculty_schedule = {}
        self.room_schedule = {}
        self.morning_break = {"start": "11:00", "duration": 15}
        self.lunch_break = {"start": "13:00", "duration": 60}
        self.current_semester = None

    def reset_schedules(self):
        """Reset schedules between semesters"""
        self.faculty_schedule = {}
        self.room_schedule = {}
        self.courses = {}
        self.faculty = {}

    def load_all_batch_configs(self, filename: str):
        """Load batch configurations for all semesters"""
        print(f"\nLoading batch configurations from {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    config = BatchConfig(
                        department=row['Department'],
                        semester=row['Semester'],
                        total_students=row['Total_Students'],
                        sections=row['Sections'],
                        lab_batch_size=row['BatchSize']
                    )
                    key = f"{config.department}_{config.semester}"
                    self.batch_configs[key] = config
                    print(f"Loaded batch config: {config.department} Semester {config.semester}")
        except Exception as e:
            print(f"Error loading batch configs: {str(e)}")
            raise

    def load_all_courses(self, filename1: str, filename2: str, semester: int):
        """Load courses from both course files for the specified semester"""
        self.courses.clear()  # Clear previous courses
        
        # Normalize file paths
        filename1 = normalize_path(filename1)
        filename2 = normalize_path(filename2)
        
        # Load from courses_1.csv
        try:
            with open(filename1, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['Semester']) == semester:
                        self._add_course_from_row(row)
        except Exception as e:
            print(f"Warning: Error loading from {filename1}: {str(e)}")

        # Load from courses.csv
        try:
            with open(filename2, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['Semester']) == semester:
                        self._add_course_from_row(row)
        except Exception as e:
            print(f"Warning: Error loading from {filename2}: {str(e)}")

    def _add_course_from_row(self, row):
        """Helper method to add a course from a CSV row"""
        try:
            faculty_name = self._get_faculty_for_course(row.get('Course Code') or row.get('Course ID'))
            if faculty_name:
                course = Course(
                    name=row['Course Name'],
                    course_id=row.get('Course Code') or row.get('Course ID'),
                    faculty_name=faculty_name,
                    semester=row['Semester'],
                    l=row['L'],
                    t=row['T'],
                    p=row['P'],
                    s=row['S'],
                    c=row['C'],
                    registered_students=row['Registered Students'],
                    department=row.get('Department')
                )
                self.courses[course.course_id] = course
                print(f"Loaded course: {course.course_id} - {course.name}")
        except Exception as e:
            print(f"Warning: Could not load course {row.get('Course Code') or row.get('Course ID')}: {str(e)}")

    def load_all_faculty(self, filename1: str, filename2: str):
        """Load faculty from both faculty files"""
        self.faculty.clear()  # Clear previous faculty
        
        # Load from faculty_1.csv
        try:
            with open(filename1, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    faculty = Faculty(
                        name=row['Faculty Name'],
                        department=row['Department'],
                        course_code=row['Course Code'],
                        preferred_slots=row['Preferred Time Slots']
                    )
                    self.faculty[faculty.name] = faculty
        except Exception as e:
            print(f"Warning: Error loading from {filename1}: {str(e)}")

        # Load additional faculty from faculty.csv
        try:
            with open(filename2, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row['Name']
                    if name not in self.faculty:
                        faculty = Faculty(
                            name=name,
                            department="",  # Department not specified in faculty.csv
                            course_code="",  # Course code not specified in faculty.csv
                            preferred_slots=row['Preferred Times']
                        )
                        self.faculty[faculty.name] = faculty
        except Exception as e:
            print(f"Warning: Error loading from {filename2}: {str(e)}")

    def load_all_rooms(self, filename1: str, filename2: str):
        """Load rooms from both room files"""
        self.rooms.clear()  # Clear previous rooms
        
        # Load from rooms_1.csv
        try:
            with open(filename1, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room = Room(
                        room_id=row['Room ID'],
                        room_number=row['Room Number'],
                        capacity=row['Capacity'],
                        room_type=row['Room Type']
                    )
                    self.rooms[room.room_id] = room
        except Exception as e:
            print(f"Warning: Error loading from {filename1}: {str(e)}")

        # Load additional rooms from rooms.csv
        try:
            with open(filename2, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room_id = row['id']
                    if room_id not in self.rooms:
                        room = Room(
                            room_id=room_id,
                            room_number=row['roomNumber'],
                            capacity=row['capacity'],
                            room_type=row['type']
                        )
                        self.rooms[room.room_id] = room
        except Exception as e:
            print(f"Warning: Error loading from {filename2}: {str(e)}")

    def load_batch_config(self, filename: str):
        print(f"\nLoading batch configuration from {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    config = BatchConfig(
                        department=row['Department'],
                        semester=row['Semester'],
                        total_students=row['Total_Students'],
                        sections=row['Sections'],
                        lab_batch_size=row['Lab_Batch_Size']
                    )
                    key = f"{config.department}_{config.semester}"
                    self.batch_configs[key] = config
                    print(f"Loaded batch config: {config.department} Semester {config.semester}")
        except Exception as e:
            print(f"Error loading batch config: {str(e)}")
            raise

    def load_courses_from_csv(self, filename: str):
        print(f"\nLoading courses from {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    faculty_name = self._get_faculty_for_course(row['Course Code'])
                    if faculty_name:
                        course = Course(
                            name=row['Course Name'],
                            course_id=row['Course Code'],
                            faculty_name=faculty_name,
                            semester=row['Semester'],
                            l=row['L'],
                            t=row['T'],
                            p=row['P'],
                            s=row['S'],
                            c=row['C'],
                            registered_students=row['Registered Students'],
                            department=row['Department']
                        )
                        self.courses[course.course_id] = course
                        print(f"Loaded course: {course.course_id} - {course.name}")
                    else:
                        print(f"Warning: No faculty found for course {row['Course Code']}")
        except Exception as e:
            print(f"Error loading courses: {str(e)}")
            raise

    def _get_faculty_for_course(self, course_code):
        """Helper method to get faculty for a course, handling department-specific course codes"""
        if not course_code:
            return None
            
        # Try to find faculty with exact course code match
        for faculty in self.faculty.values():
            if faculty.course_code == course_code:
                return faculty.name
                
        # If no exact match, try to find by department-specific code
        for faculty in self.faculty.values():
            dept_course_code = f"{faculty.department}_{course_code}"
            if faculty.course_code == dept_course_code:
                return faculty.name
                
        return None

    def load_rooms_from_csv(self, filename: str):
        print(f"\nLoading rooms from {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room = Room(
                        room_id=row['Room ID'],
                        room_number=row['Room Number'],
                        capacity=row['Capacity'],
                        room_type=row['Room Type']
                    )
                    self.rooms[room.room_id] = room
                    print(f"Loaded room: {room.room_id} ({room.room_type})")
        except Exception as e:
            print(f"Error loading rooms: {str(e)}")
            raise

    def load_faculty_from_csv(self, filename: str):
        print(f"\nLoading faculty from {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    faculty = Faculty(
                        name=row['Faculty Name'],
                        department=row['Department'],
                        course_code=row['Course Code'],
                        preferred_slots=row['Preferred Time Slots']
                    )
                    # Normalize the preferred time slots
                    faculty.preferred_slots = [self._normalize_time_slot(slot) for slot in faculty.preferred_slots]
                    self.faculty[faculty.name] = faculty
                    print(f"Loaded faculty: {faculty.name}")
        except Exception as e:
            print(f"Error loading faculty: {str(e)}")
            raise

    def _normalize_time_slot(self, slot):
        """Convert time slot to standard format (09:00-10:00)"""
        if not slot:
            return slot
        # Convert 9:00 to 09:00
        parts = slot.split('-')
        normalized_parts = []
        for part in parts:
            time_parts = part.strip().split(':')
            if len(time_parts[0]) == 1:
                time_parts[0] = '0' + time_parts[0]
            normalized_parts.append(':'.join(time_parts))
        return '-'.join(normalized_parts)

    def is_break_time(self, time_str: str) -> bool:
        time = datetime.strptime(time_str.split('-')[0], "%H:%M")
        
        morning_break_start = datetime.strptime(self.morning_break["start"], "%H:%M")
        morning_break_end = morning_break_start + timedelta(minutes=self.morning_break["duration"])
        
        lunch_break_start = datetime.strptime(self.lunch_break["start"], "%H:%M")
        lunch_break_end = lunch_break_start + timedelta(minutes=self.lunch_break["duration"])
        
        return (morning_break_start <= time <= morning_break_end or 
                lunch_break_start <= time <= lunch_break_end)

    def is_room_available(self, room: str, day: str, time: str) -> bool:
        if self.is_break_time(time):
            return False
        if room not in self.room_schedule:
            self.room_schedule[room] = {}
        if day not in self.room_schedule[room]:
            self.room_schedule[room][day] = set()
        return time not in self.room_schedule[room][day]

    def is_faculty_available(self, faculty_name: str, day: str, time: str) -> bool:
        if self.is_break_time(time):
            return False
            
        faculty = self.faculty.get(faculty_name)
        if not faculty:
            return False

        # Check if the time slot is in faculty's preferred slots
        if faculty.preferred_slots:
            normalized_time = self._normalize_time_slot(time)
            time_ok = False
            for slot in faculty.preferred_slots:
                if normalized_time == slot:
                    time_ok = True
                    break
            if not time_ok:
                return False

        if faculty_name not in self.faculty_schedule:
            self.faculty_schedule[faculty_name] = {}
        if day not in self.faculty_schedule[faculty_name]:
            self.faculty_schedule[faculty_name][day] = set()
        
        daily_hours = len(self.faculty_schedule[faculty_name].get(day, set()))
        if daily_hours >= faculty.max_hours_per_day:
            return False
            
        return time not in self.faculty_schedule[faculty_name][day]

    def create_lab_batches(self, course: Course):
        if course.ltpsc["P"] > 0:
            config_key = f"{course.department}_{course.semester}"
            batch_config = self.batch_configs.get(config_key)
            
            if batch_config:
                students_per_section = batch_config.total_students // batch_config.sections
                num_batches = (students_per_section + batch_config.batch_size - 1) // batch_config.batch_size
                
                for section in range(batch_config.sections):
                    for batch in range(num_batches):
                        batch_name = f"S{section+1}B{batch+1}"
                        course.batches.append(batch_name)
                
                print(f"Created {len(course.batches)} batches for course {course.course_id}")
            else:
                print(f"No batch configuration found for {config_key}")

    def schedule_slot(self, room: str, faculty_name: str, day: str, time: str):
        if room not in self.room_schedule:
            self.room_schedule[room] = {}
        if day not in self.room_schedule[room]:
            self.room_schedule[room][day] = set()
        self.room_schedule[room][day].add(time)
        
        if faculty_name not in self.faculty_schedule:
            self.faculty_schedule[faculty_name] = {}
        if day not in self.faculty_schedule[faculty_name]:
            self.faculty_schedule[faculty_name][day] = set()
        self.faculty_schedule[faculty_name][day].add(time)
        print(f"Scheduled: Room {room}, Faculty {faculty_name}, {day} {time}")

    def generate_timetable(self, semester: int, courses_file: str) -> List[dict]:
        print(f"\nGenerating Timetable for Semester {semester}")
        
        # Reset schedules but keep courses and faculty
        self.faculty_schedule = {}
        self.room_schedule = {}
        self.current_semester = semester
        
        timetable = []
        
        # Sort courses by total hours and registered students
        sorted_courses = sorted(
            [c for c in self.courses.values() if c.semester == semester],
            key=lambda c: (sum(c.ltpsc.values()), c.registered_students),
            reverse=True
        )

        for course in sorted_courses:
            print(f"\nScheduling course: {course.course_id} - {course.name}")
            self.create_lab_batches(course)
            course_entry = self._schedule_course(course)
            if course_entry:
                timetable.append(course_entry)
                print(f"Successfully scheduled {course.course_id}")
            else:
                print(f"Failed to schedule {course.course_id}")

        return timetable

    def _schedule_course(self, course: Course) -> dict:
        course_entry = {
            'Semester': course.semester,
            'Department': course.department,
            'Course Code': course.course_id,
            'Course Name': course.name,
            'Faculty': course.faculty_name,
            'Timeslots': []
        }

        # Schedule lectures
        for i in range(course.ltpsc["L"]):
            print(f"Scheduling lecture {i+1}/{course.ltpsc['L']} for {course.course_id}")
            slot = self._find_suitable_slot(course, "LECTURE_ROOM")
            if slot:
                course_entry['Timeslots'].append(f"L:{slot}")
            else:
                print(f"Could not find slot for lecture {i+1}")

        # Schedule tutorials
        for i in range(course.ltpsc["T"]):
            print(f"Scheduling tutorial {i+1}/{course.ltpsc['T']} for {course.course_id}")
            slot = self._find_suitable_slot(course, "LECTURE_ROOM")
            if slot:
                course_entry['Timeslots'].append(f"T:{slot}")
            else:
                print(f"Could not find slot for tutorial {i+1}")

        # Schedule practicals
        if course.ltpsc["P"] > 0:
            for batch in course.batches:
                print(f"Scheduling practical for {batch} of {course.course_id}")
                slot = self._find_suitable_slot(course, "COMPUTER_LAB", batch)
                if slot:
                    course_entry['Timeslots'].append(f"P:{slot}")
                else:
                    print(f"Could not find slot for {batch}")

        return course_entry if course_entry['Timeslots'] else None

    def _find_suitable_slot(self, course: Course, room_type: str, batch: str = None) -> str:
        for day in self.days:
            for time in self.time_slots:
                suitable_room = None
                for room in self.rooms.values():
                    # For labs, check against batch size instead of total registered students
                    required_capacity = course.registered_students
                    if room_type == "COMPUTER_LAB":
                        config_key = f"{course.department}_{course.semester}"
                        batch_config = self.batch_configs.get(config_key)
                        if batch_config:
                            required_capacity = batch_config.batch_size
                    
                    if (room.room_type == room_type and 
                        room.capacity >= required_capacity and
                        self.is_room_available(room.room_id, day, time)):
                        suitable_room = room
                        break

                if suitable_room and self.is_faculty_available(course.faculty_name, day, time):
                    self.schedule_slot(suitable_room.room_id, course.faculty_name, day, time)
                    if batch:
                        return f"{day} {time} Lab {batch} {suitable_room.room_id}"
                    return f"{day} {time} {suitable_room.room_id}"
        return None

    def export_to_csv(self, timetable: List[dict], output_file: str):
        if not timetable:
            raise ValueError("No timetable data to export")
            
        headers = [
            'Semester', 'Department', 'Course Code', 'Course Name',
            'Faculty', 'Timeslots'
        ]
        
        try:
            output_path = output_file
            print(f"\nAttempting to write to: {output_path}")
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for entry in timetable:
                    # Convert Timeslots list to comma-separated string
                    entry['Timeslots'] = ','.join(entry['Timeslots'])
                    writer.writerow(entry)
                    
            print(f"\nTimetable successfully exported to {output_path}")
            
            if os.path.exists(output_path):
                print(f"File created successfully at: {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")
            else:
                print("Warning: File was not created!")
                
        except Exception as e:
            print(f"\nError writing to file: {str(e)}")
            raise

    def allocate_room(self, course: Course, day: str, time_slot: str, room_type: str = "LECTURE_ROOM") -> Optional[Room]:
        """Allocate a room based on course requirements and student enrollment."""
        # Get available rooms of the specified type
        available_rooms = [room for room in self.rooms.values() 
                         if room.room_type == room_type and 
                         not self.is_room_occupied(room, day, time_slot)]
        
        if not available_rooms:
            return None
            
        # Sort rooms by capacity to find the most suitable room
        available_rooms.sort(key=lambda x: x.capacity)
        
        # For elective courses, find the smallest room that can accommodate all students
        if course.semester == 6 and course.course_code.startswith(('CSE_CS6', 'ECE_EC6', 'DSAI_DS6')):
            for room in available_rooms:
                if room.capacity >= course.registered_students:
                    return room
            return None  # No suitable room found for elective course
            
        # For regular courses, use department-specific rooms first
        department_rooms = [room for room in available_rooms 
                          if room.department == course.department]
        if department_rooms:
            return department_rooms[0]
            
        # If no department-specific room available, use common rooms
        common_rooms = [room for room in available_rooms 
                       if room.department == "Common"]
        if common_rooms:
            return common_rooms[0]
            
        return None

def main():
    scheduler = TimetableScheduler()
    
    try:
        print("\nStarting scheduler...")
        
        # Define input files
        batch_file = normalize_path(os.path.join(SCRIPT_DIR, 'batch_1.csv'))
        courses_file1 = normalize_path(os.path.join(SCRIPT_DIR, 'courses_1.csv'))
        courses_file2 = normalize_path(os.path.join(SCRIPT_DIR, 'courses.csv'))
        faculty_file1 = normalize_path(os.path.join(SCRIPT_DIR, 'faculty_1.csv'))
        faculty_file2 = normalize_path(os.path.join(SCRIPT_DIR, 'faculty.csv'))
        rooms_file1 = normalize_path(os.path.join(SCRIPT_DIR, 'rooms_1.csv'))
        rooms_file2 = normalize_path(os.path.join(SCRIPT_DIR, 'rooms.csv'))
        
        # Load common data
        print("\nLoading common data...")
        scheduler.load_all_batch_configs(batch_file)
        scheduler.load_all_rooms(rooms_file1, rooms_file2)
        scheduler.load_all_faculty(faculty_file1, faculty_file2)
        
        # Process each semester and combine timetables (excluding semester 1)
        ALL_SEMESTERS = [2, 4, 6, 8]  # Removed semester 1
        combined_timetable = []
        
        for semester in ALL_SEMESTERS:
            print(f"\nProcessing Semester {semester}")
            
            try:
                # Load courses for this semester
                print(f"\nLoading courses for semester {semester}...")
                scheduler.load_all_courses(courses_file1, courses_file2, semester)
                
                # Generate timetable for this semester
                print(f"\nGenerating timetable for semester {semester}...")
                timetable = scheduler.generate_timetable(semester, courses_file1)
                
                # Add to combined timetable
                combined_timetable.extend(timetable)
                
            except Exception as e:
                print(f"\nError processing semester {semester}: {str(e)}")
                continue
        
        # Save combined timetable
        output_file = normalize_path(os.path.join(SCRIPT_DIR, 'combined4_timetable.csv'))
        scheduler.export_to_csv(combined_timetable, output_file)
        print(f"\nCombined timetable saved as {output_file}")
        
        print("\nTimetable generation completed for all semesters!")
        
    except Exception as e:
        print(f"\nError in main execution: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()