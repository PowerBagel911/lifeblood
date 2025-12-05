import { ResponseMode } from '../types';

interface ModeSelectProps {
  mode: ResponseMode;
  onChange: (mode: ResponseMode) => void;
  disabled?: boolean;
}

const ModeSelect = ({ mode, onChange, disabled = false }: ModeSelectProps) => {
  const modes: { value: ResponseMode; label: string; description: string }[] = [
    {
      value: 'general',
      label: 'General',
      description: 'Concise, professional answers'
    },
    {
      value: 'checklist',
      label: 'Checklist',
      description: 'Step-by-step format'
    },
    {
      value: 'plain_english',
      label: 'Plain English',
      description: 'Simplified explanations'
    }
  ];

  return (
    <div className="flex flex-col space-y-2">
      <label className="text-sm font-medium text-gray-700">
        Response Mode
      </label>
      <select
        value={mode}
        onChange={(e) => onChange(e.target.value as ResponseMode)}
        disabled={disabled}
        className="px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm 
                   bg-white focus:outline-none focus:ring-2 focus:ring-blood-red-500 
                   focus:border-blood-red-500 disabled:bg-gray-50 disabled:text-gray-500"
      >
        {modes.map((modeOption) => (
          <option key={modeOption.value} value={modeOption.value}>
            {modeOption.label} - {modeOption.description}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModeSelect;
