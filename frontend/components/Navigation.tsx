'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Navigation.module.css';

interface NavigationProps {
  userRole: 'teacher' | 'student';
  userName: string;
  userAvatar?: string;
}

export default function Navigation({ userRole, userName, userAvatar }: NavigationProps) {
  const pathname = usePathname();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const navigationItems = [
    { href: `/${userRole}`, label: 'Classes'},

  ];

  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        {/* Logo and Brand */}
        <div className={styles.brand}>
          <div className={styles.logo}>EduHub</div>
          <div className={styles.navItems}>
            {navigationItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${
                  pathname === item.href ? styles.navItemActive : ''
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>

        {/* User Profile */}
        <div className={styles.profile}>
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className={styles.profileButton}
          >
            <div className={styles.avatar}>
              {userAvatar ? (
                <img src={userAvatar} alt={userName} className={styles.avatarImage} />
              ) : (
                userName.charAt(0).toUpperCase()
              )}
            </div>
            <div className={styles.userInfo}>
              <div className={styles.userName}>{userName}</div>
              <div className={styles.userRole}>{userRole}</div>
            </div>
            <svg className={styles.chevron} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Profile Dropdown */}
          {isProfileOpen && (
            <div className={styles.dropdown}>
              <Link href="/profile" className={styles.dropdownItem}>
                Profile Settings
              </Link>
              <Link href="/preferences" className={styles.dropdownItem}>
                Preferences
              </Link>
              <hr className={styles.dropdownSeparator} />
              <button className={styles.dropdownItem}>
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className={styles.mobileNav}>
        <div className={styles.mobileNavItems}>
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.mobileNavItem} ${
                pathname === item.href ? styles.mobileNavItemActive : ''
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
