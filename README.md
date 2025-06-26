# Simple LMS API

This project is a backend API for a simple Learning Management System (LMS) built with **Django**, **Django Ninja**, and **JWT authentication**. It provides endpoints for user registration, course management, student enrollment, content tracking, comments, bookmarks, feedback, and analytics.

## Features

* **User Authentication**: JWT-based login & registration
* **Course Management**: Create courses, list, update, delete
* **Batch Enrollment**: Enroll multiple users into a course in one request
* **Announcements**: CRUD announcements per course
* **Content Completion**: Track when users complete course content
* **Profile**: View and edit user profiles
* **Categories**: Manage custom course categories
* **Bookmarks**: Bookmark/unbookmark content items
* **Feedback**: Submit and manage course feedback and ratings
* **Dashboard**: User activity summary
* **Analytics**: Course-level metrics (members, contents, comments, feedback)

## Tech Stack

* Python 3.10+
* Django 5.x
* Django Ninja (Fast API-like framework for Django)
* SQLite (default, switchable to other DB)
* JWT authentication via ninja-simple-jwt
* Docker & docker-compose for containerized setup

## Getting Started

### Prerequisites

* Docker & docker-compose
* Git

### Installation

1. Clone the repo:

   ```bash
   git clone <repo-url>
   cd <project-root>
   ```
2. Create `.env` file from template and configure:

   ```bash
   cp .env.example .env
   # edit .env to set SECRET_KEY, DB settings, JWT settings
   ```
3. Build and run with Docker:

   ```bash
   docker-compose up --build -d
   ```
4. Apply migrations and create superuser:

   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```
5. Access API docs at:

   ```
   http://localhost:8000/api/docs
   ```

## API Endpoints

| Method | URL                                           | Description                          |
| ------ | --------------------------------------------- | ------------------------------------ |
| POST   | `/api/v1/auth/register`                       | Register a new user                  |
| POST   | `/api/v1/auth/login`                          | Obtain JWT access & refresh tokens   |
| POST   | `/api/v1/courses/batch-enroll`                | Enroll multiple users to a course    |
| GET    | `/api/v1/courses/{id}/announcements`          | List announcements for a course      |
| POST   | `/api/v1/courses/{id}/announcements`          | Create announcement (teacher only)   |
| PUT    | `/api/v1/courses/{id}/announcements/{ann_id}` | Update announcement (teacher)        |
| DELETE | `/api/v1/courses/{id}/announcements/{ann_id}` | Delete announcement (teacher)        |
| POST   | `/api/v1/completions`                         | Mark content as completed            |
| GET    | `/api/v1/courses/{id}/completions`            | List completed content for a course  |
| DELETE | `/api/v1/completions/{comp_id}`               | Remove a completion record           |
| GET    | `/api/v1/profile/{user_id}`                   | View user profile                    |
| PUT    | `/api/v1/profile`                             | Edit current user profile            |
| POST   | `/api/v1/categories`                          | Create a new category                |
| GET    | `/api/v1/categories`                          | List all categories                  |
| DELETE | `/api/v1/categories/{id}`                     | Delete category (owner only)         |
| POST   | `/api/v1/contents/{id}/bookmarks`             | Bookmark a content item              |
| GET    | `/api/v1/bookmarks`                           | List user bookmarks                  |
| DELETE | `/api/v1/bookmarks/{bookmark_id}`             | Remove bookmark                      |
| POST   | `/api/v1/courses/{id}/feedback`               | Submit or update feedback (enrolled) |
| GET    | `/api/v1/courses/{id}/feedback`               | List feedback for a course           |
| DELETE | `/api/v1/courses/{id}/feedback/{fb_id}`       | Delete a feedback entry              |
| GET    | `/api/v1/dashboard`                           | User activity dashboard              |
| GET    | `/api/v1/courses/{id}/analytics`              | Course analytics (teacher or member) |

## Database Models

1. **Profile**: Extends `User` with phone, description, avatar
2. **Category**: Custom tags for courses, per user
3. **Course**: Name, description, price, image, teacher, category
4. **CourseMember**: M2M between `Course` & `User` with roles
5. **CourseContent**: Sections or lessons in a course
6. **Comment**: Comments by members on content
7. **Announcement**: Course announcements by teacher
8. **CompletionTracking**: Records when a user completes content
9. **Bookmark**: User bookmarks of content
10. **Feedback**: One rating & message per user per course

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Commit your changes (`git commit -m "Add xyz feature"`)
4. Push to branch (`git push origin feature/xyz`)
5. Open a Pull Request

## License

MIT © Your Name

---

*This README was auto-generated to guide setup and usage of the Simple LMS API.*
