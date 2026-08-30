import { Supervisor, Team, TeamLeader, Worker } from '@/types';

// ============================================================
// SUPERVISORS
// ============================================================
export const SUPERVISORS: Supervisor[] = [
  {
    id: 'sup-1',
    userId: 'user-sup-1',
    name: 'Amit Sharma',
    email: 'amit.sharma@apexsoftware.in',
    avatarInitials: 'AS',
    projectIds: ['proj-1', 'proj-4', 'proj-9'],
    teamIds: ['team-1', 'team-4'],
  },
  {
    id: 'sup-2',
    userId: 'user-sup-2',
    name: 'Priya Deshmukh',
    email: 'priya.deshmukh@apexsoftware.in',
    avatarInitials: 'PD',
    projectIds: ['proj-2', 'proj-7'],
    teamIds: ['team-2', 'team-5'],
  },
  {
    id: 'sup-3',
    userId: 'user-sup-3',
    name: 'Rahul Mehta',
    email: 'rahul.mehta@apexsoftware.in',
    avatarInitials: 'RM',
    projectIds: ['proj-3', 'proj-10'],
    teamIds: ['team-3'],
  },
  {
    id: 'sup-4',
    userId: 'user-sup-4',
    name: 'Neha Kulkarni',
    email: 'neha.kulkarni@apexsoftware.in',
    avatarInitials: 'NK',
    projectIds: ['proj-5', 'proj-8', 'proj-11'],
    teamIds: ['team-4', 'team-6'],
  },
  {
    id: 'sup-5',
    userId: 'user-sup-5',
    name: 'Vikram Patil',
    email: 'vikram.patil@apexsoftware.in',
    avatarInitials: 'VP',
    projectIds: ['proj-6', 'proj-12'],
    teamIds: ['team-5', 'team-6'],
  },
];

// ============================================================
// TEAM LEADERS
// ============================================================
export const TEAM_LEADERS: TeamLeader[] = [
  { id: 'tl-1', userId: 'user-tl-1', name: 'Kiran Joshi', email: 'kiran.joshi@apexsoftware.in', avatarInitials: 'KJ', teamId: 'team-1' },
  { id: 'tl-2', userId: 'user-tl-2', name: 'Sneha Patil', email: 'sneha.patil@apexsoftware.in', avatarInitials: 'SP', teamId: 'team-2' },
  { id: 'tl-3', userId: 'user-tl-3', name: 'Arjun Nair', email: 'arjun.nair@apexsoftware.in', avatarInitials: 'AN', teamId: 'team-3' },
  { id: 'tl-4', userId: 'user-tl-4', name: 'Divya Rao', email: 'divya.rao@apexsoftware.in', avatarInitials: 'DR', teamId: 'team-4' },
  { id: 'tl-5', userId: 'user-tl-5', name: 'Suresh Iyer', email: 'suresh.iyer@apexsoftware.in', avatarInitials: 'SI', teamId: 'team-5' },
  { id: 'tl-6', userId: 'user-tl-6', name: 'Pooja Bhat', email: 'pooja.bhat@apexsoftware.in', avatarInitials: 'PB', teamId: 'team-6' },
];

// ============================================================
// TEAMS
// ============================================================
export const TEAMS: Team[] = [
  { id: 'team-1', name: 'Backend Engineering', supervisorId: 'sup-1', teamLeaderId: 'tl-1', memberCount: 18, projectIds: ['proj-1', 'proj-4'] },
  { id: 'team-2', name: 'Frontend Engineering', supervisorId: 'sup-2', teamLeaderId: 'tl-2', memberCount: 15, projectIds: ['proj-2', 'proj-7'] },
  { id: 'team-3', name: 'QA & Testing', supervisorId: 'sup-3', teamLeaderId: 'tl-3', memberCount: 12, projectIds: ['proj-3', 'proj-10'] },
  { id: 'team-4', name: 'UI/UX Design', supervisorId: 'sup-4', teamLeaderId: 'tl-4', memberCount: 8, projectIds: ['proj-5', 'proj-8'] },
  { id: 'team-5', name: 'DevOps & Infrastructure', supervisorId: 'sup-5', teamLeaderId: 'tl-5', memberCount: 7, projectIds: ['proj-6', 'proj-12'] },
  { id: 'team-6', name: 'Product & Integration', supervisorId: 'sup-4', teamLeaderId: 'tl-6', memberCount: 10, projectIds: ['proj-11'] },
];

// ============================================================
// WORKERS (70 total)
// ============================================================
const makeWorker = (
  id: string,
  name: string,
  roleTitle: string,
  teamId: string,
  teamLeaderId: string,
  supervisorId: string,
  activeProjectId: string | null,
  completed: number,
  inProgress: number,
  pending: number,
  blocked: number,
  status: Worker['status'] = 'ACTIVE',
): Worker => ({
  id,
  name,
  email: `${name.toLowerCase().replace(' ', '.')}@apexsoftware.in`,
  role: roleTitle,
  teamId,
  teamLeaderId,
  supervisorId,
  avatarInitials: name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase(),
  status,
  activeProjectId,
  completedTaskCount: completed,
  inProgressTaskCount: inProgress,
  pendingTaskCount: pending,
  blockedTaskCount: blocked,
});

export const WORKERS: Worker[] = [
  // Backend Engineering (team-1, sup-1, tl-1) — 18 members
  makeWorker('w-1',  'Rohan Verma',       'Senior Backend Developer',  'team-1', 'tl-1', 'sup-1', 'proj-1', 24, 3, 2, 0),
  makeWorker('w-2',  'Sunil Gupta',       'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-1', 18, 2, 4, 1),
  makeWorker('w-3',  'Kavitha Nair',      'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-1', 21, 3, 1, 0),
  makeWorker('w-4',  'Anand Krishnan',    'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4', 15, 4, 3, 1),
  makeWorker('w-5',  'Meera Pillai',      'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4', 12, 2, 5, 0),
  makeWorker('w-6',  'Deepak Tiwari',     'Senior Backend Developer',  'team-1', 'tl-1', 'sup-1', 'proj-1', 19, 2, 2, 0),
  makeWorker('w-7',  'Preethi Suresh',    'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4', 9,  3, 4, 2),
  makeWorker('w-8',  'Vishal Chandra',    'API Engineer',              'team-1', 'tl-1', 'sup-1', 'proj-1', 17, 2, 3, 0),
  makeWorker('w-9',  'Neeta Bose',        'Database Engineer',         'team-1', 'tl-1', 'sup-1', 'proj-1', 22, 1, 2, 0),
  makeWorker('w-10', 'Sanjay Mishra',     'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4', 14, 3, 3, 1),
  makeWorker('w-11', 'Pooja Sharma',      'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-9', 11, 2, 4, 0),
  makeWorker('w-12', 'Ajay Kapoor',       'Senior API Engineer',       'team-1', 'tl-1', 'sup-1', 'proj-9', 20, 4, 1, 0),
  makeWorker('w-13', 'Lavanya Reddy',     'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-9', 13, 2, 3, 1),
  makeWorker('w-14', 'Rahul Singhania',   'Database Architect',        'team-1', 'tl-1', 'sup-1', 'proj-1', 25, 1, 1, 0),
  makeWorker('w-15', 'Tanvi Deshpande',   'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4', 10, 2, 5, 1),
  makeWorker('w-16', 'Karan Ahuja',       'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-4',  8, 3, 4, 0, 'ON_LEAVE'),
  makeWorker('w-17', 'Nidhi Choudhary',   'Backend Developer',         'team-1', 'tl-1', 'sup-1', null,      7, 0, 0, 0, 'UNAVAILABLE'),
  makeWorker('w-18', 'Ganesh Iyer',       'Backend Developer',         'team-1', 'tl-1', 'sup-1', 'proj-9', 16, 2, 2, 0),

  // Frontend Engineering (team-2, sup-2, tl-2) — 15 members
  makeWorker('w-19', 'Aisha Fernandez',   'Senior Frontend Developer', 'team-2', 'tl-2', 'sup-2', 'proj-2', 22, 3, 1, 0),
  makeWorker('w-20', 'Ritu Jain',         'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-2', 16, 4, 2, 0),
  makeWorker('w-21', 'Abhishek Kumar',    'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 19, 2, 3, 1),
  makeWorker('w-22', 'Shalini Menon',     'React Developer',           'team-2', 'tl-2', 'sup-2', 'proj-2', 14, 3, 3, 0),
  makeWorker('w-23', 'Vivek Nanda',       'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 11, 2, 4, 1),
  makeWorker('w-24', 'Ishita Chatterjee', 'UI Developer',              'team-2', 'tl-2', 'sup-2', 'proj-2', 18, 3, 2, 0),
  makeWorker('w-25', 'Manish Thakur',     'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 13, 2, 3, 0),
  makeWorker('w-26', 'Prachi Saxena',     'Senior React Developer',    'team-2', 'tl-2', 'sup-2', 'proj-2', 20, 4, 1, 0),
  makeWorker('w-27', 'Vinay Hegde',       'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 15, 1, 4, 0),
  makeWorker('w-28', 'Chitra Sundaram',   'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-2',  9, 2, 5, 0, 'ON_LEAVE'),
  makeWorker('w-29', 'Akash Wadhwa',      'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 12, 3, 2, 0),
  makeWorker('w-30', 'Rekha Nambiar',     'Web Developer',             'team-2', 'tl-2', 'sup-2', 'proj-2', 17, 2, 2, 0),
  makeWorker('w-31', 'Tushar Goel',       'Frontend Developer',        'team-2', 'tl-2', 'sup-2', null,      6, 0, 0, 0, 'UNAVAILABLE'),
  makeWorker('w-32', 'Bhavna Shukla',     'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-7', 14, 2, 3, 1),
  makeWorker('w-33', 'Mohit Arora',       'Frontend Developer',        'team-2', 'tl-2', 'sup-2', 'proj-2', 10, 3, 3, 0),

  // QA & Testing (team-3, sup-3, tl-3) — 12 members
  makeWorker('w-34', 'Sangeetha Pillai',  'Senior QA Engineer',        'team-3', 'tl-3', 'sup-3', 'proj-3', 28, 3, 2, 0),
  makeWorker('w-35', 'Ravi Krishnamurti', 'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-3', 19, 4, 3, 1),
  makeWorker('w-36', 'Swati Pandey',      'Test Automation Engineer',  'team-3', 'tl-3', 'sup-3', 'proj-3', 22, 2, 2, 0),
  makeWorker('w-37', 'Nikhil Banerjee',   'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-10',16, 3, 3, 1),
  makeWorker('w-38', 'Saranya Gopalan',   'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-3', 14, 2, 4, 0),
  makeWorker('w-39', 'Praveen Pillai',    'Performance Test Engineer', 'team-3', 'tl-3', 'sup-3', 'proj-10',18, 2, 2, 0),
  makeWorker('w-40', 'Hemalatha Iyengar', 'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-3', 21, 3, 1, 0),
  makeWorker('w-41', 'Karthik Subramaniam','QA Engineer',              'team-3', 'tl-3', 'sup-3', 'proj-10',13, 2, 3, 0),
  makeWorker('w-42', 'Nandini Krishnan',  'QA Lead',                   'team-3', 'tl-3', 'sup-3', 'proj-3', 25, 4, 1, 0),
  makeWorker('w-43', 'Balaji Venkatesh',  'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-10',17, 2, 3, 1),
  makeWorker('w-44', 'Asha Malhotra',     'QA Engineer',               'team-3', 'tl-3', 'sup-3', null,       5, 0, 0, 0, 'ON_LEAVE'),
  makeWorker('w-45', 'Ramesh Ganesan',    'QA Engineer',               'team-3', 'tl-3', 'sup-3', 'proj-3', 20, 3, 2, 0),

  // UI/UX Design (team-4, sup-4, tl-4) — 8 members
  makeWorker('w-46', 'Kavya Anand',       'Senior UX Designer',        'team-4', 'tl-4', 'sup-4', 'proj-5', 16, 3, 1, 0),
  makeWorker('w-47', 'Siddharth Menon',   'UI Designer',               'team-4', 'tl-4', 'sup-4', 'proj-5', 12, 2, 3, 0),
  makeWorker('w-48', 'Preeti Chandra',    'UX Researcher',             'team-4', 'tl-4', 'sup-4', 'proj-8', 10, 2, 2, 0),
  makeWorker('w-49', 'Lokesh Rao',        'UI/UX Designer',            'team-4', 'tl-4', 'sup-4', 'proj-5', 14, 3, 2, 0),
  makeWorker('w-50', 'Gayathri Nair',     'UI Designer',               'team-4', 'tl-4', 'sup-4', 'proj-8',  9, 2, 3, 1),
  makeWorker('w-51', 'Arun Sivakumar',    'Interaction Designer',      'team-4', 'tl-4', 'sup-4', 'proj-5', 11, 3, 2, 0),
  makeWorker('w-52', 'Meghna Bhatt',      'UI Designer',               'team-4', 'tl-4', 'sup-4', 'proj-8',  8, 1, 4, 0),
  makeWorker('w-53', 'Rajeev Tripathi',   'UX Designer',               'team-4', 'tl-4', 'sup-4', null,       4, 0, 0, 0, 'UNAVAILABLE'),

  // DevOps (team-5, sup-5, tl-5) — 7 members
  makeWorker('w-54', 'Sudhir Rao',        'Senior DevOps Engineer',    'team-5', 'tl-5', 'sup-5', 'proj-6', 18, 3, 2, 0),
  makeWorker('w-55', 'Aparna Krishnan',   'DevOps Engineer',           'team-5', 'tl-5', 'sup-5', 'proj-6', 14, 2, 3, 0),
  makeWorker('w-56', 'Rohit Jha',         'Cloud Engineer',            'team-5', 'tl-5', 'sup-5', 'proj-12',11, 3, 2, 1),
  makeWorker('w-57', 'Sunitha Rajan',     'DevOps Engineer',           'team-5', 'tl-5', 'sup-5', 'proj-6', 16, 2, 2, 0),
  makeWorker('w-58', 'Harish Nambiar',    'Infrastructure Engineer',   'team-5', 'tl-5', 'sup-5', 'proj-12',13, 3, 1, 0),
  makeWorker('w-59', 'Varun Malhotra',    'DevOps Engineer',           'team-5', 'tl-5', 'sup-5', 'proj-6', 10, 2, 4, 1),
  makeWorker('w-60', 'Rani Pillai',       'SRE Engineer',              'team-5', 'tl-5', 'sup-5', 'proj-12',15, 2, 3, 0),

  // Product & Integration (team-6, sup-4, tl-6) — 10 members
  makeWorker('w-61', 'Ashok Rajan',       'Product Manager',           'team-6', 'tl-6', 'sup-4', 'proj-11',12, 4, 2, 0),
  makeWorker('w-62', 'Isha Sharma',       'Integration Engineer',      'team-6', 'tl-6', 'sup-4', 'proj-11',15, 3, 3, 1),
  makeWorker('w-63', 'Deepika Nair',      'Business Analyst',          'team-6', 'tl-6', 'sup-4', 'proj-11',10, 2, 3, 0),
  makeWorker('w-64', 'Kapil Dev',         'Integration Developer',     'team-6', 'tl-6', 'sup-4', 'proj-11',18, 3, 2, 0),
  makeWorker('w-65', 'Smita Gokhale',     'API Integration Engineer',  'team-6', 'tl-6', 'sup-4', 'proj-11',14, 2, 3, 1),
  makeWorker('w-66', 'Arvind Subramanian','Technical Writer',          'team-6', 'tl-6', 'sup-4', 'proj-11', 8, 1, 3, 0),
  makeWorker('w-67', 'Nalini Krishnamurthy','Integration Specialist',  'team-6', 'tl-6', 'sup-4', 'proj-11',13, 3, 2, 0),
  makeWorker('w-68', 'Suren Babu',        'Integration Engineer',      'team-6', 'tl-6', 'sup-4', 'proj-11',11, 2, 4, 0),
  makeWorker('w-69', 'Thilaga Ravi',      'Business Analyst',          'team-6', 'tl-6', 'sup-4', null,       5, 0, 0, 0, 'ON_LEAVE'),
  makeWorker('w-70', 'Jagannathan Pillai','Integration Developer',     'team-6', 'tl-6', 'sup-4', 'proj-11',16, 3, 2, 0),
];
