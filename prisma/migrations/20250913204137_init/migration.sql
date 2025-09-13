-- CreateEnum
CREATE TYPE "public"."Role" AS ENUM ('STUDENT', 'TEACHER');

-- CreateEnum
CREATE TYPE "public"."Difficulty" AS ENUM ('EASY', 'MEDIUM', 'HARD');

-- CreateTable
CREATE TABLE "public"."students" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "role" "public"."Role" NOT NULL DEFAULT 'STUDENT',
    "email" TEXT NOT NULL,
    "grade" INTEGER NOT NULL,
    "subject_focus" TEXT NOT NULL DEFAULT 'general_math',
    "learning_style" TEXT NOT NULL DEFAULT 'mixed',
    "preferred_content" TEXT NOT NULL DEFAULT 'mixed',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "students_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."teachers" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "role" "public"."Role" NOT NULL DEFAULT 'TEACHER',
    "email" TEXT NOT NULL,
    "subject" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "supervised_students" TEXT[],

    CONSTRAINT "teachers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."chat_sessions" (
    "id" TEXT NOT NULL,
    "student_id" TEXT NOT NULL,
    "session_type" TEXT NOT NULL DEFAULT 'tutoring',
    "started_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ended_at" TIMESTAMP(3),
    "status" TEXT NOT NULL DEFAULT 'active',
    "questions_asked" INTEGER NOT NULL DEFAULT 0,
    "concepts_covered" TEXT[],
    "difficulty_level" "public"."Difficulty" NOT NULL DEFAULT 'EASY',
    "success_indicators" JSONB,

    CONSTRAINT "chat_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."chat_messages" (
    "id" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "sender_type" TEXT NOT NULL,
    "agent_type" TEXT,
    "content" TEXT NOT NULL,
    "message_type" TEXT NOT NULL DEFAULT 'text',
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processed_by" TEXT[],
    "flagged_content" BOOLEAN NOT NULL DEFAULT false,
    "learning_indicators" JSONB,

    CONSTRAINT "chat_messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."student_preferences" (
    "id" TEXT NOT NULL,
    "student_id" TEXT NOT NULL,
    "preference_type" TEXT NOT NULL,
    "preference_value" TEXT NOT NULL,
    "confidence_score" DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    "last_updated" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "detection_method" TEXT NOT NULL,

    CONSTRAINT "student_preferences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."learning_analytics" (
    "id" TEXT NOT NULL,
    "student_id" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "session_duration" INTEGER NOT NULL,
    "questions_per_session" DOUBLE PRECISION NOT NULL,
    "response_time_avg" DOUBLE PRECISION NOT NULL,
    "concepts_mastered" TEXT[],
    "difficulty_progression" TEXT NOT NULL,
    "success_rate" DOUBLE PRECISION NOT NULL,
    "preferred_session_time" TEXT,
    "interaction_patterns" JSONB,

    CONSTRAINT "learning_analytics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."frequently_asked_questions" (
    "id" TEXT NOT NULL,
    "question_text" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "frequency_count" INTEGER NOT NULL DEFAULT 1,
    "first_asked" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_asked" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "common_answers" JSONB,
    "success_rate" DOUBLE PRECISION,
    "similar_questions" TEXT[],
    "keywords" TEXT[],

    CONSTRAINT "frequently_asked_questions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."session_takeaways" (
    "id" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "takeaway_type" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "key_concepts" TEXT[],
    "effective_methods" JSONB NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "embedding_vector" DOUBLE PRECISION[],
    "relevance_score" DOUBLE PRECISION,

    CONSTRAINT "session_takeaways_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."analytics_requests" (
    "id" TEXT NOT NULL,
    "teacher_id" TEXT NOT NULL,
    "request_type" TEXT NOT NULL,
    "parameters" JSONB NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "results" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),

    CONSTRAINT "analytics_requests_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."agent_interactions" (
    "id" TEXT NOT NULL,
    "session_id" TEXT,
    "agent_type" TEXT NOT NULL,
    "interaction_type" TEXT NOT NULL,
    "input_data" JSONB NOT NULL,
    "output_data" JSONB NOT NULL,
    "processing_time" DOUBLE PRECISION NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "success" BOOLEAN NOT NULL DEFAULT true,
    "error_message" TEXT,

    CONSTRAINT "agent_interactions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "students_email_key" ON "public"."students"("email");

-- CreateIndex
CREATE UNIQUE INDEX "teachers_email_key" ON "public"."teachers"("email");

-- CreateIndex
CREATE UNIQUE INDEX "chat_messages_id_key" ON "public"."chat_messages"("id");

-- AddForeignKey
ALTER TABLE "public"."chat_sessions" ADD CONSTRAINT "chat_sessions_student_id_fkey" FOREIGN KEY ("student_id") REFERENCES "public"."students"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."chat_messages" ADD CONSTRAINT "chat_messages_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."chat_sessions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."student_preferences" ADD CONSTRAINT "student_preferences_student_id_fkey" FOREIGN KEY ("student_id") REFERENCES "public"."students"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."learning_analytics" ADD CONSTRAINT "learning_analytics_student_id_fkey" FOREIGN KEY ("student_id") REFERENCES "public"."students"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."session_takeaways" ADD CONSTRAINT "session_takeaways_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."chat_sessions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."analytics_requests" ADD CONSTRAINT "analytics_requests_teacher_id_fkey" FOREIGN KEY ("teacher_id") REFERENCES "public"."teachers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
