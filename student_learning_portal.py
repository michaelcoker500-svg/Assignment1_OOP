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




# CHECK FUNCTIONS
def check_id(text, draft):
    value = text.upper()
    if " " in value:
        return None, "An ID cannot contain spaces."
    if len(value) > 10:
        return None, "An ID can have at most 10 characters."
    return value, None


def check_text(text, draft):
    if len(text) > 30:
        return None, "Please use 30 characters or fewer."
    return text, None


def check_long_text(text, draft):
    if len(text) > 60:
        return None, "Please use 60 characters or fewer."
    return text, None


def check_positive_number(text, draft):
    try:
        number = int(text)
    except ValueError:
        return None, "Please type a whole number (for example 5)."
    if number <= 0:
        return None, "The number must be above 0."
    if number > 1000:
        return None, "That number is too large."
    return number, None


def is_skipped(field, draft):
    """A question is skipped when its parent ID matched an existing object."""
    parent = field.get("skip_if_found")
    if parent is None:
        return False
    return draft.get(parent + "_obj") is not None


def handle_id_answer(field, value, draft):
    """Look the ID up in the dictionary BEFORE any object is created.
    Returns True if the answer is accepted, False if the question must be asked again."""
    found = field["store"].get(value)
    key = field["key"] + "_obj"
    mode = field["mode"]

    if mode == "reject":
        if found is not None:
            show_duplicate(field, value, found)
            return False
        draft[key] = None
        return True

    if mode == "must_exist":
        if found is None:
            show_not_found(field["what"], value)
            return False
        draft[key] = found
        return True

    # mode == "reuse": use the existing object instead of making a second one.
    if found is None:
        draft[key] = None
        return True
    show_box(f"{field['what'].upper()} FOUND", found.detail_lines())
    print()
    print(f"1. Use this {field['what'].lower()}")
    print("2. Enter a different ID")
    print()
    if ask_choice(1, 2) == 2:
        return False
    draft[key] = found
    return True


def ask_one_field(field, draft, fields):
    """Ask ONE question. Returns 'ok', 'back' or 'cancel'."""
    visible = [f for f in fields if not is_skipped(f, draft)]
    number = visible.index(field) + 1 if field in visible else 1
    while True:
        print()
        print(SMALL_LINE)
        print(f"Step {number} of {len(visible)}")
        if "hint" in field:
            print(field["hint"])
        current = draft.get(field["key"])
        if current is None:
            print(f"{field['label']}:")
        else:
            print(f"{field['label']} (press Enter to keep: {current}):")
        text = input("> ").strip()

        if text.upper() == "BACK":
            return "back"
        if text.upper() == "CANCEL":
            if confirm_cancel():
                return "cancel"
            continue
        if text == "":
            if current is not None:
                return "ok"
            show_error("This cannot be empty.")
            continue

        value, error = field["check"](text, draft)
        if error is not None:
            show_error(error)
            continue
        if "store" in field and not handle_id_answer(field, value, draft):
            continue
        draft[field["key"]] = value
        return "ok"


def missing_answers(fields, draft):
    """List the questions that still have no answer."""
    problems = []
    for field in fields:
        if not is_skipped(field, draft) and field["key"] not in draft:
            problems.append(f"{field['label']} has not been entered.")
    return problems


def run_entry(title, fields, draft, review_lines, find_problems, system):
    """Run a whole data-entry form. Returns 'save', 'cancel' or 'back'.
    The caller creates the object ONLY when this returns 'save'."""
    position = 0
    direction = 1
    show_title(title)
    print("Tip: type BACK for the previous question,")
    print("     or CANCEL to discard this entry.")

    while True:
        # ask the questions one by one
        while 0 <= position < len(fields):
            field = fields[position]
            if is_skipped(field, draft):
                position += direction
                continue
            result = ask_one_field(field, draft, fields)
            if result == "cancel":
                return "cancel"
            if result == "back":
                direction = -1
                position -= 1
            else:
                direction = 1
                position += 1

        if position < 0:
            return "back"

        # review screen
        while True:
            editable = [f for f in fields if not is_skipped(f, draft)]
            show_box("REVIEW RECORD", review_lines(draft))
            print()
            print("1. Save record")
            number = 2
            for field in editable:
                print(f"{number}. Edit {field['label']}")
                number += 1
            cancel_number = number
            back_number = number + 1
            print(f"{cancel_number}. Cancel")
            print(f"{back_number}. Back")
            print()
            choice = ask_choice(1, back_number)

            if choice == 1:  # SAVE: validate first.
                problems = missing_answers(fields, draft)
                if not problems:
                    problems = find_problems(system, draft)
                if problems:
                    show_box("CANNOT SAVE YET", ["Please fix this first:", ""] + problems)
                    continue
                return "save"
            elif choice == cancel_number:
                if confirm_cancel():
                    return "cancel"
            elif choice == back_number:
                position = len(fields) - 1
                direction = -1
                break
            else:
                field = editable[choice - 2]
                if ask_one_field(field, draft, fields) == "cancel":
                    return "cancel"
                for other in fields:
                    if not is_skipped(other, draft) and other["key"] not in draft:
                        if ask_one_field(other, draft, fields) == "cancel":
                            return "cancel"


def finish_entry(result, saved_title, saved_lines):
    """Show the right screen after run_entry. Call this AFTER saving."""
    if result == "save":
        show_box(saved_title, saved_lines)
    elif result == "cancel":
        show_cancelled()
    else:
        print()
        print("Returning to the main menu...")


def enrollment_review_lines(draft):
    """Lines for the review screen. Uses .get() so missing answers do not crash."""
    student = draft.get("student_id_obj")
    course = draft.get("course_code_obj")
    if student is not None:
        Fullname = student.Fullname + "  (existing student)"
    else:
        Fullname = draft.get("Fullname", "(not entered)")
    if course is not None:
        title = course.title + "  (existing course)"
        lessons = course.total_lessons
    else:
        title = draft.get("course_title", "(not entered)")
        lessons = draft.get("lessons", "(not entered)")
    return [f"Student ID    : {draft.get('student_id', '(not entered)')}",
            f"FullName      : {Fullname}",
            f"Course Code   : {draft.get('course_code', '(not entered)')}",
            f"Course Title  : {title}",
            f"Lessons       : {lessons}"]


def enrollment_problems(portal, draft):
    """Final validation just before saving."""
    problems = []
    student = draft.get("student_id_obj")
    course = draft.get("course_code_obj")
    if student is not None and course is not None:
        if portal.find_enrollment_for(student, course) is not None:
            problems.append("This student is already enrolled in this course.")
            problems.append("Edit the Student ID or the Course Code.")
    return problems


def enroll_student(portal):
    draft = {}  # TEMPORARY storage.
    fields = [
        {"key": "student_id", "label": "Student ID", "check": check_id,
         "store": portal.students, "what": "Student", "mode": "reuse"},
        {"key": "Fullname", "label": "Fullname", "check": check_text, "skip_if_found": "student_id"},
        {"key": "course_code", "label": "Course Code", "check": check_id,
         "store": portal.courses, "what": "Course", "mode": "reuse"},
        {"key": "course_title", "label": "Course Title", "check": check_text, "skip_if_found": "course_code"},
        {"key": "lessons", "label": "Number of Lessons", "check": check_positive_number,
         "skip_if_found": "course_code"},
    ]
    result = run_entry("ADD NEW ENROLLMENT", fields, draft,
                       enrollment_review_lines, enrollment_problems, portal)
    if result == "save":
        enrollment = portal.save_enrollment_draft(draft)  # Objects are created and stored HERE.
        finish_entry(result, "ENROLLMENT SAVED", ["Saved successfully.", ""] + enrollment.detail_lines())
    else:
        finish_entry(result, "", [])  # The draft is simply thrown away.


def view_all_enrollments(portal):
    count = portal.show_enrollments()
    if count == 0:
        show_box("NO RECORDS", ["There are no enrollments yet."])
    else:
        print(f"\nTotal enrollments shown: {count}")


def complete_lesson(portal):
    enrollment = find_record(portal.enrollments, "Enrollment", "Enrollment ID (example E001):")
    if enrollment is None:
        return
    if enrollment.complete_lesson():  # Instance method changes THIS object only.
        show_box("LESSON COMPLETED", enrollment.detail_lines())
    else:
        show_box("ALREADY FINISHED", ["This course is already finished.", ""] + enrollment.detail_lines())


def view_enrollment(portal):
    enrollment = find_record(portal.enrollments, "Enrollment", "Enrollment ID (example E001):")
    if enrollment is not None:
        show_box("ENROLLMENT", enrollment.detail_lines())


def search_by_enrollment_id(portal):
    """Partial search: 'E00' finds E001, E002 ..."""
    text = ask_lookup("Type part of an enrollment ID (example E00):")
    if text is None:
        return
    count = 0
    for enrollment_id, enrollment in portal.enrollments.items():
        if text in enrollment_id:
            show_box("ENROLLMENT", enrollment.detail_lines())
            count += 1
    if count == 0:
        show_box("NO MATCHES", [f"No enrollment ID contains '{text}'."])


def search_by_student(portal):
    student = find_record(portal.students, "Student", "Student ID (example S001):")
    if student is None:
        return
    show_box("STUDENT", student.detail_lines())
    if portal.show_enrollments(student_id=student.student_id) == 0:
        print("\nThis student has no enrollments yet.")


def search_by_course(portal):
    course = find_record(portal.courses, "Course", "Course code (example PY101):")
    if course is None:
        return
    show_box("COURSE", course.detail_lines())
    if portal.show_enrollments(course_code=course.course_code) == 0:
        print("\nNobody is enrolled in this course yet.")


def view_by_status(portal, status, title):
    if portal.show_enrollments(status=status) == 0:
        show_box("NO RECORDS", [f"No {title} found."])


def show_statistics(portal):
    finished = 0
    total_progress = 0
    for enrollment in portal.enrollments.values():
        total_progress += enrollment.progress_percent()
        if enrollment.is_finished():
            finished += 1
    total = len(portal.enrollments)
    average = total_progress / total if total > 0 else 0  # Avoid dividing by zero.
    show_box("PORTAL STATISTICS", [
        f"Students         : {len(portal.students)}",
        f"Courses          : {len(portal.courses)}",
        f"Enrollments      : {total}",
        "",
        f"Finished         : {finished}",
        f"In Progress      : {total - finished}",
        "",
        f"Average Progress : {average:.0f}%",
        "",
        "Created in this run (class methods):",
        f"Student objects  : {Student.count_students()}",
        f"Course objects   : {Course.count_courses()}",
    ])


def remove_enrollment(portal):
    enrollment = find_record(portal.enrollments, "Enrollment", "Enrollment ID to remove (example E003):")
    if enrollment is None:
        return
    show_box("REMOVE ENROLLMENT", enrollment.detail_lines())
    if ask_yes_no("Are you sure you want to remove this enrollment?"):
        del portal.enrollments[enrollment.enrollment_id]  # Remove the key and its object.
        print(f"\nEnrollment {enrollment.enrollment_id} removed successfully.")
    else:
        print("\nRemoval cancelled.")


def show_main_menu():
    show_title("STUDENT LEARNING PORTAL")
    print("1. View all enrollments")
    print("2. Enroll student")
    print("3. Complete lesson")
    print("4. View enrollment details")
    print("5. Search by enrollment ID")
    print("6. Search by student ID")
    print("7. Search by course code")
    print("8. View completed courses")
    print("9. View courses in progress")
    print("10. Show statistics")
    print("11. Remove enrollment")
    print("0. Exit")
    print()
    print(BIG_LINE)


def load_sample_data(portal):
    """Fictional starting data (no real people)."""
    for text in ("S001, Ama", "S002, Kofi", "S003, Musa", "S004, Fatmata"):
        portal.add_student(Student.from_string(text))  # Class method creates the object.
    for text in ("PY101, Intro to Python, 5", "MTH102, Basic Algebra, 4", "ENG103, Study Skills, 3"):
        portal.add_course(Course.from_string(text))
    first = portal.add_enrollment(portal.students["S001"], portal.courses["PY101"])
    second = portal.add_enrollment(portal.students["S002"], portal.courses["PY101"])
    third = portal.add_enrollment(portal.students["S002"], portal.courses["MTH102"])
    fourth = portal.add_enrollment(portal.students["S003"], portal.courses["ENG103"])
    for _ in range(2):
        first.complete_lesson()
    for _ in range(4):
        third.complete_lesson()
    for _ in range(3):
        fourth.complete_lesson()
    second.complete_lesson()


def main():
    portal = Portal()  # The manager object with empty dictionaries.
    load_sample_data(portal)
    try:
        while True:
            show_main_menu()
            choice = ask_choice(0, 11, "Choose an option: ")
            if choice == 1:
                view_all_enrollments(portal)
            elif choice == 2:
                enroll_student(portal)
            elif choice == 3:
                complete_lesson(portal)
            elif choice == 4:
                view_enrollment(portal)
            elif choice == 5:
                search_by_enrollment_id(portal)
            elif choice == 6:
                search_by_student(portal)
            elif choice == 7:
                search_by_course(portal)
            elif choice == 8:
                view_by_status(portal, "finished", "completed courses")
            elif choice == 9:
                view_by_status(portal, "in_progress", "courses in progress")
            elif choice == 10:
                show_statistics(portal)
            elif choice == 11:
                remove_enrollment(portal)
            else:
                print("\nGoodbye!")
                break
    except (EOFError, KeyboardInterrupt):
        print("\n\nProgram closed. Goodbye!")


if __name__ == "__main__":
    main()