script.js:// Constants
const TIME_SLOTS = [
    "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
    "14:00-15:00", "15:00-16:00", "16:00-17:00"
];

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

// Column name variations
const COLUMN_VARIATIONS = {
    semester: ['semester', 'sem'],
    department: ['department', 'dept'],
    courseCode: ['course code', 'coursecode', 'course_code', 'code'],
    courseName: ['course name', 'coursename', 'course_name', 'name'],
    faculty: ['faculty', 'professor', 'teacher', 'instructor'],
    timeSlot: ['time slot', 'timeslot', 'time_slot', 'time', 'slot'],
    day: ['day', 'weekday']
};

// Global variables
let timetableData = [];
let filteredData = [];

// DOM elements
const fileInput = document.getElementById('csvFile');
const semesterFilter = document.getElementById('semesterFilter');
const departmentFilter = document.getElementById('departmentFilter');
const timetableBody = document.getElementById('timetableBody');
const exportBtn = document.getElementById('exportBtn');
const courseDetails = document.getElementById('courseDetails');
const closeDetails = document.getElementById('closeDetails');
const uploadBtn = document.getElementById('uploadBtn');

// Debug check for DOM elements
console.log('DOM Elements loaded:', {
    fileInput: !!fileInput,
    semesterFilter: !!semesterFilter,
    departmentFilter: !!departmentFilter,
    timetableBody: !!timetableBody,
    uploadBtn: !!uploadBtn
});

// Initialize event listeners
if (fileInput) {
    fileInput.addEventListener('change', handleFileUpload);
    console.log('File input event listener added');
}
if (semesterFilter) semesterFilter.addEventListener('change', filterTimetable);
if (departmentFilter) departmentFilter.addEventListener('change', filterTimetable);
if (exportBtn) exportBtn.addEventListener('click', exportTimetable);
if (closeDetails) closeDetails.addEventListener('click', () => courseDetails.style.display = 'none');
if (uploadBtn) {
    uploadBtn.addEventListener('click', () => {
        console.log('Upload button clicked');
        fileInput.click();
    });
}

// Initialize timetable
function initializeTimetable() {
    console.log('Initializing timetable');
    if (!timetableBody) {
        console.error('Timetable body element not found!');
        return;
    }
    
    timetableBody.innerHTML = ''; // Clear existing content
    TIME_SLOTS.forEach(timeSlot => {
        const timeRow = document.createElement('div');
        timeRow.className = 'time-row';
        
        // Add time slot
        const timeSlotDiv = document.createElement('div');
        timeSlotDiv.className = 'time-slot';
        timeSlotDiv.textContent = timeSlot;
        timeRow.appendChild(timeSlotDiv);
        
        // Add day cells
        DAYS.forEach(() => {
            const dayCell = document.createElement('div');
            dayCell.className = 'day-cell';
            timeRow.appendChild(dayCell);
        });
        
        timetableBody.appendChild(timeRow);
    });
    console.log('Timetable initialized');
}

// Parse CSV row into array handling quoted fields
function parseCSVRow(row) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < row.length; i++) {
        const char = row[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

// Parse a single timeslot
function parseTimeslot(slot, baseData) {
    const match = slot.trim().match(/([LT]):(\w+)\s+(\d{2}:\d{2}-\d{2}:\d{2})\s+(\w+)/);
    if (match) {
        const type = match[1] === 'L' ? 'Lecture' : 'Tutorial';
        const day = match[2].charAt(0).toUpperCase() + match[2].slice(1).toLowerCase();
        const timeSlot = match[3];
        const room = match[4];

        if (DAYS.includes(day) && TIME_SLOTS.includes(timeSlot)) {
            return {
                ...baseData,
                type,
                day,
                timeSlot,
                room
            };
        }
    }
    return null;
}

// Handle file upload
async function handleFileUpload(event) {
    console.log('File upload triggered');
    const file = event.target.files[0];
    if (!file) {
        console.log('No file selected');
        return;
    }
    console.log('File selected:', file.name);

    try {
        const text = await file.text();
        console.log('File content loaded');
        
        const rows = text.split('\n')
            .map(row => row.trim())
            .filter(row => row);
        
        if (rows.length === 0) {
            throw new Error('CSV file is empty');
        }

        // Parse headers
        const headers = parseCSVRow(rows[0]);
        console.log('Headers found:', headers);

        // Find column indices
        const semesterIdx = headers.indexOf('Semester');
        const departmentIdx = headers.indexOf('Department');
        const courseCodeIdx = headers.indexOf('Course Code');
        const courseNameIdx = headers.indexOf('Course Name');
        const facultyIdx = headers.indexOf('Faculty');
        const timeslotsIdx = headers.indexOf('Timeslots');

        // Check for missing columns
        const missingColumns = [];
        if (semesterIdx === -1) missingColumns.push('Semester');
        if (departmentIdx === -1) missingColumns.push('Department');
        if (courseCodeIdx === -1) missingColumns.push('Course Code');
        if (courseNameIdx === -1) missingColumns.push('Course Name');
        if (facultyIdx === -1) missingColumns.push('Faculty');
        if (timeslotsIdx === -1) missingColumns.push('Timeslots');

        if (missingColumns.length > 0) {
            throw new Error('Missing required columns: ' + missingColumns.join(', '));
        }

        // Process the data
        timetableData = [];
        for (let i = 1; i < rows.length; i++) {
            const columns = parseCSVRow(rows[i]);
            if (columns.length <= Math.max(semesterIdx, departmentIdx, courseCodeIdx, courseNameIdx, facultyIdx, timeslotsIdx)) {
                console.warn(Skipping row ${i + 1}: insufficient columns);
                continue;
            }

            const baseData = {
                semester: columns[semesterIdx],
                department: columns[departmentIdx],
                courseCode: columns[courseCodeIdx],
                courseName: columns[courseNameIdx],
                faculty: columns[facultyIdx]
            };

            // Extract timeslots from quoted string
            const timeslotsStr = columns[timeslotsIdx].replace(/^"(.*)"$/, '$1');
            const timeslots = timeslotsStr.split(',').map(slot => slot.trim());

            for (const slot of timeslots) {
                const parsedSlot = parseTimeslot(slot, baseData);
                if (parsedSlot) {
                    timetableData.push(parsedSlot);
                    console.log(Added slot for ${baseData.courseCode} on ${parsedSlot.day} at ${parsedSlot.timeSlot});
                } else {
                    console.warn(Invalid timeslot format: "${slot}" for course ${baseData.courseCode});
                }
            }
        }

        console.log(Processed ${timetableData.length} time slots);
        if (timetableData.length === 0) {
            throw new Error('No valid time slots found in the CSV file');
        }

        // Debug log to check days distribution
        const dayDistribution = timetableData.reduce((acc, curr) => {
            acc[curr.day] = (acc[curr.day] || 0) + 1;
            return acc;
        }, {});
        console.log('Classes distribution by day:', dayDistribution);

        filterTimetable();
    } catch (error) {
        console.error('Error processing file:', error);
        alert('Error processing file: ' + error.message);
    }
}

// Filter timetable based on selected semester and department
function filterTimetable() {
    console.log('Filtering timetable');
    const selectedSemester = semesterFilter.value;
    const selectedDepartment = departmentFilter.value;
    
    filteredData = timetableData.filter(course => {
        const semesterMatch = selectedSemester === 'all' || course.semester === selectedSemester;
        const departmentMatch = selectedDepartment === 'all' || course.department === selectedDepartment;
        return semesterMatch && departmentMatch;
    });
    
    console.log(Filtered to ${filteredData.length} entries);
    renderTimetable();
}

// Render timetable with filtered data
function renderTimetable() {
    console.log('Rendering timetable');
    // Clear existing course slots
    document.querySelectorAll('.course-slot').forEach(slot => slot.remove());
    
    // Add filtered courses to timetable
    filteredData.forEach(course => {
        const timeIndex = TIME_SLOTS.indexOf(course.timeSlot);
        const dayIndex = DAYS.indexOf(course.day);
        
        console.log(Placing course ${course.courseCode} on ${course.day} at ${course.timeSlot} (indices: ${timeIndex}, ${dayIndex}));
        
        if (timeIndex !== -1 && dayIndex !== -1) {
            const timeRow = timetableBody.children[timeIndex];
            if (timeRow) {
                const dayCell = timeRow.children[dayIndex + 1]; // +1 for time slot column
                if (dayCell) {
                    const courseSlot = createCourseElement(course);
                    dayCell.appendChild(courseSlot);
                }
            }
        } else {
            console.warn(Invalid indices for course ${course.courseCode}: time=${timeIndex}, day=${dayIndex});
        }
    });
}

// Create course element
function createCourseElement(course) {
    const courseSlot = document.createElement('div');
    courseSlot.className = course-slot ${course.department.toLowerCase()};
    
    const courseCode = document.createElement('div');
    courseCode.className = 'course-code';
    courseCode.textContent = course.courseCode;
    
    const faculty = document.createElement('div');
    faculty.className = 'faculty';
    faculty.textContent = course.faculty;
    
    const type = document.createElement('div');
    type.className = 'type';
    type.textContent = course.type;
    
    courseSlot.appendChild(courseCode);
    courseSlot.appendChild(faculty);
    courseSlot.appendChild(type);
    
    courseSlot.addEventListener('click', () => showCourseDetails(course));
    
    return courseSlot;
}

// Show course details
function showCourseDetails(course) {
    const detailsContent = document.querySelector('.details-content');
    detailsContent.innerHTML = `
        <p><strong>Course Code:</strong> ${course.courseCode}</p>
        <p><strong>Course Name:</strong> ${course.courseName}</p>
        <p><strong>Faculty:</strong> ${course.faculty}</p>
        <p><strong>Department:</strong> ${course.department}</p>
        <p><strong>Semester:</strong> ${course.semester}</p>
        <p><strong>Type:</strong> ${course.type}</p>
        <p><strong>Time:</strong> ${course.timeSlot}</p>
        <p><strong>Day:</strong> ${course.day}</p>
        <p><strong>Room:</strong> ${course.room}</p>
    `;
    
    courseDetails.style.display = 'block';
}

// Export timetable
function exportTimetable() {
    if (filteredData.length === 0) {
        alert('No data to export. Please load a timetable first.');
        return;
    }

    const selectedSemester = semesterFilter.value;
    const selectedDepartment = departmentFilter.value;
    
    let filename = 'timetable';
    if (selectedSemester !== 'all') filename += _sem${selectedSemester};
    if (selectedDepartment !== 'all') filename += _${selectedDepartment};
    filename += '.csv';
    
    const csvContent = [
        ['Semester', 'Department', 'Course Code', 'Course Name', 'Faculty', 'Type', 'Day', 'Time Slot', 'Room'].join(','),
        ...filteredData.map(course => [
            course.semester,
            course.department,
            course.courseCode,
            course.courseName,
            course.faculty,
            course.type,
            course.day,
            course.timeSlot,
            course.room
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize the timetable when the page loads
document.addEventListener('DOMContentLoaded', initializeTimetable);