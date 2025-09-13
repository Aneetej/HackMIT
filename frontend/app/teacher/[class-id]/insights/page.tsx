'use client';

import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import styles from './page.module.css';

const usageData = [
  { day: 'Mon', usage: 65 },
  { day: 'Tue', usage: 45 },
  { day: 'Wed', usage: 55 },
  { day: 'Thu', usage: 80 },
  { day: 'Fri', usage: 70 },
  { day: 'Sat', usage: 35 },
  { day: 'Sun', usage: 60 },
];

interface InsightCard {
  id: string;
  title: string;
  content: string;
  description: string;
}

export default function InsightsPage() {
  const [frequentStruggles] = useState(['Algebra equations', 'Word problems', 'Fractions']);
  const [insightCards, setInsightCards] = useState<InsightCard[]>([
    { id: '1', title: 'Reading Comprehension', content: 'Students struggle with complex passages', description: 'Analysis of reading performance' },
    { id: '2', title: 'Math Problem Solving', content: 'Multi-step problems cause difficulty', description: 'Problem-solving patterns' },
    { id: '3', title: 'Time Management', content: 'Students rush through assignments', description: 'Completion time analysis' },
    { id: '4', title: 'Concept Application', content: 'Theory to practice gap identified', description: 'Application skill assessment' },
  ]);

  const handleAddCard = () => {
    const newCard: InsightCard = {
      id: Date.now().toString(),
      title: 'New Insight',
      content: 'Add your insight content here',
      description: 'Add description'
    };
    setInsightCards(prev => [...prev, newCard]);
  };

  return (
    <div className={styles.insightsContainer}>
      <div className={styles.topSection}>
        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>Average usage by day</h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={usageData}>
                <XAxis 
                  dataKey="day" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  width={30}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: 'var(--radius)',
                    color: 'hsl(var(--foreground))',
                    fontSize: '12px'
                  }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                  formatter={(value) => [`${value} minutes`, 'Usage']}
                  labelFormatter={(label) => `${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={styles.strugglesSection}>
          <h2 className={styles.sectionTitle}>Frequent areas of struggle</h2>
          <div className={styles.strugglesInputs}>
            {frequentStruggles.map((struggle, index) => (
              <input
                key={index}
                type="text"
                className={styles.struggleInput}
                value={struggle}
                readOnly
              />
            ))}
          </div>
        </div>
      </div>

      <div className={styles.customInsightsSection}>
        <h2 className={styles.sectionTitle}>Custom insight areas</h2>
        <div className={styles.insightCardsContainer}>
          <div className={styles.insightCards}>
            {insightCards.map((card) => (
              <div key={card.id} className={styles.insightCard}>
                <h3 className={styles.cardTitle}>{card.title}</h3>
                <p className={styles.cardContent}>{card.content}</p>
                <p className={styles.cardDescription}>{card.description}</p>
              </div>
            ))}
          </div>
          <button className={styles.addButton} onClick={handleAddCard}>
            +
          </button>
        </div>
      </div>
    </div>
  );
}
