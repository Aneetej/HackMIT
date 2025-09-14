# API Changes Documentation

## Overview
Replaced mock data endpoints with real database-integrated API routes that connect to the existing PostgreSQL database using Prisma ORM.

## Backend Changes (server.ts)

### Database Integration
- All endpoints now use `prisma` client to interact with the existing database
- Proper error handling with try-catch blocks
- HTTP status codes for different scenarios (404, 500)

### Endpoints Modified/Added

#### 1. GET `/api/student/:studentId`
**Purpose**: Get student information and enrolled classes
**Database Tables Used**: 
- `students` (main student data)
- `chat_sessions` (to get enrolled classes)

**Key Changes**:
- Queries `Student` model with `chat_sessions` relationship
- Maps `chat_sessions` to class format for frontend compatibility
- Returns actual `subject_focus` and `learning_style` from database

#### 2. GET `/api/student/:studentId/class/:classId`
**Purpose**: Get class details and chat history
**Database Tables Used**:
- `chat_sessions` (class information)
- `chat_messages` (message history)

**Key Changes**:
- Validates session belongs to student
- Retrieves all messages ordered by timestamp
- Maps database message format to frontend format

#### 3. POST `/api/student/:studentId/class/:classId/message`
**Purpose**: Send message and receive AI response
**Database Tables Used**:
- `chat_messages` (store both user and AI messages)
- `chat_sessions` (update session metrics)

**Key Changes**:
- Saves user message to database
- Creates AI response message (placeholder logic)
- Updates session `questions_asked` counter
- Returns properly formatted response

#### 4. POST `/api/student/join-class`
**Purpose**: Create new chat session (class)
**Database Tables Used**:
- `students` (validate student exists)
- `chat_sessions` (create new session)

**Key Changes**:
- Validates student exists before creating session
- Creates new `ChatSession` record
- Uses classCode as session_type

#### 5. PUT `/api/student/:studentId/preferences`
**Purpose**: Update student learning preferences
**Database Tables Used**:
- `students` (update preferences)

**Key Changes**:
- Updates `subject_focus` and `learning_style` fields
- Proper error handling for non-existent students

## Frontend Changes

### axios-config.tsx
- Fixed baseURL to use `http://localhost:4000` (matching server port)
- Removed hardcoded external API URL

### student/apis.ts
**Complete Rewrite**: Replaced comments with full implementation

**Added TypeScript Interfaces**:
- `ChatMessage` - Message structure
- `ClassInfo` - Class basic info
- `StudentInfo` - Student data with classes
- `ClassDetails` - Full class with chat history
- `MessageResponse` - AI response format

**Added API Functions**:
- `getStudentInfo()` - Fetch student data
- `getClass()` - Get class and chat history
- `sendMessage()` - Send message, get AI response
- `joinClass()` - Create new class session
- `updatePreferences()` - Update learning preferences

## Database Schema Utilization

### Tables Used
- **students**: Core student information and preferences
- **chat_sessions**: Class/session management
- **chat_messages**: Message storage and history
- **student_preferences**: (Available for future enhanced preference system)

### Key Relationships
- Student → ChatSessions (one-to-many)
- ChatSession → ChatMessages (one-to-many)
- Student → StudentPreferences (one-to-many, unused currently)

## Configuration
- **Database**: PostgreSQL via Prisma ORM
- **Server Port**: 4000 (from .env)
- **CORS**: Enabled for frontend integration
- **Error Handling**: Comprehensive try-catch with proper HTTP status codes

## Notes
- AI response generation is placeholder - ready for actual AI integration
- All endpoints follow REST conventions
- Frontend TypeScript interfaces match backend response formats exactly
- Database queries are optimized with proper includes and selects
