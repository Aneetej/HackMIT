import { PrismaClient } from "@prisma/client";
//import {app} from "./app";
import cors from "cors";
import dotenv from "dotenv";
import express, { Request, Response } from "express";


dotenv.config();
const app = express();
const prisma = new PrismaClient();

app.use(cors());
app.use(express.json());

// Test route
app.get("/", (req: Request, res: Response) => {
    res.send("API is running");
});

// Endpoint : Fetching students sep
app.get("/students", async (req: Request, res: Response)=> {
    const students = await prisma.student.findMany();
    res.json(students);
});

// Endpoint : Fetching teachers sep
app.get("/teachers", async (req: Request, res: Response)=> {
    const teachers = await prisma.teacher.findMany();
    res.json(teachers);
});

// Endpoint : Try fetching students and teachers merged 
app.get("/users", async (req: Request, res: Response) => {
    const students = await prisma.student.findMany();
    const teachers = await prisma.teacher.findMany();
  
    const users = [
      ...students.map((s: any) => ({ id: s.id, name: s.name, role: "STUDENT" })),
      ...teachers.map((t: any) => ({ id: t.id, name: t.name, role: "TEACHER" }))
    ];
  
    res.json(users);
});
  
// Endpoint : Fetching summaries 
app.get("/summaries", async (req: Request, res: Response) => {
    const summaries = await prisma.summary.findMany();
    res.json(summaries);
});

// Endpoint : Creating summary 
app.post("/summaries", async (req: Request, res: Response) => {
    const {summary} = req.body;
    const newSummary = await prisma.summary.create({
        data: {summary}
    });
    res.json(newSummary);
});

// STUDENT API ROUTES - Database integrated endpoints
// Endpoint: Get student info and enrolled classes
app.get("/api/student/:studentId", async (req: Request, res: Response) => {
    const { studentId } = req.params;
    
    try {
        const student = await prisma.student.findUnique({
            where: { id: studentId },
            include: {
                chat_sessions: {
                    select: {
                        id: true,
                        session_type: true
                    },
                    distinct: ['session_type']
                }
            }
        });

        if (!student) {
            return res.status(404).json({ message: "Student not found" });
        }

        // Convert chat sessions to class format for frontend compatibility
        const classes = student.chat_sessions.map((session: any) => ({
            classId: session.id,
            className: session.session_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
        }));

        res.json({
            interests: student.subject_focus,
            learningStyle: student.learning_style,
            classes
        });
    } catch (error) {
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Get class chat history
app.get("/api/student/:studentId/class/:classId", async (req: Request, res: Response) => {
    const { studentId, classId } = req.params;
    
    try {
        const session = await prisma.chatSession.findFirst({
            where: {
                id: classId,
                student_id: studentId
            },
            include: {
                messages: {
                    orderBy: { timestamp: 'asc' }
                }
            }
        });

        if (!session) {
            return res.status(404).json({ message: "Class not found" });
        }

        const chatHistory = session.messages.map((msg: any) => ({
            id: msg.id,
            message: msg.content,
            sender: msg.sender_type === 'student' ? 'user' : 'assistant',
            timestamp: msg.timestamp.toISOString()
        }));

        res.json({
            classId: session.id,
            className: session.session_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            chatHistory
        });
    } catch (error) {
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Send message and get AI response
app.post("/api/student/:studentId/class/:classId/message", async (req: Request, res: Response) => {
    const { studentId, classId } = req.params;
    const { message } = req.body;
    
    try {
        // Save user message
        const userMessage = await prisma.chatMessage.create({
            data: {
                session_id: classId,
                sender_type: 'student',
                content: message,
                message_type: 'text'
            }
        });

        // For now, create a simple AI response (replace with actual AI integration later)
        const aiResponse = await prisma.chatMessage.create({
            data: {
                session_id: classId,
                sender_type: 'agent',
                agent_type: 'student_agent',
                content: `I understand you're asking about "${message}". Let me help you with that.`,
                message_type: 'text'
            }
        });

        // Update session metrics
        await prisma.chatSession.update({
            where: { id: classId },
            data: {
                questions_asked: { increment: 1 }
            }
        });

        res.json({
            id: aiResponse.id,
            message: aiResponse.content,
            sender: 'assistant',
            timestamp: aiResponse.timestamp.toISOString()
        });
    } catch (error) {
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Join/Create new class session
app.post("/api/student/join-class", async (req: Request, res: Response) => {
    const { studentId, classCode } = req.body;
    
    try {
        // Validate student exists
        const student = await prisma.student.findUnique({
            where: { id: studentId }
        });

        if (!student) {
            return res.status(404).json({ message: "Student not found" });
        }

        // Create new chat session (treating classCode as session type)
        const sessionType = classCode.toLowerCase().replace(/\s+/g, '_');
        const newSession = await prisma.chatSession.create({
            data: {
                student_id: studentId,
                session_type: sessionType,
                status: 'active'
            }
        });

        res.json({
            classId: newSession.id,
            className: sessionType.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            chatHistory: []
        });
    } catch (error) {
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Update student preferences
app.put("/api/student/:studentId/preferences", async (req: Request, res: Response) => {
    const { studentId } = req.params;
    const { interests, learningStyle } = req.body;
    
    try {
        await prisma.student.update({
            where: { id: studentId },
            data: {
                subject_focus: interests,
                learning_style: learningStyle
            }
        });

        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Create new student (registration)
app.post("/api/student/register", async (req: Request, res: Response) => {
    const { email, name, grade, subject_focus, learning_style } = req.body;
    
    try {
        // Check if student already exists
        const existingStudent = await prisma.student.findUnique({
            where: { email }
        });

        if (existingStudent) {
            return res.status(409).json({ 
                message: "Student with this email already exists",
                studentId: existingStudent.id
            });
        }

        // Create new student
        const newStudent = await prisma.student.create({
            data: {
                email,
                name,
                grade: parseInt(grade),
                subject_focus: subject_focus || "general_math",
                learning_style: learning_style || "mixed",
                preferred_content: "mixed",
                role: "STUDENT"
            }
        });

        res.status(201).json({
            success: true,
            studentId: newStudent.id,
            student: {
                id: newStudent.id,
                name: newStudent.name,
                email: newStudent.email,
                grade: newStudent.grade,
                subject_focus: newStudent.subject_focus,
                learning_style: newStudent.learning_style
            }
        });
    } catch (error) {
        console.error("Student registration error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Create new teacher (registration)
app.post("/api/teacher/register", async (req: Request, res: Response) => {
    const { email, name, subject } = req.body;
    
    try {
        // Check if teacher already exists
        const existingTeacher = await prisma.teacher.findUnique({
            where: { email }
        });

        if (existingTeacher) {
            return res.status(409).json({ 
                message: "Teacher with this email already exists",
                teacherId: existingTeacher.id
            });
        }

        // Create new teacher
        const newTeacher = await prisma.teacher.create({
            data: {
                email,
                name,
                subject,
                role: "TEACHER",
                supervised_students: []
            }
        });

        res.status(201).json({
            success: true,
            teacherId: newTeacher.id,
            teacher: {
                id: newTeacher.id,
                name: newTeacher.name,
                email: newTeacher.email,
                subject: newTeacher.subject
            }
        });
    } catch (error) {
        console.error("Teacher registration error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Student sign-in (check if student exists by email)
app.post("/api/student/signin", async (req: Request, res: Response) => {
    const { email } = req.body;
    
    try {
        const student = await prisma.student.findUnique({
            where: { email }
        });

        if (!student) {
            return res.status(404).json({ 
                message: "No account found with this email address"
            });
        }

        res.json({
            success: true,
            studentId: student.id,
            student: {
                id: student.id,
                name: student.name,
                email: student.email,
                grade: student.grade,
                subject_focus: student.subject_focus,
                learning_style: student.learning_style
            }
        });
    } catch (error) {
        console.error("Student sign-in error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Teacher sign-in (check if teacher exists by email)
app.post("/api/teacher/signin", async (req: Request, res: Response) => {
    const { email } = req.body;
    
    try {
        const teacher = await prisma.teacher.findUnique({
            where: { email }
        });

        if (!teacher) {
            return res.status(404).json({ 
                message: "No account found with this email address"
            });
        }

        res.json({
            success: true,
            teacherId: teacher.id,
            teacher: {
                id: teacher.id,
                name: teacher.name,
                email: teacher.email,
                subject: teacher.subject
            }
        });
    } catch (error) {
        console.error("Teacher sign-in error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

const port = process.env.PORT || 4000 ;

app.listen(port, ()=> console.log(`API up on :${port}`) );

// nice shutdown 
process.on("SIGINT", async () => {await prisma.$disconnect(); process.exit(0);});
process.on("SIGTERM", async () => {await prisma.$disconnect(); process.exit(0);});

