# Analytics Agent Testing Commands

## Prerequisites
Make sure you have the following running:
1. Backend server on port 4000
2. Database connection established
3. Node.js and Python environments set up

## Step-by-Step Testing Commands

### 1. Navigate to Project Directory
```bash
cd /Users/potriabhisribarama/Documents/HackMIT
```

### 2. Start Backend Server (if not already running)
```bash
# Terminal 1 - Start the backend API server
npm run dev
# This should start the server on http://localhost:4000
```

### 3. Clear and Insert Enhanced Mock Data
```bash
# Terminal 2 - Insert fresh mock data with 5 students
node insert_mock_data.js
```

### 4. Verify Database Data
```bash
# Check data counts in database
node -e "
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function checkData() {
  console.log('=== Database Verification ===');
  const faqCount = await prisma.frequentlyAskedQuestion.count();
  const analyticsCount = await prisma.learningAnalytics.count();
  const takeawaysCount = await prisma.sessionTakeaway.count();
  const sessionsCount = await prisma.chatSession.count();
  
  console.log('FAQ entries:', faqCount);
  console.log('Learning analytics entries:', analyticsCount);
  console.log('Session takeaways entries:', takeawaysCount);
  console.log('Chat sessions entries:', sessionsCount);
  
  await prisma.\$disconnect();
}

checkData().catch(console.error);
"
```

### 5. Test Individual API Endpoints

#### Test FAQs Endpoint
```bash
curl -s "http://localhost:4000/api/teacher/cmfjnia2t0000oihjgwx13py3/faqs?start=2025-08-15&end=2025-09-14" | jq '.topFaqs[:3]'
```

#### Test Topic Performance Endpoint
```bash
curl -s "http://localhost:4000/api/teacher/cmfjnia2t0000oihjgwx13py3/topic-performance?start=2025-08-15&end=2025-09-14" | jq '.successfulTopics[:3]'
```

#### Test Analytics Summary Endpoint
```bash
curl -s "http://localhost:4000/api/teacher/cmfjnia2t0000oihjgwx13py3/analytics-summary?start=2025-08-15&end=2025-09-14" | jq '.'
```

### 6. Test Complete Analytics Agent Report
```bash
# Generate the full analytics report
python build_teacher_overview.py --teacher-id cmfjnia2t0000oihjgwx13py3
```

### 7. Test with Different Teacher ID (if available)
```bash
# Test with another teacher ID to see different results
python build_teacher_overview.py --teacher-id teacher_456
```

### 8. Save Report to File
```bash
# Generate and save report to file
python build_teacher_overview.py --teacher-id cmfjnia2t0000oihjgwx13py3 --output teacher_report.md
```

### 9. View Generated Report
```bash
# View the generated report
cat teacher_report.md
```

### 10. Test Analytics Agent Directly
```bash
# Test the analytical agent Python class directly
python -c "
from analytical_agent import AnalyticalAgent
import json

agent = AnalyticalAgent()
teacher_id = 'cmfjnia2t0000oihjgwx13py3'
start_date = '2025-08-15'
end_date = '2025-09-14'

print('=== Testing Analytics Agent ===')

# Test FAQ fetching
faqs = agent.fetch_faqs(teacher_id, start_date, end_date)
print('FAQs fetched:', len(faqs.get('topFaqs', [])) if faqs else 0)

# Test topic performance
topics = agent.fetch_topic_performance(teacher_id, start_date, end_date)
print('Successful topics:', len(topics.get('successfulTopics', [])) if topics else 0)
print('Struggling topics:', len(topics.get('strugglingTopics', [])) if topics else 0)

# Test analytics summary
summary = agent.fetch_analytics_summary(teacher_id, start_date, end_date)
print('Summary generated:', bool(summary.get('summary')))
print('Key insights:', len(summary.get('keyInsights', [])))
print('Recommendations:', len(summary.get('recommendations', [])))
"
```

### 11. Check Prisma Studio (Optional)
```bash
# Open Prisma Studio to visually inspect data
npx prisma studio
# Then open http://localhost:5557 in browser
```

## Expected Results

After running these commands, you should see:

1. **Database populated** with:
   - 5+ FAQ entries
   - 10+ learning analytics entries (2 per student)
   - 8+ session takeaways (multiple students)
   - 5+ chat sessions

2. **API endpoints returning** realistic data with multiple students

3. **Complete analytics report** showing:
   - ❓ Most Frequently Asked Questions
   - ✅ Topics Students Excel At (with multiple students)
   - ⚠️ Topics Students Struggle With (diverse struggles)
   - 📊 Analytics Summary with insights and recommendations

4. **Realistic metrics** reflecting a class of 5 students with varied performance

## Troubleshooting

If you encounter issues:

```bash
# Check if backend is running
curl http://localhost:4000/api/health

# Check database connection
npx prisma db push

# Reset database if needed
npx prisma migrate reset --force

# Reinstall dependencies if needed
npm install
pip install -r requirements.txt
```

## Sample Expected Output

The analytics report should show data like:
- FAQs asked 100+ times total across multiple categories
- 5 students with different success rates
- Multiple struggling topics across different students
- Intelligent summary with actionable insights for a class of 5 students
