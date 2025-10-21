import { Checkbox } from 'primereact/checkbox';

export type PermitStatus = 'APPROVED' | 'REQUESTED' | 'SUSPEND' | 'EXPIRED' | string;

interface StatusCheckboxesProps {
  value: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
}

const ALL_STATUSES: PermitStatus[] = ['APPROVED', 'REQUESTED', 'SUSPEND', 'EXPIRED'];

export default function StatusCheckboxes({ value, onChange, disabled }: StatusCheckboxesProps) {
  const toggle = (status: string, checked: boolean) => {
    if (checked) {
      // single-select: selecting one status unselects the others
      onChange([status]);
    } else {
      // unchecking clears selection
      onChange([]);
    }
  };

  const formatLabel = (str: string) => str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
      {ALL_STATUSES.map((s) => (
        <div key={s} className="p-field-checkbox" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Checkbox
            inputId={`status-${s}`}
            value={s}
            onChange={(e) => toggle(s, e.checked as boolean)}
            checked={value.includes(s)}
            disabled={disabled}
          />
          <label htmlFor={`status-${s}`}>{formatLabel(s)}</label>
        </div>
      ))}
    </div>
  );
}
