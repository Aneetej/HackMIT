import styles from './CommonStruggle.module.css'

interface CommonStruggleProps {
    struggles: string;
    title?: string;
    editable?: boolean;
    onStruggleChange?: (value: string) => void;
}

export default function CommonStruggle({ 
    struggles, 
    title = "Common Struggle", 
    editable = false,
    onStruggleChange 
}: CommonStruggleProps) {
    return (
        <div className={styles.card}>
            <h3 className={styles.cardTitle}>{title}</h3>
            <div className={styles.strugglesContainer}>
                {struggles}
            </div>
        </div>
    )
}