import { PrismaClient } from "@prisma/client";
//import {app} from "./app";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";


dotenv.config();
const app = express();
const prisma = new PrismaClient();

app.use(cors());
app.use(express.json());

// Test route
app.get("/", (req, res) => {
    res.send("API is running");
});

// Endpoint : Fetching students sep
app.get("/students", async (req, res)=> {
    const students = await prisma.student.findMany();
    res.json(students);
});

// Endpoint : Fetching teachers sep
app.get("/teachers", async (req, res)=> {
    const teachers = await prisma.teacher.findMany();
    res.json(teachers);
});

// Endpoint : Try fetching students and teachers merged 
app.get("/users", async (req, res) => {
    const students = await prisma.student.findMany();
    const teachers = await prisma.teacher.findMany();
  
    const users = [
      ...students.map(s => ({ id: s.id, name: s.name, role: "STUDENT" })),
      ...teachers.map(t => ({ id: t.id, name: t.name, role: "TEACHER" }))
    ];
  
    res.json(users);
});
  
// Endpoint : Fetching summaries 
app.get("/summaries", async (req, res) => {
    const summaries = await prisma.summary.findMany();
    res.json(summaries);
});

// Endpoint : Creating summary 
app.post("/summaries", async (req, res) => {
    const {summary} = req.body;
    const newSummary = await prisma.summary.create({
        data: {summary}
    });
    res.json(newSummary);
});

const port = process.env.PORT || 4000 ;

app.listen(port, ()=> console.log(`API up on :${port}`) );

// nice shutdown 
process.on("SIGINT", async () => {await prisma.$disconnect(); process.exit(0);});
process.on("SIGTERM", async () => {await prisma.$disconnect(); process.exit(0);});

