from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    handphone   = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image       = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="categories"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(models.Model):
    name        = models.CharField("Nama Kursus", max_length=255)
    description = models.TextField("Deskripsi")
    price       = models.IntegerField("Harga")
    image       = models.ImageField(
        "Gambar", upload_to="course", blank=True, null=True
    )
    teacher     = models.ForeignKey(
        User,
        verbose_name="Pengajar",
        on_delete=models.RESTRICT,
        related_name="courses_created",
    )
    category    = models.ForeignKey(
        Category,
        verbose_name="Kategori",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    created_at  = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at  = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Data Mata Kuliah"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_member(self, user: User) -> bool:
        return self.members.filter(user=user).exists()


ROLE_OPTIONS = [
    ("std", "Siswa"),
    ("ast", "Asisten"),
]


class CourseMember(models.Model):
    course  = models.ForeignKey(
        Course, on_delete=models.RESTRICT, related_name="members"
    )
    user    = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="enrollments"
    )
    roles   = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default="std")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber Matkul"
        verbose_name_plural = "Subscriber Matkul"
        unique_together = ("course", "user")

    def __str__(self):
        return f"{self.user.username} in {self.course.name} as {self.roles}"


class CourseContent(models.Model):
    name            = models.CharField("judul konten", max_length=200)
    description     = models.TextField("deskripsi", default="-")
    video_url       = models.CharField("URL Video", max_length=200, null=True, blank=True)
    file_attachment = models.FileField("File", null=True, blank=True)
    course          = models.ForeignKey(
        Course, on_delete=models.RESTRICT, related_name="contents"
    )
    parent          = models.ForeignKey(
        "self", on_delete=models.RESTRICT,
        null=True, blank=True, related_name="children"
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"

    def __str__(self):
        return f"{self.course.name} → {self.name}"


class Comment(models.Model):
    content    = models.ForeignKey(
        CourseContent, on_delete=models.CASCADE, related_name="comments"
    )
    member     = models.ForeignKey(
        CourseMember, on_delete=models.CASCADE, related_name="comments"
    )
    comment    = models.TextField("komentar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"

    def __str__(self):
        return f"{self.member.user.username}: {self.comment[:30]}"


class Announcement(models.Model):
    course       = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="announcements"
    )
    title        = models.CharField(max_length=255)
    message      = models.TextField()
    publish_date = models.DateTimeField()
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.course.name}] {self.title}"


class CompletionTracking(models.Model):
    user         = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="completions"
    )
    content      = models.ForeignKey(
        CourseContent, on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content")
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.username} completed {self.content.name}"


class Bookmark(models.Model):
    user       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookmarks"
    )
    content    = models.ForeignKey(
        CourseContent, on_delete=models.CASCADE, related_name="bookmarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content")

    def __str__(self):
        return f"🔖 {self.user.username} → {self.content.name}"


class Feedback(models.Model):
    course     = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="feedbacks"
    )
    user       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feedbacks"
    )
    message    = models.TextField()
    rating     = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "user")

    def __str__(self):
        return f"{self.user.username} → {self.course.name}"
