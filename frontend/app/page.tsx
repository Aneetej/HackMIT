'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '../lib/auth/apis';
import styles from './page.module.css';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'student' | 'teacher'>('student');
  const [isSignUp, setIsSignUp] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData(e.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const name = formData.get('name') as string;
    const grade = formData.get('grade') as string;
    const subject = formData.get('subject') as string;

    try {
      if (isSignUp) {
        // Registration flow
        if (activeTab === 'student') {
          const response = await authApi.registerStudent({
            email,
            name,
            grade,
            subject_focus: 'general_math',
            learning_style: 'mixed'
          });
          
          // Store user data in unified format
          localStorage.setItem('user', JSON.stringify({
            userType: 'student',
            userId: response.studentId
          }));
          router.push('/student');
        } else {
          const response = await authApi.registerTeacher({
            email,
            name,
            subject
          });
          if (response.success) {
            setError('');
            setIsLoading(false);
            
            // Store user data in unified format
            localStorage.setItem('user', JSON.stringify({
              userType: 'teacher',
              userId: response.teacherId
            }));
            router.push('/teacher');
          }
        }
      } else {
        // Sign in flow - check if user exists
        if (activeTab === 'student') {
          const response = await authApi.signInStudent({ email });
          
          // Store user data in unified format
          localStorage.setItem('user', JSON.stringify({
            userType: 'student',
            userId: response.studentId
          }));
          router.push('/student');
        } else {
          const response = await authApi.signInTeacher({ email });
          
          // Store user data in unified format
          localStorage.setItem('user', JSON.stringify({
            userType: 'teacher',
            userId: response.teacherId
          }));
          router.push('/teacher');
        }
      }
    } catch (error: any) {
      console.error('Authentication error:', error);
      if (error.response?.status === 409) {
        setError('An account with this email already exists. Please sign in instead.');
        setIsSignUp(false);
      } else if (error.response?.status === 404) {
        setError('No account found with this email address. Please sign up first.');
        setIsSignUp(true);
      } else {
        setError(isSignUp ? 'Registration failed. Please try again.' : 'Sign in failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.title}>MathEngageAI</h1>
          <p className={styles.subtitle}>
            Personalized AI tutoring that adapts to your learning style
          </p>
        </div>

        <div className={styles.authContainer}>
          <div className={styles.tabContainer}>
            <button
              className={`${styles.tab} ${activeTab === 'student' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('student')}
            >
              Student
            </button>
            <button
              className={`${styles.tab} ${activeTab === 'teacher' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('teacher')}
            >
              Teacher
            </button>
          </div>

          <div className={styles.formContainer}>
            <form onSubmit={handleSubmit} className={styles.form}>
              <h2 className={styles.formTitle}>
                {isSignUp ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className={styles.formSubtitle}>
                {isSignUp 
                  ? `Join as a ${activeTab} and start your learning journey`
                  : `Sign in to your ${activeTab} account`
                }
              </p>

              {error && (
                <div className={styles.errorMessage}>
                  {error}
                </div>
              )}

              <div className={styles.inputGroup}>
                <label htmlFor="email" className={styles.label}>
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className={styles.input}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="password" className={styles.label}>
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  className={styles.input}
                  placeholder="Enter your password"
                  required
                />
              </div>

              {isSignUp && (
                <>
                  <div className={styles.inputGroup}>
                    <label htmlFor="confirmPassword" className={styles.label}>
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      id="confirmPassword"
                      name="confirmPassword"
                      className={styles.input}
                      placeholder="Confirm your password"
                      required
                    />
                  </div>

                  <div className={styles.inputGroup}>
                    <label htmlFor="name" className={styles.label}>
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      className={styles.input}
                      placeholder="Enter your full name"
                      required
                    />
                  </div>

                  {activeTab === 'student' && (
                    <div className={styles.inputGroup}>
                      <label htmlFor="grade" className={styles.label}>
                        Grade Level
                      </label>
                      <select id="grade" name="grade" className={styles.input} required>
                        <option value="">Select your grade</option>
                        <option value="6">6th Grade</option>
                        <option value="7">7th Grade</option>
                        <option value="8">8th Grade</option>
                        <option value="9">9th Grade</option>
                        <option value="10">10th Grade</option>
                        <option value="11">11th Grade</option>
                        <option value="12">12th Grade</option>
                      </select>
                    </div>
                  )}

                  {activeTab === 'teacher' && (
                    <div className={styles.inputGroup}>
                      <label htmlFor="subject" className={styles.label}>
                        Subject Area
                      </label>
                      <input
                        type="text"
                        id="subject"
                        name="subject"
                        className={styles.input}
                        placeholder="e.g., Algebra, Geometry, Calculus"
                        required
                      />
                    </div>
                  )}
                </>
              )}

              <button 
                type="submit" 
                className={styles.submitButton}
                disabled={isLoading}
              >
                {isLoading ? 'Loading...' : (isSignUp ? 'Create Account' : 'Sign In')}
              </button>

              <div className={styles.authToggle}>
                <span className={styles.authToggleText}>
                  {isSignUp ? 'Already have an account?' : "Don't have an account?"}
                </span>
                <button
                  type="button"
                  className={styles.authToggleButton}
                  onClick={() => setIsSignUp(!isSignUp)}
                >
                  {isSignUp ? 'Sign In' : 'Sign Up'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
