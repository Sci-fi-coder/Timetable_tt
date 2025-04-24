styles.css::root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --background-color: #f5f6fa;
    --text-color: #2c3e50;
    --border-color: #dcdde1;
    --hover-color: #f1f2f6;
    
    /* Course colors */
    --cs-color: #e74c3c;
    --ec-color: #3498db;
    --ds-color: #2ecc71;
    --ii-color: #9b59b6;
    --other-color: #95a5a6;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}

body {
    background-color: #f5f6fa;
    color: #2c3e50;
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

header h1 {
    font-size: 2em;
    color: #2c3e50;
    margin-bottom: 20px;
}

.controls {
    display: flex;
    gap: 15px;
    align-items: center;
    flex-wrap: wrap;
}

select, button {
    padding: 10px 15px;
    border: 1px solid #dcdde1;
    border-radius: 5px;
    font-size: 1em;
    background-color: #fff;
    cursor: pointer;
    transition: all 0.3s ease;
}

select:hover, button:hover {
    border-color: #2c3e50;
}

button {
    background-color: #2c3e50;
    color: #fff;
    border: none;
    display: flex;
    align-items: center;
    gap: 8px;
}

button:hover {
    background-color: #34495e;
}

.timetable-container {
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow-x: auto;
}

.timetable-header {
    display: grid;
    grid-template-columns: 100px repeat(5, 1fr);
    background-color: #2c3e50;
    color: #fff;
    font-weight: 500;
}

.time-row {
    display: grid;
    grid-template-columns: 100px repeat(5, 1fr);
    border-bottom: 1px solid #dcdde1;
}

.time-slot, .day {
    padding: 15px;
    text-align: center;
    font-weight: 500;
}

.day-cell {
    padding: 10px;
    min-height: 80px;
    border-left: 1px solid #dcdde1;
    position: relative;
}

.course-slot {
    background-color: #fff;
    border-radius: 5px;
    padding: 10px;
    margin: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.course-slot:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.course-slot.cse {
    border-left: 4px solid #3498db;
}

.course-slot.ece {
    border-left: 4px solid #e74c3c;
}

.course-slot.dsai {
    border-left: 4px solid #2ecc71;
}

.course-code {
    font-weight: 500;
    font-size: 0.9em;
    margin-bottom: 5px;
}

.faculty {
    font-size: 0.8em;
    color: #7f8c8d;
}

/* Course details styles */
.course-details {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    max-width: 500px;
    width: 90%;
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #dcdde1;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.2em;
    color: #7f8c8d;
    cursor: pointer;
    padding: 5px;
}

.close-btn:hover {
    color: #2c3e50;
}

.details-content p {
    margin-bottom: 10px;
}

.details-content strong {
    color: #2c3e50;
}

/* Responsive styles */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    header {
        padding: 15px;
    }
    
    .controls {
        flex-direction: column;
        align-items: stretch;
    }
    
    .time-slot, .day {
        padding: 10px;
        font-size: 0.9em;
    }
    
    .course-slot {
        padding: 8px;
    }
    
    .course-code {
        font-size: 0.8em;
    }
    
    .faculty {
        font-size: 0.7em;
    }
}