import { PrismaClient } from "@prisma/client";
//import {app} from "./app";
import cors from "cors";
import dotenv from "dotenv";
import express, { Request, Response } from "express";
import axios from "axios";

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

// GET /api/student/:studentId/classes - Get all classes for a student (MUST come before /api/student/:studentId)
app.get('/api/student/:studentId/classes', async (req, res) => {
  try {
    const { studentId } = req.params;

    const student = await prisma.student.findUnique({
      where: { id: studentId },
      include: {
        classrooms: {
          include: {
            teacher: {
              select: { id: true, name: true }
            },
            _count: {
              select: { students: true }
            }
          }
        }
      }
    });

    if (!student) {
      return res.status(404).json({ error: 'Student not found' });
    }

    const classesWithDetails = student.classrooms.map((cls: any) => ({
      ...cls,
      studentCount: cls._count.students,
      teacherName: cls.teacher?.name || 'Unknown Teacher'
    }));

    res.json({ success: true, classes: classesWithDetails });
  } catch (error) {
    console.error('Error fetching student classes:', error);
    res.status(500).json({ error: 'Failed to fetch classes' });
  }
});

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

app.post("/api/student/:studentId/class/:classId/message", async (req: Request, res: Response) => {
    console.log('Message endpoint hit');
    
    try {
        const { studentId, classId } = req.params;
        const { message } = req.body;
        
        // Validate required parameters
        if (!studentId || !classId || !message) {
            console.error('Missing required parameters:', { studentId, classId, message });
            return res.status(400).json({ 
                error: "Missing required parameters",
                details: { studentId: !!studentId, classId: !!classId, message: !!message }
            });
        }
        
        console.log('Processing message:', { studentId, classId, messageLength: message.length });

        // Find the ChatSession using studentId and classId
        let chatSession;
        try {
            chatSession = await prisma.chatSession.findFirst({
                where: {
                    student_id: studentId,
                    classId: classId
                }
            });
            
        console.log("CHRWF, ", chatSession)
        } catch (sessionError) {
            console.error('Error handling ChatSession:', sessionError);
            return res.status(500).json({ 
                error: "Database error with chat session",
                details: sessionError instanceof Error ? sessionError.message : 'Unknown session error'
            });
        }

        // Save user message with error handling (using the actual session_id)
        let userMessage;
        try {
            userMessage = await prisma.chatMessage.create({
                data: {
                    session_id: chatSession?.id, // Use the actual ChatSession ID
                    sender_type: 'student',
                    content: message,
                    message_type: 'text'
                }
            });
            console.log('User message saved:', userMessage.id);
        } catch (dbError) {
            console.error('Database error saving user message:', dbError);
            return res.status(500).json({ 
                error: "Database error saving message",
                details: dbError instanceof Error ? dbError.message : 'Unknown database error'
            });
        }

        // Call FastAPI to get AI response
        let aiResponseContent = `I understand you're asking about "${message}". Let me help you with that.`; // Fallback response
        
        try {
            console.log('Calling FastAPI...');
            const fastApiResponse = await axios.post('http://localhost:8000/api/chat/message', {
                chat_session_id: chatSession?.id,
                student_id: studentId,
                user_message: message,
                class_id: classId
            }, {
                timeout: 30000, // 30 second timeout
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (fastApiResponse.status === 200) {
                const fastApiData = fastApiResponse.data;
                aiResponseContent = fastApiData.response || aiResponseContent;
                console.log('FastAPI response received', aiResponseContent);
            } else {
                console.error('FastAPI call failed:', fastApiResponse.status, fastApiResponse.statusText);
            }
        } catch (fetchError) {
            console.error('Error calling FastAPI:', {
                message: fetchError instanceof Error ? fetchError.message : 'Unknown error',
                code: axios.isAxiosError(fetchError) ? fetchError.code : 'Unknown',
                response: axios.isAxiosError(fetchError) ? fetchError.response?.data : 'No response data'
            });
            // Will use fallback response - this is fine, don't return error here
        }

        // Save AI response to database
        let aiResponse;
        try {
            aiResponse = await prisma.chatMessage.create({
                data: {
                    session_id: chatSession.id, // Use the actual ChatSession ID
                    sender_type: 'agent',
                    agent_type: 'student_agent',
                    content: aiResponseContent,
                    message_type: 'text'
                }
            });
            console.log('AI response saved:', aiResponse.id);
        } catch (dbError) {
            console.error('Database error saving AI response:', dbError);
            return res.status(500).json({ 
                error: "Database error saving AI response",
                details: dbError instanceof Error ? dbError.message : 'Unknown database error'
            });
        }

        // Update session metrics
        try {
            await prisma.chatSession.update({
                where: { id: chatSession.id },
                data: {
                    questions_asked: { increment: 1 }
                }
            });
            console.log('Session metrics updated');
        } catch (dbError) {
            console.error('Error updating session metrics:', dbError);
            // Don't fail the request for this, just log it
        }

        const response = {
            id: aiResponse.id,
            message: aiResponse.content,
            sender: 'assistant',
            timestamp: aiResponse.timestamp.toISOString()
        };
        
        console.log('Sending successful response');
        res.json(response);
        
    } catch (error) {
        console.error("Unexpected error in message endpoint:", {
            message: error instanceof Error ? error.message : 'Unknown error',
            stack: error instanceof Error ? error.stack : 'No stack trace',
            type: typeof error,
            error
        });
        
        res.status(500).json({ 
            error: "Internal server error",
            message: error instanceof Error ? error.message : 'Unknown error occurred'
        });
    }
});


// Student Management Endpoints

// POST /api/student/join-class - Join a class and create chat session
app.post('/api/student/join-class', async (req, res) => {
  try {
    const { classId, studentId } = req.body;

    if (!classId || !studentId) {
      return res.status(400).json({ error: 'Class ID and Student ID are required' });
    }

    // Check if class exists
    const classData = await prisma.classroom.findUnique({
      where: { id: classId }
    });

    if (!classData) {
      return res.status(404).json({ error: 'Invalid class ID' });
    }

    // Check if student exists
    const student = await prisma.student.findUnique({
      where: { id: studentId }
    });

    if (!student) {
      return res.status(404).json({ error: 'Student already in class' });
    }

    // Add student to class
    await prisma.classroom.update({
      where: { id: classId },
      data: {
        students: {
          connect: { id: studentId }
        }
      }
    });

    // Create a new chat session for the student and class
    const chatSession = await prisma.chatSession.create({
      data: {
        student_id: studentId,
        classId: classId
      }
    });

    res.json({ 
      success: true, 
      message: 'Successfully joined class',
      classTitle: classData.name,
      chatSessionId: chatSession.id
    });
  } catch (error) {
    console.error('Error joining class:', error);
    res.status(500).json({ error: 'Failed to join class' });
  }
});


// POST /api/teacher/:teacherId/class - Create a new class
app.post('/api/teacher/:teacherId/class', async (req, res) => {
  try {
    const { teacherId } = req.params;
    const { name, restrictions, teachingStyle, studentGrade, subject, otherNotes } = req.body;

    // Generate a 6-digit class ID
    const generateClassId = () => {
      return Math.floor(100000 + Math.random() * 900000).toString();
    };

    let classId = generateClassId();
    
    // Ensure unique class ID
    let existingClass = await prisma.classroom.findUnique({ where: { id: classId } });
    while (existingClass) {
      classId = generateClassId();
      existingClass = await prisma.classroom.findUnique({ where: { id: classId } });
    }

    const newClass = await prisma.classroom.create({
      data: {
        id: classId,
        name,
        restrictions,
        teachingStyle,
        studentGrade,
        subject,
        otherNotes,
        teacherId,
      },
    });

    res.json({ success: true, class: newClass });
  } catch (error) {
    console.error('Error creating class:', error);
    res.status(500).json({ error: 'Failed to create class' });
  }
});

// GET /api/teacher/:teacherId/classes - Get all classes for a teacher
app.get('/api/teacher/:teacherId/classes', async (req, res) => {
  try {
    const { teacherId } = req.params;

    const classes = await prisma.classroom.findMany({
      where: { teacherId },
      include: {
        _count: {
          select: { students: true }
        }
      }
    });

    const classesWithCount = classes.map(cls => ({
      ...cls,
      studentCount: cls._count.students
    }));

    res.json({ success: true, classes: classesWithCount });
  } catch (error) {
    console.error('Error fetching classes:', error);
    res.status(500).json({ error: 'Failed to fetch classes' });
  }
});

// GET /api/class/:classId - Get a single class by ID
app.get('/api/classroom/:classId', async (req, res) => {
  try {
    const { classId } = req.params;

    const classData = await prisma.classroom.findUnique({
      where: { id: classId },
      include: {
        _count: {
          select: { students: true }
        }
      }
    });

    if (!classData) {
      return res.status(404).json({ error: 'Class not found' });
    }

    const classWithCount = {
      ...classData,
      studentCount: classData._count.students
    };

    res.json({ success: true, class: classWithCount });
  } catch (error) {
    console.error('Error fetching class:', error);
    res.status(500).json({ error: 'Failed to fetch class' });
  }
});

// PUT /api/class/:classId - Update class details
app.put('/api/classroom/:classId', async (req, res) => {
  try {
    const { classId } = req.params;
    const { name, restrictions, teachingStyle, studentGrade, subject, otherNotes } = req.body;

    const updatedClass = await prisma.classroom.update({
      where: { id: classId },
      data: {
        name,
        restrictions,
        teachingStyle,
        studentGrade,
        subject,
        otherNotes,
      },
    });

    res.json({ success: true, class: updatedClass });
  } catch (error: any) {
    console.error('Error updating class:', error);
    if (error.code === 'P2025') {
      res.status(404).json({ error: 'Class not found' });
    } else {
      res.status(500).json({ error: 'Failed to update class' });
    }
  }
});

// DELETE /api/class/:classId - Delete a class
app.delete('/api/classroom/:classId', async (req, res) => {
  try {
    const { classId } = req.params;

    await prisma.classroom.delete({
      where: { id: classId },
    });

    res.json({ success: true, message: 'Class deleted successfully' });
  } catch (error: any) {
    console.error('Error deleting class:', error);
    if (error.code === 'P2025') {
      res.status(404).json({ error: 'Class not found' });
    } else {
      res.status(500).json({ error: 'Failed to delete class' });
    }
  }
});

// GET /api/class/:classId/students - Get all students for a specific class
app.get('/api/classroom/:classId/students', async (req, res) => {
  try {
    const { classId } = req.params;

    // First verify the class exists
    const classExists = await prisma.classroom.findUnique({
      where: { id: classId },
    });

    if (!classExists) {
      return res.status(404).json({ error: 'Class not found' });
    }

    // Get all students enrolled in this class through chat sessions
    const students = await prisma.student.findMany({
      where: {
        chat_sessions: {
          some: {
            classId: classId
          }
        }
      },
      select: {
        id: true,
        name: true,
        email: true,
        grade: true,
        subject_focus: true,
        learning_style: true,
        preferred_content: true,
        created_at: true,
        chat_sessions: {
          where: {
            classId: classId
          },
          select: {
            id: true,
            questions_asked: true,
            started_at: true,
            ended_at: true,
            status: true
          }
        }
      },
      orderBy: {
        name: 'asc'
      }
    });

    res.json({ 
      success: true, 
      students: students.map(student => ({
        ...student,
        sessionInfo: student.chat_sessions[0] // Since we filter by classId, there should be only one
      }))
    });
  } catch (error) {
    console.error('Error fetching class students:', error);
    res.status(500).json({ error: 'Failed to fetch students' });
  }
});

// GET /api/class/:classId/insights/messages - Get average messages per student over last 7 days
app.get('/api/classroom/:classId/insights/messages', async (req, res) => {
  try {
    const { classId } = req.params;

    // First verify the class exists
    const classExists = await prisma.classroom.findUnique({
      where: { id: classId },
    });

    if (!classExists) {
      return res.status(404).json({ error: 'Class not found' });
    }

    // Calculate date 7 days ago
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    // Get message statistics for students in this class over the last 7 days
    const messageStats = await prisma.student.findMany({
      where: {
        chat_sessions: {
          some: {
            classId: classId
          }
        }
      },
      select: {
        id: true,
        name: true,
        chat_sessions: {
          where: {
            classId: classId
          },
          select: {
            messages: {
              where: {
                timestamp: {
                  gte: sevenDaysAgo
                },
                sender_type: 'student'
              },
              select: {
                id: true,
                timestamp: true
              }
            }
          }
        }
      }
    });

    // Calculate average messages per student
    const studentMessageCounts = messageStats.map(student => {
      const totalMessages = student.chat_sessions.reduce((total: number, session: any) => {
        return total + session.messages.length;
      }, 0);
      
      return {
        studentId: student.id,
        studentName: student.name,
        messageCount: totalMessages
      };
    });

    const totalMessages = studentMessageCounts.reduce((sum, student) => sum + student.messageCount, 0);
    const averageMessages = studentMessageCounts.length > 0 ? totalMessages / studentMessageCounts.length : 0;

    res.json({
      success: true,
      data: {
        averageMessagesPerStudent: Math.round(averageMessages * 100) / 100, // Round to 2 decimal places
        totalStudents: studentMessageCounts.length,
        totalMessages: totalMessages,
        studentBreakdown: studentMessageCounts,
        dateRange: {
          from: sevenDaysAgo.toISOString(),
          to: new Date().toISOString()
        }
      }
    });
  } catch (error) {
    console.error('Error fetching message insights:', error);
    res.status(500).json({ error: 'Failed to fetch message insights' });
  }
});

// GET /api/class/:classId/student/:studentId/daily-usage - Get daily usage for a specific student over last 7 days
app.get('/api/classroom/:classId/student/:studentId/daily-usage', async (req, res) => {
  try {
    const { classId, studentId } = req.params;

    // First verify the class and student exist
    const classExists = await prisma.classroom.findUnique({
      where: { id: classId },
    });

    if (!classExists) {
      return res.status(404).json({ error: 'Class not found' });
    }

    const studentExists = await prisma.student.findUnique({
      where: { id: studentId },
    });

    if (!studentExists) {
      return res.status(404).json({ error: 'Student not found' });
    }

    // Calculate date 7 days ago
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    // Get all messages from this student in this class over the last 7 days
    const messages = await prisma.chatMessage.findMany({
      where: {
        sender_type: 'student',
        timestamp: {
          gte: sevenDaysAgo
        },
        session: {
          student_id: studentId,
          classId: classId
        }
      },
      select: {
        id: true,
        timestamp: true,
        content: true
      },
      orderBy: {
        timestamp: 'asc'
      }
    });

    // Group messages by day
    const dailyUsage = [];
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      
      const dayMessages = messages.filter(message => {
        const messageDate = new Date(message.timestamp);
        return messageDate >= date && messageDate < nextDate;
      });

      dailyUsage.push({
        day: days[date.getDay()],
        date: date.toISOString().split('T')[0],
        messageCount: dayMessages.length,
        messages: dayMessages
      });
    }

    const totalMessages = messages.length;
    const averageDaily = totalMessages / 7;

    res.json({
      success: true,
      data: {
        studentId: studentId,
        studentName: studentExists.name,
        classId: classId,
        dailyUsage: dailyUsage,
        totalMessages: totalMessages,
        averageDailyMessages: Math.round(averageDaily * 100) / 100,
        dateRange: {
          from: sevenDaysAgo.toISOString(),
          to: new Date().toISOString()
        }
      }
    });
  } catch (error) {
    console.error('Error fetching student daily usage:', error);
    res.status(500).json({ error: 'Failed to fetch student daily usage' });
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

// Insight endpoints

// Endpoint: Create a new insight for a specific class
app.post("/api/classrooms/:classId/insights", async (req: Request, res: Response) => {
    const { classId } = req.params;
    const { title, description } = req.body;

    try {
        if (!title || !description) {
            return res.status(400).json({ 
                message: "Title and description are required" 
            });
        }

        // Verify class exists
        const classExists = await prisma.classroom.findUnique({
            where: { id: classId }
        });

        if (!classExists) {
            return res.status(404).json({ 
                message: "Class not found" 
            });
        }

        const insight = await prisma.insight.create({
            data: {
                title,
                description,
                classId
            }
        });

        res.status(201).json({
            success: true,
            insight
        });
    } catch (error) {
        console.error("Create insight error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Fetch all insights for a specific class
app.get("/api/classrooms/:classId/insights", async (req: Request, res: Response) => {
    const { classId } = req.params;

    try {
        // Verify class exists
        const classExists = await prisma.classroom.findUnique({
            where: { id: classId }
        });

        if (!classExists) {
            return res.status(404).json({ 
                message: "Class not found" 
            });
        }

        const insights = await prisma.insight.findMany({
            where: { classId },
            orderBy: { id: 'desc' } // Most recent first
        });

        res.json({
            success: true,
            insights
        });
    } catch (error) {
        console.error("Fetch insights error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Update an existing insight
app.put("/api/insights/:insightId", async (req: Request, res: Response) => {
    const { insightId } = req.params;
    const { title, description } = req.body;

    try {
        if (!title || !description) {
            return res.status(400).json({ 
                message: "Title and description are required" 
            });
        }

        // Check if insight exists
        const existingInsight = await prisma.insight.findUnique({
            where: { id: insightId }
        });

        if (!existingInsight) {
            return res.status(404).json({ 
                message: "Insight not found" 
            });
        }

        const updatedInsight = await prisma.insight.update({
            where: { id: insightId },
            data: {
                title,
                description
            }
        });

        res.json({
            success: true,
            insight: updatedInsight
        });
    } catch (error) {
        console.error("Update insight error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Delete an insight
app.delete("/api/insights/:insightId", async (req: Request, res: Response) => {
    const { insightId } = req.params;

    try {
        // Check if insight exists
        const existingInsight = await prisma.insight.findUnique({
            where: { id: insightId }
        });

        if (!existingInsight) {
            return res.status(404).json({ 
                message: "Insight not found" 
            });
        }

        await prisma.insight.delete({
            where: { id: insightId }
        });

        res.json({
            success: true,
            message: "Insight deleted successfully"
        });
    } catch (error) {
        console.error("Delete insight error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Note endpoints

// Endpoint: Get or create note for a student in a class
app.get("/api/classrooms/:classId/students/:studentId/note", async (req: Request, res: Response) => {
    const { classId, studentId } = req.params;

    try {
        // Verify class and student exist
        const classExists = await prisma.classroom.findUnique({
            where: { id: classId }
        });

        if (!classExists) {
            return res.status(404).json({ 
                message: "Class not found" 
            });
        }

        const studentExists = await prisma.student.findUnique({
            where: { id: studentId }
        });

        if (!studentExists) {
            return res.status(404).json({ 
                message: "Student not found" 
            });
        }

        // Try to find existing note
        let note = await prisma.note.findFirst({
            where: {
                classId,
                studentId
            }
        });

        // If no note exists, create an empty one
        if (!note) {
            note = await prisma.note.create({
                data: {
                    content: "",
                    classId,
                    studentId
                }
            });
        }

        res.json({
            success: true,
            note
        });
    } catch (error) {
        console.error("Get note error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// Endpoint: Update note for a student in a class
app.put("/api/classrooms/:classId/students/:studentId/note", async (req: Request, res: Response) => {
    const { classId, studentId } = req.params;
    const { content } = req.body;

    try {
        if (content === undefined) {
            return res.status(400).json({ 
                message: "Content is required" 
            });
        }

        // Verify class and student exist
        const classExists = await prisma.classroom.findUnique({
            where: { id: classId }
        });

        if (!classExists) {
            return res.status(404).json({ 
                message: "Class not found" 
            });
        }

        const studentExists = await prisma.student.findUnique({
            where: { id: studentId }
        });

        if (!studentExists) {
            return res.status(404).json({ 
                message: "Student not found" 
            });
        }

        // Try to find existing note
        let note = await prisma.note.findFirst({
            where: {
                classId,
                studentId
            }
        });

        if (note) {
            // Update existing note
            note = await prisma.note.update({
                where: { id: note.id },
                data: { content }
            });
        } else {
            // Create new note
            note = await prisma.note.create({
                data: {
                    content,
                    classId,
                    studentId
                }
            });
        }

        res.json({
            success: true,
            note
        });
    } catch (error) {
        console.error("Update note error:", error);
        res.status(500).json({ message: "Internal server error" });
    }
});

// PUT /api/student/:studentId/preferences - Update student preferences
app.put('/api/student/:studentId/preferences', async (req, res) => {
  try {
    const { studentId } = req.params;
    const { interests, learningStyle } = req.body;

    // Validate required parameters
    if (!studentId && !interests && !learningStyle) {
      return res.status(400).json({ 
        error: "Missing required parameters",
        details: { studentId: !!studentId, interests: !!interests, learningStyle: !!learningStyle }
      });
    }

    // Update student preferences in database
    const updatedStudent = await prisma.student.update({
      where: { id: studentId },
      data: {
        subject_focus: interests,
        learning_style: learningStyle,
        updated_at: new Date()
      }
    });

    console.log(`Updated preferences for student ${studentId}:`, {
      subject_focus: interests,
      learning_style: learningStyle
    });

    res.json({ 
      success: true, 
      message: 'Preferences updated successfully',
      student: {
        id: updatedStudent.id,
        subject_focus: updatedStudent.subject_focus,
        learning_style: updatedStudent.learning_style
      }
    });

  } catch (error) {
    console.error('Error updating student preferences:', error);
    
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Student not found' });
    }
    
    res.status(500).json({ error: 'Failed to update preferences' });
  }
});

const port = process.env.PORT || 4000 ;

app.listen(port, ()=> console.log(`API up on :${port}`) );

// nice shutdown 
process.on("SIGINT", async () => {await prisma.$disconnect(); process.exit(0);});
process.on("SIGTERM", async () => {await prisma.$disconnect(); process.exit(0);});
