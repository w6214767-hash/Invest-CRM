export default function ScoreBadge({ score }) {
  const value = Number(score || 0)
  const tone = value >= 70 ? 'good' : value >= 45 ? 'medium' : 'low'
  return <span className={`score-badge ${tone}`}>{value.toFixed(0)}</span>
}
