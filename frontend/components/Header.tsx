'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import styles from './Header.module.css';

interface UserData {
  userType: 'student' | 'teacher';
  userId: string;
  name?: string;
  email?: string;
}

export default function Header() {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Get user data from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUserData(parsedUser);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  const handleSignOut = () => {
    localStorage.removeItem('user');
    setUserData(null);
    router.push('/');
  };

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <div className={styles.logoPlaceholder}>
            Lumos
          </div>
        </Link>

        <div className={styles.profileSection}>
          <div className={styles.profileContainer}>
            <button
              className={styles.profileButton}
              onClick={() => setShowProfileMenu(!showProfileMenu)}
            >
              <div className={styles.profileIcon}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </button>

            {showProfileMenu && (
              <div className={styles.profileMenu}>
                {userData ? (
                  <button
                    className={styles.menuButton}
                    onClick={handleSignOut}
                  >
                    Sign Out
                  </button>
                ) : (
                  <button
                    className={styles.menuButton}
                    onClick={() => {
                      router.push('/');
                      setShowProfileMenu(false);
                    }}
                  >
                    Sign In
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
