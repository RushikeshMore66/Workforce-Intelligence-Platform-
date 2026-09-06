import { ProfileCard } from '@/components/settings/ProfileCard';

export const metadata = { title: 'Settings' };

type Field = {
  label: string;
  value: string;
  type: string;
  readonly?: boolean;
  on?: boolean;
};

type Section = {
  title: string;
  fields: Field[];
};

const SECTIONS: Section[] = [
  {
    title: 'Account',
    fields: [
      { label: 'Full Name', value: 'Rajesh Mehta', type: 'text' },
      { label: 'Email Address', value: 'rajesh.mehta@apexsoftware.in', type: 'email' },
      { label: 'Company', value: 'Apex Software Solutions', type: 'text' },
      { label: 'Role', value: 'Owner', type: 'text', readonly: true },
    ],
  },
  {
    title: 'Notifications',
    fields: [
      { label: 'Blocker alerts', value: 'Enabled', type: 'toggle', on: true },
      { label: 'Deadline reminders', value: 'Enabled', type: 'toggle', on: true },
      { label: 'Project updates', value: 'Enabled', type: 'toggle', on: true },
      { label: 'Weekly digest email', value: 'Disabled', type: 'toggle', on: false },
    ],
  },
  {
    title: 'Display',
    fields: [
      { label: 'Date format', value: 'DD MMM YYYY', type: 'text', readonly: true },
      { label: 'Time zone', value: 'Asia/Kolkata (IST, UTC+5:30)', type: 'text', readonly: true },
      { label: 'Currency', value: 'INR (₹)', type: 'text', readonly: true },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="max-w-[700px] mx-auto space-y-6">
      <div>
        <h1 className="wi-page-title">Settings</h1>
        <p className="text-sm text-[#667085] mt-0.5">Manage your account preferences and application settings.</p>
      </div>

      <div className="bg-[#FFFAEB] border border-[#FEDF89] rounded-xl px-5 py-3.5 text-sm text-[#B54708]">
        <strong>Demo mode:</strong> Settings changes are not persisted. This page demonstrates the intended settings UI layout.
      </div>

      {/* Profile Card */}
      <ProfileCard />

      {/* Settings sections */}
      {SECTIONS.map(section => (
        <div key={section.title} className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">{section.title}</h2>
          </div>
          <div className="divide-y divide-[#F3F4F6]">
            {section.fields.map(field => (
              <div key={field.label} className="flex items-center justify-between px-5 py-4">
                <div>
                  <div className="text-sm font-medium text-[#172033]">{field.label}</div>
                </div>
                <div className="flex items-center gap-2">
                  {field.type === 'toggle' ? (
                    <div className={`relative inline-flex w-9 h-5 rounded-full transition-colors ${field.on ? 'bg-[#263B80]' : 'bg-[#D1D5DB]'}`}>
                      <span className={`inline-block w-4 h-4 rounded-full bg-white shadow transition-transform mt-0.5 ${field.on ? 'translate-x-4' : 'translate-x-0.5'}`} />
                    </div>
                  ) : (
                    <span className={`text-sm ${field.readonly ? 'text-[#9CA3AF]' : 'text-[#172033]'}`}>{field.value}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-[#172033] mb-3">Danger Zone</h2>
        <div className="border border-[#FECDCA] rounded-lg p-4 bg-[#FEF3F2]">
          <p className="text-sm text-[#B42318]">Account deletion and data export options will be available when the backend is connected.</p>
        </div>
      </div>
    </div>
  );
}
