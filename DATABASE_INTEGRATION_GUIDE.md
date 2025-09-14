# Database Integration Guide

## Overview
This guide explains how to switch from hardcoded mock data to real database queries for the analytics system.

## Current State Analysis

### ✅ Complete Data Coverage:
All analytics data can be calculated from the existing schema tables.
- **Session data**: Duration, status, concepts covered (`ChatSession` table)  
- **Message data**: Counts, timestamps, sender types (`ChatMessage` table)
- **Learning analytics**: Engagement metrics, success rates (`LearningAnalytics` table)
- **FAQ data**: Questions, categories, frequency (`FrequentlyAskedQuestion` table)
- **Teacher data**: Supervised students (`Teacher` table)

### ✅ All Required Data Available in Current Schema

## Code Changes Made

### 1. Updated AnalyticalAgent Class
- Added `use_mock_data` parameter to constructor
- Added Prisma database connection
- Made methods async for database operations
- Added real data calculation methods

### 2. Key Methods Added:
- `_calculate_overview_metrics()`: Calculates real metrics from database
- `fetch_faqs()`: Gets FAQ data from database
- Real-time calculation of:
  - Completion rates from `ChatSession.status`
  - Session durations from `started_at`/`ended_at`
  - Message counts from `ChatMessage` table
  - Student activity from session counts
  - Peak hours from message timestamps
  - Learning challenges from `concepts_covered`

### 3. Data Mapping:

| Hardcoded Data | Database Source | Calculation Method |
|----------------|-----------------|-------------------|
| Total Students | `Student` table | Count of supervised students |
| Total Sessions | `ChatSession` table | Count in date range |
| Completion Rate | `ChatSession.status` | % with status="completed" |
| Avg Duration | `started_at`/`ended_at` | Average time difference |
| Message Counts | `ChatMessage` table | Count per student/session |
| Student Names | `Student.name` | Direct lookup |
| Peak Hours | `ChatMessage.timestamp` | Group by hour, find max |
| FAQ Data | `FrequentlyAskedQuestion` | Order by frequency_count |
| Learning Challenges | `ChatSession.concepts_covered` | Count frequency |

## Setup Requirements

### 1. Install Dependencies:
```bash
pip install prisma
npm install prisma @prisma/client
```

### 2. Generate Prisma Client:
```bash
npx prisma generate
```

### 3. Database Setup:
```bash
npx prisma db push  # Apply schema to database
```

### 4. Environment Variables:
```bash
DATABASE_URL="postgresql://username:password@host:5432/database_name"
USE_MOCK_DATA=false  # Set to false to use real data
```

## Usage Examples

### Using Real Database Data:
```python
# Initialize with real data
agent = AnalyticalAgent(use_mock_data=False)

# Fetch real analytics (async)
import asyncio
overview = asyncio.run(agent.fetch_teacher_overview("teacher_123", "2025-09-06", "2025-09-13"))
faqs = asyncio.run(agent.fetch_faqs("teacher_123", limit=10))
```

### Fallback to Mock Data:
```python
# Initialize with mock data (default)
agent = AnalyticalAgent(use_mock_data=True)

# Will use MockDataGenerator
overview = agent._generate_mock_overview("teacher_123", "2025-09-06", "2025-09-13")
```

## Benefits of Real Data Integration

1. **Accurate Analytics**: Real student engagement and performance data
2. **Dynamic Insights**: Data updates automatically as students use the system
3. **Personalized Recommendations**: Based on actual student struggles and patterns
4. **Scalable**: Works with any number of students and teachers
5. **AI-Enhanced**: Exa AI generates lesson plans based on real misconceptions

## Exa AI Integration (Already Implemented)

The system now generates lesson plans using:
- **Real misconceptions** from database
- **Actual student struggles** from session data
- **Exa AI API** for dynamic content generation
- **Fallback templates** when API unavailable

## Next Steps

1. **Populate Database** with real student/session data
2. **Set Environment Variables** for database connection
3. **Test Real Data Flow** with actual database
4. **Configure Exa API Key** for AI-generated lesson plans

## Error Handling

The system includes robust fallback mechanisms:
- Database connection fails → Use mock data
- Prisma client unavailable → Use mock data  
- Exa API unavailable → Use template lessons
- No data found → Generate empty/default responses

This ensures the analytics system always works, regardless of external dependencies.
