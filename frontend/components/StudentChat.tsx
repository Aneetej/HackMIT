'use client';

import { useEffect, useRef } from 'react';
import styles from './StudentChat.module.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  classId: string;
}

interface Class {
  id: string;
  name: string;
}

interface StudentChatProps {
  selectedClass: string | null;
  classes: Class[];
  messages: Message[];
  chatMessage: string;
  setChatMessage: (message: string) => void;
  onSendMessage: () => void;
  getMessagesForClass: (classId: string) => Message[];
}

export default function StudentChat({
  selectedClass,
  classes,
  messages,
  chatMessage,
  setChatMessage,
  onSendMessage,
  getMessagesForClass
}: StudentChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  return (
    <div className={styles.rightContent}>
      <div className={styles.chatContainer}>
        <div className={styles.chatArea}>
          <div className={styles.chatHeader}>
            {selectedClass ? (
              <h2 className={styles.chatTitle}>
                Chat - {classes.find(c => c.id === selectedClass)?.name}
              </h2>
            ) : (
              <h2 className={styles.chatTitle}>Select a class to start chatting</h2>
            )}
          </div>
          <div className={styles.chatMessages}>
            {selectedClass ? (
              <>
                <div className={styles.welcomeMessage}>
                  Welcome to {classes.find(c => c.id === selectedClass)?.name}! Ask any questions about your coursework.
                </div>
                {getMessagesForClass(selectedClass).map((message) => (
                  <div 
                    key={message.id} 
                    className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.assistantMessage}`}
                  >
                    <div className={styles.messageContent}>
                      {message.text}
                    </div>
                    <div className={styles.messageTime}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className={styles.noClassMessage}>
                Please select a class from the sidebar to begin chatting.
              </div>
            )}
          </div>
          <div className={styles.chatInput}>
            <input
              type="text"
              className={styles.messageInput}
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder={selectedClass ? "Type your message..." : "Select a class first"}
              disabled={!selectedClass}
            />
            <button 
              className={styles.sendButton}
              onClick={onSendMessage}
              disabled={!selectedClass}
            >
              ↑
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
