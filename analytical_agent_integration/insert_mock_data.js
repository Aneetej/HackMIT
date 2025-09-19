const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function insertMockData() {
  console.log('=== Inserting Mock Data for Analytics Testing ===');
  
  try {
    // 1. Insert FAQ data
    console.log('Inserting FAQ data...');
    
    const faqData = [
      {
        question_text: "How do I solve quadratic equations?",
        category: "algebra",
        frequency_count: 25,
        success_rate: 0.78,
        keywords: ["algebra", "quadratic", "equations"]
      },
      {
        question_text: "What is the Pythagorean theorem?",
        category: "geometry", 
        frequency_count: 18,
        success_rate: 0.85,
        keywords: ["geometry", "theorem", "pythagorean"]
      },
      {
        question_text: "How do I find the derivative of a function?",
        category: "calculus",
        frequency_count: 22,
        success_rate: 0.65,
        keywords: ["calculus", "derivative", "function"]
      },
      {
        question_text: "What are prime numbers?",
        category: "number_theory",
        frequency_count: 12,
        success_rate: 0.92,
        keywords: ["numbers", "prime", "theory"]
      },
      {
        question_text: "How do I solve systems of equations?",
        category: "algebra",
        frequency_count: 20,
        success_rate: 0.70,
        keywords: ["algebra", "systems", "equations"]
      }
    ];

    for (const faq of faqData) {
      await prisma.frequentlyAskedQuestion.create({
        data: {
          ...faq,
          first_asked: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          last_asked: new Date(Date.now() - 24 * 60 * 60 * 1000)
        }
      });
    }
    console.log('✓ FAQ data inserted');

    // 2. Create students first
    console.log('Creating students...');
    
    const studentsData = [
      { id: "cmfjniab50001oihjqsfvi427", name: "Alice Johnson", email: "alice.johnson@school.edu", grade: 10 },
      { id: "cmfjniab50002oihjqsfvi428", name: "Bob Smith", email: "bob.smith@school.edu", grade: 10 },
      { id: "cmfjniab50003oihjqsfvi429", name: "Carol Davis", email: "carol.davis@school.edu", grade: 10 },
      { id: "cmfjniab50004oihjqsfvi430", name: "David Wilson", email: "david.wilson@school.edu", grade: 10 },
      { id: "cmfjniab50005oihjqsfvi431", name: "Emma Brown", email: "emma.brown@school.edu", grade: 10 }
    ];

    for (const student of studentsData) {
      try {
        await prisma.student.create({
          data: student
        });
      } catch (error) {
        if (!error.message.includes('Unique constraint')) {
          throw error;
        }
        console.log(`Student ${student.name} already exists, continuing...`);
      }
    }
    console.log('✓ Students created');

    // 3. Insert Learning Analytics data (successful topics)
    console.log('Inserting learning analytics data...');
    
    const studentIds = [
      "cmfjniab50001oihjqsfvi427",
      "cmfjniab50002oihjqsfvi428", 
      "cmfjniab50003oihjqsfvi429",
      "cmfjniab50004oihjqsfvi430",
      "cmfjniab50005oihjqsfvi431"
    ];
    
    const analyticsData = [
      // Student 1 - Strong in algebra
      {
        student_id: studentIds[0],
        concepts_mastered: ["quadratic_equations", "linear_equations", "factoring"],
        success_rate: 0.85,
        session_duration: 45,
        questions_per_session: 8.5,
        response_time_avg: 12.3,
        difficulty_progression: "progressive"
      },
      {
        student_id: studentIds[0],
        concepts_mastered: ["geometry_basics", "area_calculation", "perimeter"],
        success_rate: 0.92,
        session_duration: 38,
        questions_per_session: 7.2,
        response_time_avg: 10.1,
        difficulty_progression: "advanced"
      },
      // Student 2 - Excellent in geometry
      {
        student_id: studentIds[1],
        concepts_mastered: ["geometry_basics", "area_calculation", "perimeter", "volume"],
        success_rate: 0.94,
        session_duration: 35,
        questions_per_session: 6.8,
        response_time_avg: 9.5,
        difficulty_progression: "advanced"
      },
      {
        student_id: studentIds[1],
        concepts_mastered: ["trigonometry", "sine_cosine", "identities"],
        success_rate: 0.88,
        session_duration: 40,
        questions_per_session: 7.5,
        response_time_avg: 11.2,
        difficulty_progression: "steady"
      },
      // Student 3 - Good with numbers
      {
        student_id: studentIds[2],
        concepts_mastered: ["prime_numbers", "divisibility", "factors"],
        success_rate: 0.90,
        session_duration: 32,
        questions_per_session: 6.8,
        response_time_avg: 11.5,
        difficulty_progression: "steady"
      },
      {
        student_id: studentIds[2],
        concepts_mastered: ["fractions", "decimals", "percentages"],
        success_rate: 0.82,
        session_duration: 42,
        questions_per_session: 9.1,
        response_time_avg: 14.2,
        difficulty_progression: "gradual"
      },
      // Student 4 - Struggling with calculus
      {
        student_id: studentIds[3],
        concepts_mastered: ["basic_algebra", "variables", "expressions"],
        success_rate: 0.75,
        session_duration: 50,
        questions_per_session: 10.2,
        response_time_avg: 16.8,
        difficulty_progression: "gradual"
      },
      {
        student_id: studentIds[3],
        concepts_mastered: ["fractions", "decimals"],
        success_rate: 0.68,
        session_duration: 48,
        questions_per_session: 11.5,
        response_time_avg: 18.3,
        difficulty_progression: "slow"
      },
      // Student 5 - Mixed performance
      {
        student_id: studentIds[4],
        concepts_mastered: ["linear_equations", "graphing", "slope"],
        success_rate: 0.80,
        session_duration: 44,
        questions_per_session: 8.8,
        response_time_avg: 13.7,
        difficulty_progression: "progressive"
      },
      {
        student_id: studentIds[4],
        concepts_mastered: ["word_problems", "problem_solving"],
        success_rate: 0.72,
        session_duration: 52,
        questions_per_session: 9.8,
        response_time_avg: 15.9,
        difficulty_progression: "gradual"
      }
    ];

    for (let i = 0; i < analyticsData.length; i++) {
      const data = analyticsData[i];
      await prisma.learningAnalytics.create({
        data: {
          ...data,
          date: new Date(Date.now() - (i * 5) * 24 * 60 * 60 * 1000)
        }
      });
    }
    console.log('✓ Learning analytics data inserted');

    // 3. Create test chat sessions for multiple students
    console.log('Creating test chat sessions...');
    
    const sessionData = [
      {
        id: "test_session_mock_001",
        student_id: studentIds[0],
        concepts_covered: ["algebra", "geometry", "calculus"]
      },
      {
        id: "test_session_mock_002", 
        student_id: studentIds[1],
        concepts_covered: ["geometry", "trigonometry"]
      },
      {
        id: "test_session_mock_003",
        student_id: studentIds[2], 
        concepts_covered: ["number_theory", "fractions"]
      },
      {
        id: "test_session_mock_004",
        student_id: studentIds[3],
        concepts_covered: ["basic_algebra", "calculus"]
      },
      {
        id: "test_session_mock_005",
        student_id: studentIds[4],
        concepts_covered: ["linear_equations", "word_problems"]
      }
    ];

    for (let i = 0; i < sessionData.length; i++) {
      const session = sessionData[i];
      try {
        await prisma.chatSession.create({
          data: {
            id: session.id,
            student_id: session.student_id,
            started_at: new Date(Date.now() - (10 + i * 2) * 24 * 60 * 60 * 1000),
            ended_at: new Date(Date.now() - (10 + i * 2) * 24 * 60 * 60 * 1000 + 45 * 60 * 1000),
            questions_asked: 12 + i * 3,
            concepts_covered: session.concepts_covered
          }
        });
      } catch (error) {
        if (!error.message.includes('Unique constraint')) {
          throw error;
        }
        console.log(`Chat session ${session.id} already exists, continuing...`);
      }
    }

    // 4. Insert Session Takeaways data (struggling topics)
    console.log('Inserting session takeaways data...');
    
    const takeawaysData = [
      // Student 1 struggles
      {
        session_id: "test_session_mock_001",
        takeaway_type: "difficulty_calculus",
        summary: "Student struggled with derivative concepts",
        key_concepts: ["derivatives", "calculus", "chain_rule"],
        effective_methods: { visual_aids: true, practice_problems: true },
        relevance_score: 0.8
      },
      {
        session_id: "test_session_mock_001",
        takeaway_type: "confusion_complex_algebra",
        summary: "Student had difficulty with complex algebraic expressions",
        key_concepts: ["complex_expressions", "algebra", "factoring"],
        effective_methods: { step_by_step: true, examples: true },
        relevance_score: 0.75
      },
      // Student 2 struggles  
      {
        session_id: "test_session_mock_002",
        takeaway_type: "difficulty_advanced_trig",
        summary: "Student struggled with advanced trigonometric identities",
        key_concepts: ["trigonometry", "identities", "advanced_concepts"],
        effective_methods: { visual_aids: true, practice: true },
        relevance_score: 0.7
      },
      // Student 3 struggles
      {
        session_id: "test_session_mock_003",
        takeaway_type: "confusion_fraction_operations",
        summary: "Student confused about complex fraction operations",
        key_concepts: ["fractions", "operations", "complex_fractions"],
        effective_methods: { guided_practice: true, visual_aids: true },
        relevance_score: 0.8
      },
      // Student 4 struggles (most struggling student)
      {
        session_id: "test_session_mock_004",
        takeaway_type: "difficulty_calculus",
        summary: "Student very confused about calculus fundamentals",
        key_concepts: ["calculus", "derivatives", "limits"],
        effective_methods: { one_on_one: true, basic_review: true },
        relevance_score: 0.9
      },
      {
        session_id: "test_session_mock_004",
        takeaway_type: "struggle_algebraic_thinking",
        summary: "Student needs foundational algebra support",
        key_concepts: ["algebra", "variables", "basic_operations"],
        effective_methods: { remedial_work: true, practice: true },
        relevance_score: 0.85
      },
      // Student 5 struggles
      {
        session_id: "test_session_mock_005",
        takeaway_type: "struggle_word_problems",
        summary: "Student needs help translating word problems to equations",
        key_concepts: ["word_problems", "translation", "problem_solving"],
        effective_methods: { guided_practice: true, templates: true },
        relevance_score: 0.85
      },
      {
        session_id: "test_session_mock_005",
        takeaway_type: "difficulty_graphing",
        summary: "Student confused about graphing linear functions", 
        key_concepts: ["graphing", "linear_functions", "slope"],
        effective_methods: { visual_tools: true, interactive: true },
        relevance_score: 0.7
      }
    ];

    for (let i = 0; i < takeawaysData.length; i++) {
      const data = takeawaysData[i];
      await prisma.sessionTakeaway.create({
        data: {
          ...data,
          created_at: new Date(Date.now() - (i * 2) * 24 * 60 * 60 * 1000),
          embedding_vector: [0.1, 0.2, 0.3, 0.4, 0.5] // Mock embedding vector
        }
      });
    }
    console.log('✓ Session takeaways data inserted');

    console.log('\n✅ All mock data inserted successfully!');
    console.log('\nYou can now test the analytics with:');
    console.log('python build_teacher_overview.py --teacher-id cmfjnia2t0000oihjgwx13py3');

  } catch (error) {
    console.error('Error inserting mock data:', error);
  } finally {
    await prisma.$disconnect();
  }
}

insertMockData();
