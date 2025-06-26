from ninja import NinjaAPI, Router
from ninja.responses import Response
from django.utils import timezone
from django.contrib.auth.models import User

from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

from typing import List
from lms_core.schema import (
    RegisterInput, RegisterOutput,
    BatchEnrollInput, BatchEnrollOutput,
    AnnouncementIn, AnnouncementOut,
    CompletionInput, CompletionOut,
    ProfileOut, ProfileEditInput,
    CategoryIn, CategoryOut,
    BookmarkIn, BookmarkOut,
    FeedbackIn, FeedbackOut,
    DashboardOut, CourseAnalyticsOut,
    CourseContentMini,
)
from lms_core.models import (
    Course, CourseMember, CourseContent, Comment,
    Profile, Announcement, CompletionTracking,
    Category, Bookmark, Feedback
)

apiv1 = NinjaAPI()
auth = HttpJwtAuth()


# ─── AUTH ─────────────────────────────────────────────────
auth_router = Router()
auth_router.add_router("", mobile_auth_router)

@auth_router.post("/register", response=RegisterOutput)
def register(request, data: RegisterInput):
    if User.objects.filter(username=data.username).exists():
        return {"success": False, "message": "Username sudah digunakan.", "user": None}
    user = User.objects.create_user(data.username, data.email, data.password)
    return {"success": True, "message": f"User {user.username} berhasil didaftarkan.", "user": user}

apiv1.add_router("/auth/", auth_router)


# ─── BATCH ENROLL ───────────────────────────────────────────
enroll_router = Router(auth=auth)

@enroll_router.post("/batch-enroll", response=BatchEnrollOutput)
def batch_enroll(request, data: BatchEnrollInput):
    course = Course.objects.filter(id=data.course_id).first()
    if not course:
        return {"success": False, "message": "Course not found.", "enrolled": []}

    enrolled_payload = []
    for uid in data.user_ids:
        user = User.objects.filter(id=uid).first()
        if not user:
            continue
        member, _ = CourseMember.objects.get_or_create(
            course=course,
            user=user,
            defaults={"roles": data.roles}
        )
        # return plain IDs to match schema
        enrolled_payload.append({
            "id":        member.id,
            "course_id": course.id,
            "user_id":   user.id,
            "roles":     member.roles,
        })

    return {
        "success": True,
        "message": f"{len(enrolled_payload)} user(s) enrolled.",
        "enrolled": enrolled_payload,
    }

apiv1.add_router("/courses/", enroll_router)


# ─── ANNOUNCEMENTS ─────────────────────────────────────────
announce_router = Router(auth=auth)

@announce_router.post("/{course_id}/announcements", response=AnnouncementOut)
def create_announcement(request, course_id: int, data: AnnouncementIn):
    course = Course.objects.filter(id=course_id).first()
    if not course or course.teacher != request.user:
        return Response({"detail": "Forbidden"}, status=403)
    return Announcement.objects.create(
        course=course,
        title=data.title,
        message=data.message,
        publish_date=data.publish_date
    )

@announce_router.get("/{course_id}/announcements", response=List[AnnouncementOut])
def list_announcements(request, course_id: int):
    return list(
        Announcement.objects.filter(
            course_id=course_id,
            publish_date__lte=timezone.now()
        )
    )

@announce_router.put("/{course_id}/announcements/{ann_id}", response=AnnouncementOut)
def edit_announcement(request, course_id: int, ann_id: int, data: AnnouncementIn):
    ann = Announcement.objects.filter(id=ann_id, course_id=course_id).first()
    if not ann or ann.course.teacher != request.user:
        return Response({"detail": "Forbidden"}, status=403)
    for k, v in data.dict().items():
        setattr(ann, k, v)
    ann.save()
    return ann

@announce_router.delete("/{course_id}/announcements/{ann_id}")
def delete_announcement(request, course_id: int, ann_id: int):
    ann = Announcement.objects.filter(id=ann_id, course_id=course_id).first()
    if not ann or ann.course.teacher != request.user:
        return Response({"detail": "Forbidden"}, status=403)
    ann.delete()
    return {"success": True}

apiv1.add_router("/courses/", announce_router)


# ─── COMPLETION TRACKING ────────────────────────────────────
completion_router = Router(auth=auth)

@completion_router.post("/completions", response=CompletionOut)
def add_completion(request, data: CompletionInput):
    content = CourseContent.objects.filter(id=data.content_id).first()
    if not content:
        return Response({"detail": "Content not found."}, status=404)

    # only members or teacher may mark complete
    is_member  = CourseMember.objects.filter(course=content.course, user=request.user).exists()
    is_teacher = (content.course.teacher == request.user)
    if not (is_member or is_teacher):
        return Response({"detail": "Forbidden."}, status=403)

    comp, _ = CompletionTracking.objects.get_or_create(
        user=request.user,
        content=content
    )
    return {
        "id":         comp.id,
        "user_id":    comp.user.id,
        "content_id": comp.content.id,
    }

@completion_router.get("/courses/{course_id}/completions", response=List[CourseContentMini])
def show_completions(request, course_id: int):
    qs = CompletionTracking.objects.filter(
        user=request.user,
        content__course_id=course_id
    ).select_related("content")

    # serialize each content item into schema fields
    return [
        {
            "id":          ct.content.id,
            "name":        ct.content.name,
            "description": ct.content.description,
            "course_id":   ct.content.course.id,
            "created_at":  ct.content.created_at,
            "updated_at":  ct.content.updated_at,
        }
        for ct in qs
    ]

@completion_router.delete("/completions/{comp_id}")
def delete_completion(request, comp_id: int):
    comp = CompletionTracking.objects.filter(id=comp_id).first()
    if not comp:
        return Response({"detail": "Not found"}, status=404)
    # allow owner or course teacher
    if comp.user != request.user and comp.content.course.teacher != request.user:
        return Response({"detail": "Forbidden"}, status=403)
    comp.delete()
    return {"success": True}

apiv1.add_router("", completion_router)


# ─── PROFILE ────────────────────────────────────────────────
profile_router = Router(auth=auth)

@profile_router.get("/profile/{user_id}", response=ProfileOut)
def show_profile(request, user_id: int):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"detail": "Not found"}, status=404)
    prof, _ = Profile.objects.get_or_create(user=user)
    enrolled = [m.course for m in CourseMember.objects.filter(user=user)]
    created  = list(Course.objects.filter(teacher=user))
    return {
        "id":             user.id,
        "username":       user.username,
        "email":          user.email,
        "first_name":     user.first_name,
        "last_name":      user.last_name,
        "handphone":      prof.handphone,
        "description":    prof.description,
        "profile_image":  prof.image.url if prof.image else None,
        "courses_enrolled": enrolled,
        "courses_created":  created,
    }

@profile_router.put("/profile", response=ProfileOut)
def edit_profile(request, data: ProfileEditInput):
    user = request.user
    prof, _ = Profile.objects.get_or_create(user=user)
    for field, val in data.dict(exclude_unset=True).items():
        if hasattr(user, field):
            setattr(user, field, val)
        else:
            setattr(prof, field, val)
    user.save()
    prof.save()
    enrolled = [m.course for m in CourseMember.objects.filter(user=user)]
    created  = list(Course.objects.filter(teacher=user))
    return {
        "id":              user.id,
        "username":        user.username,
        "email":           user.email,
        "first_name":      user.first_name,
        "last_name":       user.last_name,
        "handphone":       prof.handphone,
        "description":     prof.description,
        "profile_image":   prof.image.url if prof.image else None,
        "courses_enrolled": enrolled,
        "courses_created":  created,
    }

apiv1.add_router("", profile_router)


# ─── CATEGORIES ────────────────────────────────────────────
category_router = Router(auth=auth)

@category_router.post("/categories", response=CategoryOut)
def add_category(request, data: CategoryIn):
    return Category.objects.create(name=data.name, user=request.user)

@category_router.get("/categories", response=List[CategoryOut])
def list_categories(request):
    return list(Category.objects.all())

@category_router.delete("/categories/{cat_id}")
def delete_category(request, cat_id: int):
    cat = Category.objects.filter(id=cat_id, user=request.user).first()
    if not cat:
        return Response({"detail": "Not found or forbidden"}, status=404)
    cat.delete()
    return {"success": True}

apiv1.add_router("", category_router)


# ─── BOOKMARKS ─────────────────────────────────────────────
bookmark_router = Router(auth=auth)

@bookmark_router.post("/contents/{content_id}/bookmarks", response=BookmarkOut)
def add_bookmark(request, content_id: int, data: BookmarkIn):
    content = CourseContent.objects.filter(id=content_id).first()
    if not content:
        return Response({"detail": "Not found."}, status=404)
    bm, _ = Bookmark.objects.get_or_create(user=request.user, content=content)
    return bm

@bookmark_router.get("/bookmarks", response=List[BookmarkOut])
def list_bookmarks(request):
    return list(Bookmark.objects.filter(user=request.user))

@bookmark_router.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(request, bookmark_id: int):
    bm = Bookmark.objects.filter(id=bookmark_id, user=request.user).first()
    if not bm:
        return Response({"detail": "Not found"}, status=404)
    bm.delete()
    return {"success": True}

apiv1.add_router("", bookmark_router)


# ─── FEEDBACK ──────────────────────────────────────────────
feedback_router = Router(auth=auth)

@feedback_router.post("/{course_id}/feedback", response=FeedbackOut)
def add_feedback(request, course_id: int, data: FeedbackIn):
    course  = Course.objects.filter(id=course_id).first()
    allowed = CourseMember.objects.filter(course=course, user=request.user).exists()
    if not course or not allowed:
        return Response({"detail": "Forbidden or not found"}, status=403)
    fb, _ = Feedback.objects.update_or_create(
        course=course,
        user=request.user,
        defaults={"message": data.message, "rating": data.rating}
    )
    return fb

@feedback_router.get("/{course_id}/feedback", response=List[FeedbackOut])
def list_feedback(request, course_id: int):
    return list(Feedback.objects.filter(course_id=course_id))

@feedback_router.put("/{course_id}/feedback/{fb_id}", response=FeedbackOut)
def edit_feedback(request, course_id: int, fb_id: int, data: FeedbackIn):
    fb = Feedback.objects.filter(id=fb_id, course_id=course_id, user=request.user).first()
    if not fb:
        return Response({"detail": "Not found or forbidden"}, status=404)
    fb.message = data.message
    fb.rating  = data.rating
    fb.save()
    return fb

@feedback_router.delete("/{course_id}/feedback/{fb_id}")
def delete_feedback(request, course_id: int, fb_id: int):
    fb = Feedback.objects.filter(id=fb_id, course_id=course_id, user=request.user).first()
    if not fb:
        return Response({"detail": "Not found or forbidden"}, status=404)
    fb.delete()
    return {"success": True}

apiv1.add_router("/courses/", feedback_router)


# ─── DASHBOARD ─────────────────────────────────────────────
dashboard_router = Router(auth=auth)

@dashboard_router.get("/dashboard", response=DashboardOut)
def user_dashboard(request):
    enrolled_count    = CourseMember.objects.filter(user=request.user).count()
    created_count     = Course.objects.filter(teacher=request.user).count()
    comments_count    = Comment.objects.filter(member__user=request.user).count()
    completions_count = CompletionTracking.objects.filter(user=request.user).count()
    return {
        "courses_enrolled":   enrolled_count,
        "courses_created":    created_count,
        "comments_count":     comments_count,
        "completions_count":  completions_count,
    }

apiv1.add_router("", dashboard_router)


# ─── ANALYTICS ────────────────────────────────────────────
analytics_router = Router(auth=auth)

@analytics_router.get("/{course_id}/analytics", response=CourseAnalyticsOut)
def course_analytics(request, course_id: int):
    course = Course.objects.filter(id=course_id).first()
    if not course or (
        course.teacher != request.user and
        not CourseMember.objects.filter(course=course, user=request.user).exists()
    ):
        return Response({"detail": "Not found or forbidden"}, status=404)

    members_count   = CourseMember.objects.filter(course=course).count()
    contents_count  = CourseContent.objects.filter(course=course).count()
    comments_count  = Comment.objects.filter(content__course=course).count()
    feedback_count  = Feedback.objects.filter(course=course).count()

    return {
        "members_count":   members_count,
        "contents_count":  contents_count,
        "comments_count":  comments_count,
        "feedback_count":  feedback_count,
    }

apiv1.add_router("/courses/", analytics_router)
