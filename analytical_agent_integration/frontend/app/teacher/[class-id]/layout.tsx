'use client';

import { use } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import styles from './layout.module.css';

export default function ClassLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ 'class-id': string }>;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const resolvedParams = use(params);
  const classId = resolvedParams['class-id'];

  const handleBack = () => {
    router.push('/teacher');
  };

  const getActiveTab = () => {
    if (pathname.includes('/students')) return 'Students';
    if (pathname.includes('/insights')) return 'Insights';
    return 'Setup';
  };

  const handleTabClick = (tab: string) => {
    switch (tab) {
      case 'Setup':
        router.push(`/teacher/${classId}`);
        break;
      case 'Students':
        router.push(`/teacher/${classId}/students`);
        break;
      case 'Insights':
        router.push(`/teacher/${classId}/insights`);
        break;
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-8)' }}>
            <button className={styles.backButton} onClick={handleBack}>
              <svg className={styles.backIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            
            <nav className={styles.navigation}>
              {['Setup', 'Students', 'Insights'].map((tab) => (
                <button
                  key={tab}
                  className={`${styles.navTab} ${getActiveTab() === tab ? styles.navTabActive : ''}`}
                  onClick={() => handleTabClick(tab)}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
          
          <div className={styles.classCode}>
            Class code: {classId}
          </div>
        </div>
      </header>

      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
