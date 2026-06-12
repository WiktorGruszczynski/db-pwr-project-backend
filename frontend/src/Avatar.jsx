export default function Avatar({ name, size = 36 }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: size,
        height: size,
        borderRadius: '50%',
        background: 'var(--primary-soft)',
        color: 'var(--primary-hover)',
        fontWeight: 700,
        fontSize: size * 0.42,
        textTransform: 'uppercase',
        flexShrink: 0,
      }}
    >
      {(name || '?').charAt(0)}
    </span>
  );
}
