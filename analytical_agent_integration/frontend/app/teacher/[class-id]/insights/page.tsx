'use client';

import { useState, useEffect, use } from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { teacherApi, MessageInsightsData, InsightData } from '../../../../lib/teacher/apis';
import CommonStruggle from '../../../../components/CommonStruggle';
import styles from './page.module.css';

export default function InsightsPage({ params }: { params: Promise<{ 'class-id': string }> }) {
  const resolvedParams = use(params);
  const classId = resolvedParams['class-id'];
  
  const [messageInsights, setMessageInsights] = useState<MessageInsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [frequentStruggles] = useState('Students frequently struggle with algebra equations, word problems, and fractions. These areas require additional attention and support.');
  const [insightCards, setInsightCards] = useState<InsightData[]>([]);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [editingCard, setEditingCard] = useState<string | null>(null);
  const [editingValues, setEditingValues] = useState<{title: string, description: string}>({title: '', description: ''});
  const [newInsight, setNewInsight] = useState({ title: '', description: '' });
  const [showNewInsightForm, setShowNewInsightForm] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setInsightsLoading(true);
        
        // Fetch message insights and custom insights in parallel
        const [messageResponse, insightsResponse] = await Promise.all([
          teacherApi.getMessageInsights(classId),
          teacherApi.getInsights(classId)
        ]);
        
        if (messageResponse.success) {
          setMessageInsights(messageResponse.data);
        } else {
          setError('Failed to load message insights');
        }
        
        if (insightsResponse.success) {
          setInsightCards(insightsResponse.insights);
        } else {
          setError('Failed to load insights');
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
        setInsightsLoading(false);
      }
    };

    fetchData();
  }, [classId]);

  const handleCreateInsight = async () => {
    if (newInsight.title.trim() && newInsight.description.trim()) {
      try {
        const response = await teacherApi.createInsight(classId, {
          title: newInsight.title,
          description: newInsight.description
        });
        
        if (response.success) {
          setInsightCards(prev => [response.insight, ...prev]);
          setNewInsight({ title: '', description: '' });
          setShowNewInsightForm(false);
        }
      } catch (error) {
        console.error('Error creating insight:', error);
        setError('Failed to create insight');
      }
    }
  };

  const handleCancelInsight = () => {
    setNewInsight({ title: '', description: '' });
    setShowNewInsightForm(false);
  };

  const handleDeleteCard = async (cardId: string) => {
    try {
      const response = await teacherApi.deleteInsight(cardId);
      
      if (response.success) {
        setInsightCards(prev => prev.filter(card => card.id !== cardId));
      }
    } catch (error) {
      console.error('Error deleting insight:', error);
      setError('Failed to delete insight');
    }
  };

  const handleEditCard = (cardId: string) => {
    const card = insightCards.find(c => c.id === cardId);
    if (card) {
      setEditingValues({title: card.title, description: card.description});
      setEditingCard(cardId);
    }
  };

  const handleSaveEdit = async (cardId: string) => {
    try {
      const response = await teacherApi.updateInsight(cardId, {
        title: editingValues.title,
        description: editingValues.description
      });
      
      if (response.success) {
        setInsightCards(prev => prev.map(card => 
          card.id === cardId ? response.insight : card
        ));
        setEditingCard(null);
        setEditingValues({title: '', description: ''});
      }
    } catch (error) {
      console.error('Error updating insight:', error);
      setError('Failed to update insight');
    }
  };

  const handleCancelEdit = () => {
    setEditingCard(null);
    setEditingValues({title: '', description: ''});
  };

  // Generate chart data from message insights
  const generateChartData = () => {
    if (!messageInsights || messageInsights.studentBreakdown.length === 0) {
      return [
        { day: 'Mon', usage: 0 },
        { day: 'Tue', usage: 0 },
        { day: 'Wed', usage: 0 },
        { day: 'Thu', usage: 0 },
        { day: 'Fri', usage: 0 },
        { day: 'Sat', usage: 0 },
        { day: 'Sun', usage: 0 },
      ];
    }

    // For now, distribute the average across days (in a real app, you'd have daily data)
    const avgMessages = messageInsights.averageMessagesPerStudent;
    return [
      { day: 'Mon', usage: Math.round(avgMessages * 0.8) },
      { day: 'Tue', usage: Math.round(avgMessages * 1.2) },
      { day: 'Wed', usage: Math.round(avgMessages * 0.9) },
      { day: 'Thu', usage: Math.round(avgMessages * 1.4) },
      { day: 'Fri', usage: Math.round(avgMessages * 1.1) },
      { day: 'Sat', usage: Math.round(avgMessages * 0.5) },
      { day: 'Sun', usage: Math.round(avgMessages * 0.7) },
    ];
  };

  return (
    <div className={styles.insightsContainer}>
      <div className={styles.topSection}>
        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>Average usage by day</h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={generateChartData()}>
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
                  formatter={(value) => [`${value} messages`, 'Messages']}
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

        <CommonStruggle 
          struggles={frequentStruggles}
          title="Frequent areas of struggle"
          editable={false}
        />
      </div>

      <div className={styles.customInsightsSection}>
        <h2 className={styles.sectionTitle}>Custom insight areas</h2>
        <div className={styles.insightCardsContainer}>
          {insightsLoading ? (
            <div className={styles.loadingMessage}>Loading insights...</div>
          ) : (
            <div className={styles.insightCards}>
              {insightCards.map((card) => (
              <div key={card.id} className={styles.insightCard}>
                <div className={styles.cardHeader}>
                  {editingCard === card.id ? (
                    <input
                      type="text"
                      value={editingValues.title}
                      onChange={(e) => setEditingValues(prev => ({ ...prev, title: e.target.value }))}
                      className={styles.editInput}
                    />
                  ) : (
                    <h3 className={styles.cardTitle}>{card.title}</h3>
                  )}
                  <div className={styles.cardActions}>
                    {editingCard === card.id ? (
                      <>
                        <button 
                          className={styles.actionButton}
                          onClick={() => handleSaveEdit(card.id)}
                          title="Save changes"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="20,6 9,17 4,12"/>
                          </svg>
                        </button>
                        <button 
                          className={styles.actionButton}
                          onClick={handleCancelEdit}
                          title="Cancel editing"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                          </svg>
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          className={styles.actionButton}
                          onClick={() => handleEditCard(card.id)}
                          title="Edit insight"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                        <button 
                          className={styles.actionButton}
                          onClick={() => handleDeleteCard(card.id)}
                          title="Delete insight"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="3,6 5,6 21,6"/>
                            <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
                            <line x1="10" y1="11" x2="10" y2="17"/>
                            <line x1="14" y1="11" x2="14" y2="17"/>
                          </svg>
                        </button>
                      </>
                    )}
                  </div>
                </div>
                <div className={styles.cardBody}>
                  <div className={styles.cardDescription}>
                    {editingCard === card.id ? (
                      <textarea
                        value={editingValues.description}
                        onChange={(e) => setEditingValues(prev => ({ ...prev, description: e.target.value }))}
                        className={styles.editTextarea}
                      />
                    ) : (
                      card.description
                    )}
                  </div>
                  <div className={styles.cardOutput}>
                    <span className={styles.outputLabel}>Output:</span>
                    <div className={styles.outputValue}>Loading analytics...</div>
                  </div>
                </div>
              </div>
            ))}
            {showNewInsightForm ? (
              <div className={styles.newInsightForm}>
                <input
                  type="text"
                  placeholder="Insight Title"
                  value={newInsight.title}
                  onChange={(e) => setNewInsight(prev => ({ ...prev, title: e.target.value }))}
                  className={styles.insightInput}
                />
                <textarea
                  placeholder="Insight Description"
                  value={newInsight.description}
                  onChange={(e) => setNewInsight(prev => ({ ...prev, description: e.target.value }))}
                  className={styles.insightTextarea}
                />
                <div className={styles.formButtons}>
                  <button className={styles.createButton} onClick={handleCreateInsight}>
                    Create
                  </button>
                  <button className={styles.cancelButton} onClick={handleCancelInsight}>
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button className={styles.addButton} onClick={() => setShowNewInsightForm(true)}>
                +
              </button>
            )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
