# Qryti Learn API Documentation

**Version:** 1.0.0  
**Author:** Manus AI  
**Last Updated:** July 5, 2025  
**Base URL:** `https://api.qryti.com` (Production) | `http://localhost:5002` (Development)

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Core APIs](#core-apis)
4. [Enterprise APIs](#enterprise-apis)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

## Introduction

The Qryti Learn API provides comprehensive access to ISO/IEC 42001 learning management functionality, including user management, course delivery, assessment systems, certification generation, and enterprise features. This RESTful API supports JSON data exchange and implements JWT-based authentication for secure access control.

The API architecture follows modern best practices with clear separation between public endpoints, authenticated user endpoints, and administrative functions. All endpoints return consistent JSON responses with appropriate HTTP status codes and detailed error messages when applicable.




## Authentication

The Qryti Learn API uses JSON Web Tokens (JWT) for authentication. Users must obtain an access token through the login endpoint and include it in the Authorization header for protected endpoints.

### Authentication Flow

1. **User Registration**: Create a new user account using the registration endpoint
2. **User Login**: Authenticate with email and password to receive access and refresh tokens
3. **Token Usage**: Include the access token in the Authorization header for protected endpoints
4. **Token Refresh**: Use the refresh token to obtain new access tokens when they expire

### Token Format

```
Authorization: Bearer <access_token>
```

### Token Expiration

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2025-07-05T10:30:00Z"
  }
}
```

#### POST /api/auth/login

Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /api/auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### GET /api/auth/profile

Get current user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-07-05T10:30:00Z",
  "last_login": "2025-07-05T15:45:00Z"
}
```


## Core APIs

### Course Management

The course management system provides access to ISO/IEC 42001 learning content organized into structured courses and modules.

#### GET /api/courses

Retrieve all available courses.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "courses": [
    {
      "id": 1,
      "title": "ISO/IEC 42001 Foundation",
      "description": "Introduction to AI Management Systems",
      "duration_hours": 8,
      "difficulty_level": "Beginner",
      "modules_count": 4,
      "enrolled": true,
      "progress_percentage": 75,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/courses/{course_id}

Retrieve detailed information about a specific course.

**Parameters:**
- `course_id` (integer): Unique course identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "ISO/IEC 42001 Foundation",
  "description": "Comprehensive introduction to AI Management Systems",
  "duration_hours": 8,
  "difficulty_level": "Beginner",
  "modules": [
    {
      "id": 1,
      "title": "Introduction to AI Management",
      "description": "Overview of AI management principles",
      "order": 1,
      "duration_minutes": 120,
      "completed": true
    }
  ],
  "enrollment_status": "enrolled",
  "progress_percentage": 75
}
```

#### POST /api/courses/{course_id}/enroll

Enroll in a specific course.

**Parameters:**
- `course_id` (integer): Unique course identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (201 Created):**
```json
{
  "message": "Successfully enrolled in course",
  "enrollment": {
    "course_id": 1,
    "user_id": 1,
    "enrolled_at": "2025-07-05T15:30:00Z",
    "status": "active"
  }
}
```

### Quiz System

The quiz system provides comprehensive assessment capabilities with multiple question types and instant scoring.

#### GET /api/quizzes

Retrieve all available quizzes.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "ISO 42001 Foundations Assessment",
    "description": "Test your understanding of AI management fundamentals",
    "questions_count": 20,
    "time_limit_minutes": 30,
    "passing_score": 70,
    "attempts_allowed": 3,
    "user_attempts": 1,
    "best_score": 85,
    "module_id": 1
  }
]
```

#### GET /api/quizzes/{quiz_id}

Retrieve detailed quiz information including questions.

**Parameters:**
- `quiz_id` (integer): Unique quiz identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "ISO 42001 Foundations Assessment",
  "description": "Test your understanding of AI management fundamentals",
  "time_limit_minutes": 30,
  "passing_score": 70,
  "questions": [
    {
      "id": 1,
      "question_text": "What is the primary purpose of ISO/IEC 42001?",
      "question_type": "multiple_choice",
      "options": [
        "To manage AI systems effectively",
        "To develop AI algorithms",
        "To regulate AI companies",
        "To train AI models"
      ],
      "points": 5
    }
  ]
}
```

#### POST /api/quizzes/{quiz_id}/start

Start a new quiz attempt.

**Parameters:**
- `quiz_id` (integer): Unique quiz identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (201 Created):**
```json
{
  "attempt_id": 123,
  "quiz_id": 1,
  "started_at": "2025-07-05T15:30:00Z",
  "time_limit_minutes": 30,
  "expires_at": "2025-07-05T16:00:00Z"
}
```

#### POST /api/quizzes/{quiz_id}/submit

Submit quiz answers for scoring.

**Parameters:**
- `quiz_id` (integer): Unique quiz identifier

**Request Body:**
```json
{
  "attempt_id": 123,
  "answers": [
    {
      "question_id": 1,
      "selected_options": [0]
    },
    {
      "question_id": 2,
      "selected_options": [1, 3]
    }
  ]
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "attempt_id": 123,
  "score": 85,
  "percentage": 85,
  "passed": true,
  "total_questions": 20,
  "correct_answers": 17,
  "time_taken_minutes": 25,
  "submitted_at": "2025-07-05T15:55:00Z",
  "detailed_results": [
    {
      "question_id": 1,
      "correct": true,
      "points_earned": 5,
      "points_possible": 5
    }
  ]
}
```


### Certificate System

The certificate system generates professional PDF certificates and provides verification capabilities.

#### GET /api/certificates/stats

Get certificate statistics (public endpoint).

**Response (200 OK):**
```json
{
  "total_certificates": 1250,
  "certificates_this_month": 89,
  "verification_requests": 2340,
  "average_score": 82.5
}
```

#### GET /api/certificates

Get user's certificates.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "certificates": [
    {
      "id": 1,
      "certificate_id": "QRT-2025-001234",
      "course_title": "ISO/IEC 42001 Foundation",
      "issued_date": "2025-07-05T16:00:00Z",
      "score": 85,
      "verification_url": "https://verify.qryti.com/QRT-2025-001234",
      "download_url": "/api/certificates/1/download"
    }
  ]
}
```

#### GET /api/certificates/{certificate_id}/download

Download certificate PDF.

**Parameters:**
- `certificate_id` (integer): Unique certificate identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
- Content-Type: application/pdf
- Returns PDF file for download

#### GET /api/certificates/verify/{verification_code}

Verify certificate authenticity (public endpoint).

**Parameters:**
- `verification_code` (string): Certificate verification code

**Response (200 OK):**
```json
{
  "valid": true,
  "certificate": {
    "certificate_id": "QRT-2025-001234",
    "recipient_name": "John Doe",
    "course_title": "ISO/IEC 42001 Foundation",
    "issued_date": "2025-07-05T16:00:00Z",
    "issuing_organization": "Qryti Learn"
  }
}
```

### Video Learning System

The video system provides YouTube integration with progress tracking and engagement analytics.

#### GET /api/videos/stats

Get video learning statistics.

**Response (200 OK):**
```json
{
  "total_videos": 45,
  "total_watch_time_hours": 1250,
  "average_completion_rate": 78.5,
  "most_watched_video": "Introduction to AI Management"
}
```

#### GET /api/videos

Get available videos.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "videos": [
    {
      "id": 1,
      "title": "Introduction to AI Management",
      "description": "Overview of AI management principles",
      "youtube_id": "dQw4w9WgXcQ",
      "duration_seconds": 1800,
      "course_id": 1,
      "module_id": 1,
      "watch_progress": 75,
      "completed": false
    }
  ]
}
```

#### POST /api/videos/{video_id}/progress

Update video watch progress.

**Parameters:**
- `video_id` (integer): Unique video identifier

**Request Body:**
```json
{
  "progress_seconds": 900,
  "total_duration": 1800,
  "completed": false
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Progress updated successfully",
  "progress_percentage": 50,
  "completed": false
}
```

### Knowledge Base System

The knowledge base provides downloadable resources and comprehensive search capabilities.

#### GET /api/knowledge/stats

Get knowledge base statistics.

**Response (200 OK):**
```json
{
  "total_resources": 125,
  "total_downloads": 5670,
  "categories": 8,
  "average_rating": 4.6
}
```

#### GET /api/knowledge/resources

Get available knowledge base resources.

**Query Parameters:**
- `category` (string, optional): Filter by category
- `search` (string, optional): Search in title and description
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "resources": [
    {
      "id": 1,
      "title": "ISO/IEC 42001 Implementation Guide",
      "description": "Comprehensive guide for implementing AI management systems",
      "category": "Implementation Guides",
      "file_type": "PDF",
      "file_size_mb": 2.5,
      "download_count": 234,
      "rating": 4.8,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 6,
    "total_items": 125,
    "items_per_page": 20
  }
}
```

#### GET /api/knowledge/resources/{resource_id}/download

Download a knowledge base resource.

**Parameters:**
- `resource_id` (integer): Unique resource identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
- Content-Type: application/pdf (or appropriate file type)
- Returns file for download

#### POST /api/knowledge/resources/{resource_id}/bookmark

Bookmark a resource.

**Parameters:**
- `resource_id` (integer): Unique resource identifier

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (201 Created):**
```json
{
  "message": "Resource bookmarked successfully",
  "bookmark_id": 123
}
```

