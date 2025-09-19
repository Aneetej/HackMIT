import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  console.log("Starting database seed...");

  // --- Teacher ---
  const teacher = await prisma.teacher.create({
    data: {
      name: "Dr. Euler",
      email: "euler@mathengage.ai",
      subject: "Mathematics",
      role: "TEACHER", // enum as string
      supervised_students: [], // will update after creating students
    },
  });

  // --- Students ---
  const alice = await prisma.student.create({
    data: {
      name: "Alice",
      email: "alice@student.ai",
      grade: 10,
      role: "STUDENT", // enum as string
      subject_focus: "algebra",
      learning_style: "visual",
      preferred_content: "videos",
    },
  });

  const bob = await prisma.student.create({
    data: {
      name: "Bob",
      email: "bob@student.ai",
      grade: 11,
      role: "STUDENT", // enum as string
      subject_focus: "geometry",
      learning_style: "kinesthetic",
      preferred_content: "interactive",
    },
  });

  // Update teacher with supervised students
  await prisma.teacher.update({
    where: { id: teacher.id },
    data: {
      supervised_students: [alice.id, bob.id],
    },
  });

  // --- Chat Session for Alice ---
  const session = await prisma.chatSession.create({
    data: {
      student_id: alice.id,
      session_type: "tutoring",
      status: "active",
      difficulty_level: "EASY", // enum as string
      concepts_covered: ["linear equations"],
      questions_asked: 2,
    },
  });

  // --- Chat Messages ---
  await prisma.chatMessage.createMany({
    data: [
      {
        session_id: session.id,
        sender_type: "student",
        agent_type: "student_agent",
        content: "How do I solve 2x + 3 = 7?",
        message_type: "text",
        processed_by: ["student_agent"],
      },
      {
        session_id: session.id,
        sender_type: "agent",
        agent_type: "teacher_agent",
        content: "Subtract 3, then divide by 2. The answer is x = 2.",
        message_type: "text",
        processed_by: ["teacher_agent"],
      },
    ],
  });

  // --- Session Takeaway ---
  await prisma.sessionTakeaway.create({
    data: {
      session_id: session.id,
      takeaway_type: "learning_breakthrough",
      summary: "Alice successfully learned how to solve a basic linear equation.",
      key_concepts: ["linear equations", "basic algebra"],
      effective_methods: { method: "step_by_step_explanation" },
      embedding_vector: [0.12, 0.98, -0.33],
      relevance_score: 0.9,
    },
  });

  // --- Student Preference ---
  await prisma.studentPreference.create({
    data: {
      student_id: bob.id,
      preference_type: "content_format",
      preference_value: "interactive",
      confidence_score: 0.85,
      detection_method: "inferred",
    },
  });

  // --- Learning Analytics ---
  await prisma.learningAnalytics.create({
    data: {
      student_id: alice.id,
      session_duration: 45,
      questions_per_session: 3.5,
      response_time_avg: 4.2,
      concepts_mastered: ["linear equations"],
      difficulty_progression: "improving",
      success_rate: 0.8,
      preferred_session_time: "evening",
    },
  });

  // --- FAQ ---
  await prisma.frequentlyAskedQuestion.create({
    data: {
      question_text: "What is the quadratic formula?",
      category: "algebra",
      frequency_count: 10,
      common_answers: ["x = (-b ± √(b²-4ac)) / 2a"],
      success_rate: 0.95,
      similar_questions: ["quadratic roots", "solve ax²+bx+c=0"],
      keywords: ["quadratic", "formula", "roots"],
    },
  });

  // --- Summary ---
  await prisma.summary.create({
    data: {
      summary: "Alice had a breakthrough solving linear equations during tutoring.",
    },
  });

  console.log("Seeding complete!");
}

main()
  .catch((e) => {
    console.error(" Seed failed:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
