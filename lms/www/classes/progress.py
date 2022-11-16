import frappe
from lms.lms.utils import has_course_moderator_role
from frappe import _

def get_context(context):
	context.no_cache = 1

	if not has_course_moderator_role():
		message = "Only Moderators have access to this page."
		if frappe.session.user == "Guest":
			message = "Please login to access this page."

		raise frappe.PermissionError(_(message))

	student = frappe.form_dict["username"]
	classname = frappe.form_dict["classname"]

	context.student = frappe.db.get_value("User", {"username": student}, ["first_name", "full_name", "name"], as_dict=True)
	context.class_info = frappe.db.get_value("LMS Class", classname, ["name"], as_dict=True)

	class_courses = frappe.get_all("Class Course", {
		"parent": classname
	}, ["course", "title"])

	for course in class_courses:
		course.membership = frappe.db.get_value("LMS Batch Membership", {
			"member": context.student.name,
			"course": course.course
		}, ["progress"], as_dict=True)
		course.quizzes = frappe.get_all("LMS Quiz", {"course": course.course}, ["name", "title"])
		course.assignments = frappe.get_all("Course Lesson", {"course": course.course, "question": ["is", "set"]}, ["name", "title"])

	context.class_courses = class_courses
