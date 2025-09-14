'use client';

import { useState, useEffect } from 'react';
import StudentSidebar from '../../components/StudentSidebar';
import StudentChat from '../../components/StudentChat';
import { studentApi, ClassInfo } from '../../lib/student/apis';
import styles from './page.module.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  classId: string;
}

export default function StudentPage() {
  const [activeTab, setActiveTab] = useState('Classes');
  const [joinCode, setJoinCode] = useState('');
  const [chatMessage, setChatMessage] = useState('');
  const [interests, setInterests] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Get student ID from localStorage
  const [studentId, setStudentId] = useState<string | null>(null);

  // Load student ID from localStorage and then load classes
  useEffect(() => {
    const userData = localStorage.getItem('user');
    console.log('Raw localStorage data:', userData);
    if (userData) {
      const parsedData = JSON.parse(userData);
      console.log('Parsed localStorage data:', parsedData);
      if (parsedData.userType === 'student' && parsedData.userId) {
        console.log('Setting studentId to:', parsedData.userId);
        setStudentId(parsedData.userId);
      } else {
        console.log('User is not a student or userId missing');
      }
    } else {
      console.log('No user data found in localStorage');
    }
  }, []);

  // Load classes when studentId is available
  useEffect(() => {
    console.log('studentId:', studentId);
    if (studentId) {
      loadClasses();
    }
  }, [studentId]);

  const loadClasses = async () => {
    if (!studentId) return;
    
    try {
      setIsLoading(true);
      setError(null);
      console.log('Loading classes for studentId:', studentId);
      const response = await studentApi.getClasses(studentId);
      if (response.success) {
        setClasses(response.classes);
      }
    } catch (error) {
      console.error('Error loading classes:', error);
      setError('Failed to load classes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinClass = async () => {
    if (!studentId) {
      setError('Student ID not found. Please log in again.');
      return;
    }
    
    try {
      setError(null);
      const response = await studentApi.joinClass(joinCode, studentId);
      if (response.success) {
        setJoinCode('');
        // Reload classes to show the new one
        await loadClasses();
      }
    } catch (error: any) {
      console.error('Error joining class:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Failed to join class');
      }
    }
  };

  const handleUpdatePreferences = async () => {
    if (!studentId) return;
    
    try {
      await studentApi.updatePreferences(studentId, interests, learningStyle);
      console.log('Preferences updated successfully');
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  const handleSendMessage = () => {
    if (chatMessage.trim() && selectedClass) {
      const newMessage: Message = {
        id: Date.now().toString(),
        text: chatMessage,
        sender: 'user',
        timestamp: new Date(),
        classId: selectedClass
      };
      
      setMessages([...messages, newMessage]);
      setChatMessage('');
      
      // Simulate assistant response after a short delay
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: `I understand you're asking about "${chatMessage}". Let me help you with that in ${classes.find(c => c.id === selectedClass)?.name}.`,
          sender: 'assistant',
          timestamp: new Date(),
          classId: selectedClass
        };
        setMessages(prev => [...prev, assistantMessage]);
      }, 1000);
    }
  };

  const handleSelectClass = (classId: string) => {
    setSelectedClass(classId);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const getMessagesForClass = (classId: string) => {
    return messages.filter(msg => msg.classId === classId);
  };

  return (
    <div className={styles.container}>
      <main className={styles.main}>
        <div className={styles.layout}>
          <StudentSidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            classes={classes}
            selectedClass={selectedClass}
            onSelectClass={handleSelectClass}
            joinCode={joinCode}
            setJoinCode={setJoinCode}
            onJoinClass={handleJoinClass}
            interests={interests}
            setInterests={setInterests}
            learningStyle={learningStyle}
            setLearningStyle={setLearningStyle}
            onUpdatePreferences={handleUpdatePreferences}
            sidebarCollapsed={sidebarCollapsed}
            onToggleSidebar={toggleSidebar}
            isLoading={isLoading}
            error={error}
          />

          <StudentChat
            selectedClass={selectedClass}
            classes={classes}
            messages={messages}
            chatMessage={chatMessage}
            setChatMessage={setChatMessage}
            onSendMessage={handleSendMessage}
            getMessagesForClass={getMessagesForClass}
          />
        </div>
      </main>
    </div>
  );
}
