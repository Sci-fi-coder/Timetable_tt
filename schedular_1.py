import csv
import os
from datetime import datetime

# Constants
DEPARTMENTS = ["CSE", "ECE", "DSAI"]
SECTIONS = ["A", "B"]
SEMESTERS = [1, 2, 3, 4, 6, 8]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIME_SLOTS = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", 
              "14:00-15:00", "15:00-16:00", "16:00-17:00"]

# Get the current directory where the script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Course:
    def __init__(self, code, name, department, semester, l, t, p, s, c, students):
        self.code = code
        self.name = name
        self.department = department
        self.semester = int(semester)
        self.l = int(l) if l else 0
        self.t = int(t) if t else 0
        self.p = int(p) if p else 0
        self.s = int(s) if s else 0
        self.c = int(c) if c else 0
        self.students = int(students)
        self.faculty = None
        self.schedule = []

class Faculty:
    def __init__(self, name, department, course_code, preferred_slots):
        self.name = name
        self.department = department
        self.course_code = course_code
        self.preferred_slots = preferred_slots.split(',') if preferred_slots else []
        self.schedule = {}  # day -> list of time slots

class Room:
    def __init__(self, room_id, room_number, capacity, room_type):
        self.room_id = room_id
        self.room_number = room_number
        self.capacity = int(capacity)
        self.room_type = room_type
        self.schedule = {}  # day -> list of time slots

class BatchConfig:
    def __init__(self, department, semester, total_students, sections, batch_size):
        self.department = department
        self.semester = int(semester)
        self.total_students = int(total_students)
        self.sections = int(sections)
        self.batch_size = int(batch_size)

class Scheduler:
    def __init__(self):
        self.courses = {}  # code -> Course
        self.faculty = {}  # name -> Faculty
        self.rooms = {}    # room_id -> Room
        self.batch_configs = {}  # dept_sem -> BatchConfig
        self.timetables = {}  # dept_section -> list of scheduled courses

    def load_data(self):
        """Load all data from CSV files"""
        self.load_batch_configs()
        self.load_courses()
        self.load_faculty()
        self.load_rooms()
        self.assign_faculty_to_courses()

    def load_batch_configs(self):
        """Load batch configurations from batch_1.csv"""
        batch_file = os.path.join(CURRENT_DIR, "batch_1.csv")
        try:
            with open(batch_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    config = BatchConfig(
                        department=row['Department'],
                        semester=row['Semester'],
                        total_students=row['Total_Students'],
                        sections=row['Sections'],
                        batch_size=row['BatchSize']
                    )
                    key = f"{config.department}_{config.semester}"
                    self.batch_configs[key] = config
                    print(f"Loaded batch config: {config.department} Semester {config.semester}")
        except Exception as e:
            print(f"Error loading batch configs: {str(e)}")

    def load_courses(self):
        """Load courses from courses_1.csv"""
        course_file = os.path.join(CURRENT_DIR, "courses_1.csv")
        try:
            with open(course_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    course = Course(
                        code=row['Course Code'],
                        name=row['Course Name'],
                        department=row['Department'],
                        semester=row['Semester'],
                        l=row['L'],
                        t=row['T'],
                        p=row['P'],
                        s=row['S'],
                        c=row['C'],
                        students=row['Registered Students']
                    )
                    self.courses[course.code] = course
                    print(f"Loaded course: {course.code} - {course.name}")
        except Exception as e:
            print(f"Error loading courses: {str(e)}")

    def load_faculty(self):
        """Load faculty from final_faculty_121.csv"""
        faculty_file = os.path.join(CURRENT_DIR, "final_faculty_121.csv")
        try:
            with open(faculty_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Faculty Name'] == '-':
                        continue
                    faculty = Faculty(
                        name=row['Faculty Name'],
                        department=row['Department'],
                        course_code=row['Course Code'],
                        preferred_slots=row['Preferred Time Slots']
                    )
                    self.faculty[faculty.name] = faculty
                    print(f"Loaded faculty: {faculty.name}")
        except Exception as e:
            print(f"Error loading faculty: {str(e)}")

    def load_rooms(self):
        """Load rooms from rooms_1.csv"""
        room_file = os.path.join(CURRENT_DIR, "rooms_1.csv")
        try:
            with open(room_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room = Room(
                        room_id=row['Room ID'],
                        room_number=row['Room Number'],
                        capacity=row['Capacity'],
                        room_type=row['Room Type']
                    )
                    self.rooms[room.room_id] = room
                    print(f"Loaded room: {room.room_id} - {room.room_number}")
        except Exception as e:
            print(f"Error loading rooms: {str(e)}")

    def assign_faculty_to_courses(self):
        """Assign faculty to courses based on course code"""
        for faculty in self.faculty.values():
            if faculty.course_code and faculty.course_code in self.courses:
                self.courses[faculty.course_code].faculty = faculty.name
                print(f"Assigned {faculty.name} to {faculty.course_code}")

    def is_faculty_available(self, faculty_name, day, time_slot):
        """Check if faculty is available at the given day and time slot"""
        if faculty_name not in self.faculty:
            return False
        
        faculty = self.faculty[faculty_name]
        if day not in faculty.schedule:
            faculty.schedule[day] = []
            return True
        
        return time_slot not in faculty.schedule[day]

    def is_room_available(self, room_id, day, time_slot):
        """Check if room is available at the given day and time slot"""
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        if day not in room.schedule:
            room.schedule[day] = []
            return True
        
        return time_slot not in room.schedule[day]

    def schedule_course(self, course, section, day, time_slot, room_id):
        """Schedule a course at the given day, time slot and room"""
        # Update faculty schedule
        if course.faculty:
            if day not in self.faculty[course.faculty].schedule:
                self.faculty[course.faculty].schedule[day] = []
            self.faculty[course.faculty].schedule[day].append(time_slot)
        
        # Update room schedule
        if day not in self.rooms[room_id].schedule:
            self.rooms[room_id].schedule[day] = []
        self.rooms[room_id].schedule[day].append(time_slot)
        
        # Update course schedule
        course.schedule.append({
            'day': day,
            'time': time_slot,
            'room': room_id,
            'section': section
        })
        
        print(f"Scheduled {course.code} for {section} on {day} at {time_slot} in {room_id}")

    def find_suitable_slot(self, course, section):
        """Find a suitable day, time slot and room for a course"""
        for day in DAYS:
            for time_slot in TIME_SLOTS:
                # Check if faculty is available
                if course.faculty and not self.is_faculty_available(course.faculty, day, time_slot):
                    continue
                
                # Find suitable room
                for room in self.rooms.values():
                    if room.capacity >= course.students and self.is_room_available(room.room_id, day, time_slot):
                        # Found a suitable slot
                        return day, time_slot, room.room_id
        
        return None, None, None

    def generate_timetables(self):
        """Generate timetables for all departments and sections"""
        for department in DEPARTMENTS:
            for section in SECTIONS:
                key = f"{department}_{section}"
                self.timetables[key] = []
                
                # Get courses for this department
                dept_courses = [c for c in self.courses.values() if c.department == department]
                
                # Schedule each course
                for course in dept_courses:
                    # Check if this department has multiple sections in this semester
                    config_key = f"{department}_{course.semester}"
                    if config_key in self.batch_configs and self.batch_configs[config_key].sections > 1:
                        # Schedule for this specific section
                        day, time_slot, room_id = self.find_suitable_slot(course, section)
                        if day and time_slot and room_id:
                            self.schedule_course(course, section, day, time_slot, room_id)
                            
                            # Add to timetable
                            self.timetables[key].append({
                                'Semester': course.semester,
                                'Department': department,
                                'Section': section,
                                'Course Code': course.code,
                                'Course Name': course.name,
                                'Faculty': course.faculty or "TBD",
                                'Day': day,
                                'Time': time_slot,
                                'Room': room_id
                            })
                    else:
                        # Only one section, schedule for section A only
                        if section == "A":
                            day, time_slot, room_id = self.find_suitable_slot(course, section)
                            if day and time_slot and room_id:
                                self.schedule_course(course, section, day, time_slot, room_id)
                                
                                # Add to timetable
                                self.timetables[key].append({
                                    'Semester': course.semester,
                                    'Department': department,
                                    'Section': section,
                                    'Course Code': course.code,
                                    'Course Name': course.name,
                                    'Faculty': course.faculty or "TBD",
                                    'Day': day,
                                    'Time': time_slot,
                                    'Room': room_id
                                })

    def export_timetables(self):
        """Export timetables to CSV files"""
        for key, timetable in self.timetables.items():
            if not timetable:
                continue
                
            department, section = key.split('_')
            filename = f"timetable_{department}_section{section}.csv"
            filepath = os.path.join(CURRENT_DIR, filename)
            
            headers = ['Semester', 'Department', 'Section', 'Course Code', 'Course Name', 
                      'Faculty', 'Day', 'Time', 'Room']
            
            try:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(timetable)
                print(f"Exported timetable to {filename}")
            except Exception as e:
                print(f"Error exporting timetable to {filename}: {str(e)}")

def main():
    print(f"Starting scheduler at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {CURRENT_DIR}")
    
    # Create scheduler
    scheduler = Scheduler()
    
    # Load data
    print("\nLoading data...")
    scheduler.load_data()
    
    # Generate timetables
    print("\nGenerating timetables...")
    scheduler.generate_timetables()
    
    # Export timetables
    print("\nExporting timetables...")
    scheduler.export_timetables()
    
    print(f"\nScheduler completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
