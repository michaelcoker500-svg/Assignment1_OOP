class Course:  # A class is a blueprint. Course is the blueprint for any course.
    total_courses = 0  # Class attribute: ONE value shared by ALL Course objects.

    def __init__(self, course_code, title, total_lessons):
        self.course_code = course_code
        self.title = title
        self.total_lessons = total_lessons
        Course.total_courses += 1

    def describe(self):
        return f"{self.course_code} - {self.title} ({self.total_lessons} lessons)"

    def detail_lines(self):
        return [f"Course Code : {self.course_code}",
                f"Title       : {self.title}",
                f"Lessons     : {self.total_lessons}"]

    @classmethod
    def from_string(cls, text):
        code, title, lessons = text.split(",")
        return cls(code.strip().upper(), title.strip(), int(lessons))

    @classmethod
    def count_courses(cls):
        return cls.total_courses


class Student:
    total_students = 0

    def __init__(self, student_id, Fullname):
        self.student_id = student_id
        self.Fullname = Fullname
        Student.total_students += 1

    def describe(self):  # INSTANCE METHOD
        return f"{self.student_id} ({self.Fullname})"

    def detail_lines(self):  # INSTANCE METHOD
        return [f"ID       : {self.student_id}",
                f"Fullname : {self.Fullname}"]

    @classmethod
    def from_string(cls, text):
        student_id, Fullname = text.split(",")
        return cls(student_id.strip().upper(), Fullname.strip())

    @classmethod
    def count_students(cls):  # CLASS METHOD
        return cls.total_students


class Enrollment:
    def __init__(self, enrollment_id, student, course):
        self.enrollment_id = enrollment_id
        self.student = student
        self.course = course
        self.lessons_completed = 0

    def complete_lesson(self):
        if self.lessons_completed < self.course.total_lessons:
            self.lessons_completed += 1
            return True  # It worked.
        return False  # The course was already finished.

    def is_finished(self):
        return self.lessons_completed >= self.course.total_lessons

    def progress_percent(self):
        return (self.lessons_completed / self.course.total_lessons) * 100

    def status_text(self):
        return "Finished" if self.is_finished() else "In Progress"

    def detail_lines(self):
        return [f"Enrollment ID : {self.enrollment_id}",
                "",
                f"Student ID    : {self.student.student_id}",
                f"Student       : {self.student.Fullname}",
                "",
                f"Course Code   : {self.course.course_code}",
                f"Course Title  : {self.course.title}",
                "",
                f"Lessons       : {self.lessons_completed} / {self.course.total_lessons}",
                f"Progress      : {self.progress_percent():.0f}%",
                f"Status        : {self.status_text()}"]


class Portal:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.enrollments = {}

    # ADD functions (each one protects against duplicate IDs)
    def add_student(self, student):
        if student.student_id in self.students:
            return False
        self.students[student.student_id] = student
        return True

    def add_course(self, course):
        if course.course_code in self.courses:
            return False
        self.courses[course.course_code] = course
        return True

    def next_enrollment_id(self):
        number = len(self.enrollments) + 1
        while f"E{number:03d}" in self.enrollments:
            number += 1
        return f"E{number:03d}"

    def find_enrollment_for(self, student, course):
        for enrollment in self.enrollments.values():
            if (enrollment.student.student_id == student.student_id
                    and enrollment.course.course_code == course.course_code):
                return enrollment
        return None

    def add_enrollment(self, student, course):
        if self.find_enrollment_for(student, course) is not None:
            return None
        new_id = self.next_enrollment_id()
        enrollment = Enrollment(new_id, student, course)
        self.enrollments[new_id] = enrollment
        return enrollment

    def save_enrollment_draft(self, draft):
        """Called ONLY after the user chose SAVE. This is where objects are really created."""
        student = draft["student_id_obj"]  # Reuse the existing student if there is one...
        if student is None:  # ...otherwise create a new Student object now.
            student = Student(draft["student_id"], draft["Fullname"])
            self.add_student(student)
        course = draft["course_code_obj"]
        if course is None:
            course = Course(draft["course_code"], draft["course_title"], draft["lessons"])
            self.add_course(course)
        return self.add_enrollment(student, course)

    # DISPLAY / SEARCH
    def show_enrollments(self, student_id=None, course_code=None, status=None):
        """Print every enrollment that matches the filters. Returns how many were printed."""
        count = 0
        for enrollment in self.enrollments.values():
            if student_id is not None and enrollment.student.student_id != student_id:
                continue
            if course_code is not None and enrollment.course.course_code != course_code:
                continue
            if status == "finished" and not enrollment.is_finished():
                continue
            if status == "in_progress" and enrollment.is_finished():
                continue
            show_box("ENROLLMENT", enrollment.detail_lines())
            count += 1
        return count
