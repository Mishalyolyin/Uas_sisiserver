from ninja import Schema
from typing import Optional, List
from datetime import datetime

# -------- User and Auth Schemas --------
class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class RegisterInput(Schema):
    username: str
    email: str
    password: str

class RegisterOutput(Schema):
    success: bool
    message: str
    user: Optional[UserOut]

# -------- Batch Enroll --------
class BatchEnrollInput(Schema):
    course_id: int
    user_ids: List[int]
    roles: Optional[str] = 'std'

class BatchEnrollOutput(Schema):
    success: bool
    message: str
    enrolled: List['CourseMemberOut']

# -------- Announcement --------
class AnnouncementIn(Schema):
    title: str
    message: str
    publish_date: datetime

class AnnouncementOut(Schema):
    id: int
    course_id: int
    title: str
    message: str
    publish_date: datetime
    created_at: datetime
    updated_at: datetime

# -------- Course Schemas --------
class CourseSchemaIn(Schema):
    name: str
    description: str
    price: int

class CourseSchemaOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image: Optional[str]
    teacher: UserOut
    created_at: datetime
    updated_at: datetime

class CourseMemberOut(Schema):
    id: int
    course_id: CourseSchemaOut
    user_id: UserOut
    roles: str

# -------- Content Schemas --------
class CourseContentMini(Schema):
    id: int
    name: str
    description: str
    course_id: int
    created_at: datetime
    updated_at: datetime

class CourseContentFull(Schema):
    id: int
    name: str
    description: str
    video_url: Optional[str]
    file_attachment: Optional[str]
    course_id: CourseSchemaOut
    created_at: datetime
    updated_at: datetime

# -------- Comment Schemas --------
class CourseCommentIn(Schema):
    comment: str

class CourseCommentOut(Schema):
    id: int
    content_id: CourseContentMini
    member_id: CourseMemberOut
    comment: str
    created_at: datetime
    updated_at: datetime

# -------- Completion Tracking --------
class CompletionInput(Schema):
    content_id: int

class CompletionOut(Schema):
    id: int
    user_id: int
    content_id: int

# -------- Profile Schemas --------
class ProfileOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    handphone: Optional[str]
    description: Optional[str]
    profile_image: Optional[str]
    courses_enrolled: List[CourseSchemaOut]
    courses_created: List[CourseSchemaOut]

class ProfileEditInput(Schema):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    handphone: Optional[str]
    description: Optional[str]
    profile_image: Optional[str]

# -------- Category Schemas --------
class CategoryIn(Schema):
    name: str

class CategoryOut(Schema):
    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime

# -------- Bookmark Schemas --------
class BookmarkIn(Schema):
    pass

class BookmarkOut(Schema):
    id: int
    user_id: int
    content_id: int
    created_at: datetime

# -------- Feedback Schemas --------
class FeedbackIn(Schema):
    message: str
    rating: Optional[float] = None

class FeedbackOut(Schema):
    id: int
    course_id: int
    user_id: int
    message: str
    rating: Optional[float]
    created_at: datetime
    updated_at: datetime

# -------- Dashboard --------
class DashboardOut(Schema):
    courses_enrolled: int
    courses_created: int
    comments_count: int
    completions_count: int

class CourseAnalyticsOut(Schema):
    members_count: int         # total enrolled in this course
    contents_count: int        # total content items in this course
    comments_count: int        # total comments on this course
    feedback_count: int        # total feedback entries on this course
