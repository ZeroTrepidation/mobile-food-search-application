import { Checkbox } from 'primereact/checkbox';

export type PermitStatus = 'APPROVED' | 'REQUESTED' | 'SUSPEND' | 'EXPIRED' | string;

interface StatusCheckboxesProps {
  value: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
  default?: string;
}

const ALL_STATUSES: PermitStatus[] = ['APPROVED', 'REQUESTED', 'SUSPEND', 'EXPIRED'];

export default function StatusCheckboxes({ value, onChange, disabled }: StatusCheckboxesProps) {
  const toggle = (status: string, checked: boolean) => {
    if (status === 'APPROVED') return; // lock APPROVED
    if (checked) {
      if (!value.includes(status)) onChange([...value, status]);
    } else {
      onChange(value.filter((s) => s !== status));
    }
  };

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
      {ALL_STATUSES.map((s) => (
        <div key={s} className="p-field-checkbox" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Checkbox
            inputId={`status-${s}`}
            value={s}
            onChange={(e) => toggle(s, e.checked as boolean)}
            checked={s === 'APPROVED' ? true : value.includes(s)}
            disabled={disabled || s === 'APPROVED'}
          />
          <label htmlFor={`status-${s}`}>{s}</label>
        </div>
      ))}
    </div>
  );
}
