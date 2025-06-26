from django.contrib import admin
from .models import (
    Course,
    CourseMember,
    CourseContent,
    Comment,
    Profile,
    Announcement,
    CompletionTracking,
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "description", "teacher", "created_at"]
    list_filter  = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "price", "image", "teacher", "created_at", "updated_at"]

@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ["course_id", "user_id", "roles", "created_at"]
    list_filter  = ["roles"]
    search_fields = ["user_id__username", "course_id__name"]

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["name", "course_id", "created_at"]
    list_filter  = ["course_id"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["content_id", "member_id", "comment", "created_at"]
    list_filter  = ["member_id__roles"]
    search_fields = ["comment"]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "handphone", "description"]
    search_fields = ["user__username", "handphone"]

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["course", "title", "publish_date", "created_at"]
    list_filter  = ["course"]
    search_fields = ["title", "message"]

@admin.register(CompletionTracking)
class CompletionTrackingAdmin(admin.ModelAdmin):
    list_display = ["user", "content", "completed_at"]
    list_filter  = ["user"]
    search_fields = ["content__name"]
