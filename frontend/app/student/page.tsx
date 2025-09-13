'use client';

import { useState } from 'react';
import Navigation from '../../components/Navigation';
import StudentSidebar from '../../components/StudentSidebar';
import StudentChat from '../../components/StudentChat';
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
  const [classes] = useState([
    { id: '1', name: 'Mathematics 101' },
    { id: '2', name: 'Physics Fundamentals' },
    { id: '3', name: 'Chemistry Lab' },
  ]);

  const handleJoinClass = () => {
    if (joinCode.trim()) {
      console.log('Joining class with code:', joinCode);
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
      setMessages(prev => [...prev, newMessage]);
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
      <Navigation 
        userRole="student" 
        userName="John Smith" 
      />
      
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
            sidebarCollapsed={sidebarCollapsed}
            onToggleSidebar={toggleSidebar}
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
