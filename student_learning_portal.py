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



# ============================================================
# Everything below uses the classes above
# ============================================================

BIG_LINE = "=" * 40
SMALL_LINE = "-" * 40


def show_title(text):
    """Print a centred title between two big lines."""
    print()
    print(BIG_LINE)
    print(text.center(40))
    print(BIG_LINE)
    print()


def show_box(title, lines):
    """Print a title, then every line given, then a closing line."""
    show_title(title)
    for line in lines:
        print(line)
    print()
    print(BIG_LINE)


def show_error(message):
    """Print a short, friendly error message."""
    print()
    print(f"[!] {message}")


def show_not_found(what, value):
    """Screen shown when an ID does not exist in the dictionary."""
    show_box("RECORD NOT FOUND", [
        f"No {what.lower()} with ID {value} was found.",
        "",
        "Please check the ID and try again.",
    ])


def show_duplicate(field, value, found):
    """Screen shown when an ID is already used. 'found' is the existing object."""
    lines = [f"{field['label']} {value} already exists.", "", f"Existing {field['what']}:"]
    lines = lines + found.detail_lines()
    lines = lines + ["", f"Please enter a different {field['label']}."]
    show_box("DUPLICATE ID", lines)


def show_cancelled():
    """Screen shown after the user cancels. Nothing was saved."""
    show_box("ENTRY CANCELLED", ["Nothing was saved.", "", "Returning to the main menu..."])


def ask_choice(first, last, prompt="Choose: "):
    """Ask for a whole number between first and last. Keeps asking until it is valid."""
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print(f"[!] Please type a number from {first} to {last}.")
            continue
        if number < first or number > last:
            print(f"[!] Please choose a number from {first} to {last}.")
            continue
        return number


def ask_yes_no(question):
    """Ask a Yes/No question. Returns True for Yes."""
    print()
    print(question)
    print()
    print("1. Yes")
    print("2. No")
    print()
    return ask_choice(1, 2) == 1


def confirm_cancel():
    """Ask 'Cancel this entry?'. Returns True only if the user really wants to cancel."""
    print()
    print("Cancel this entry?")
    print()
    print("1. Continue")
    print("2. Cancel")
    print()
    return ask_choice(1, 2) == 2


def ask_lookup(prompt):
    """Ask for an ID. Returns None if the user types BACK or CANCEL."""
    print()
    print("(Type BACK to return to the menu)")
    print(prompt)
    text = input("> ").strip()
    if text.upper() in ("BACK", "CANCEL"):
        return None
    return text.upper()
    # .upper() makes searching case-insensitive (s001 = S001).


def find_record(store, what, prompt):
    """Ask for an ID until the object is found in the dictionary 'store'.
    Returns the object, or None if the user goes back."""
    while True:
        text = ask_lookup(prompt)
        if text is None:
            return None
        if text == "":
            show_error("Please type an ID.")
            continue
        record = store.get(text)
        if record is not None:
            return record
        show_not_found(what, text)