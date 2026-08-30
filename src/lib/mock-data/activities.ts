import { ProjectActivity } from '@/types';

const now = new Date('2026-08-30T14:00:00Z');

function minsAgo(mins: number): string {
  return new Date(now.getTime() - mins * 60 * 1000).toISOString();
}

function hoursAgo(hours: number): string {
  return minsAgo(hours * 60);
}

function daysAgo(days: number): string {
  return hoursAgo(days * 24);
}

export const PROJECT_ACTIVITIES: ProjectActivity[] = [
  // Recent
  {
    id: 'act-1',
    projectId: 'proj-1',
    description: 'Rohan Verma completed Invoice Generation API task',
    userId: 'w-1',
    userName: 'Rohan Verma',
    timestamp: minsAgo(12),
    type: 'TASK_COMPLETED',
  },
  {
    id: 'act-2',
    projectId: 'proj-3',
    description: 'Sangeetha Pillai updated CRM email integration progress',
    userId: 'w-34',
    userName: 'Sangeetha Pillai',
    timestamp: minsAgo(42),
    type: 'TASK_UPDATED',
  },
  {
    id: 'act-3',
    projectId: 'proj-11',
    description: 'Isha Sharma reported a blocker: PayU credentials not received',
    userId: 'w-62',
    userName: 'Isha Sharma',
    timestamp: hoursAgo(1),
    type: 'BLOCKER_REPORTED',
  },
  {
    id: 'act-4',
    projectId: 'proj-4',
    description: 'Amit Sharma changed Automation Platform priority to HIGH',
    userId: 'sup-1',
    userName: 'Amit Sharma',
    timestamp: hoursAgo(2),
    type: 'PROJECT_UPDATED',
  },
  {
    id: 'act-5',
    projectId: 'proj-7',
    description: 'Vivek Nanda updated document upload module progress',
    userId: 'w-23',
    userName: 'Vivek Nanda',
    timestamp: hoursAgo(3),
    type: 'TASK_UPDATED',
  },
  {
    id: 'act-6',
    projectId: 'proj-2',
    description: 'Aisha Fernandez completed reservation engine core logic',
    userId: 'w-19',
    userName: 'Aisha Fernandez',
    timestamp: hoursAgo(4),
    type: 'TASK_COMPLETED',
  },
  {
    id: 'act-7',
    projectId: 'proj-9',
    description: 'Ajay Kapoor completed live chat WebSocket integration',
    userId: 'w-12',
    userName: 'Ajay Kapoor',
    timestamp: hoursAgo(5),
    type: 'TASK_COMPLETED',
  },
  {
    id: 'act-8',
    projectId: 'proj-3',
    description: 'Ravi Krishnamurti reported a blocker: email server SSL certificate issue',
    userId: 'w-35',
    userName: 'Ravi Krishnamurti',
    timestamp: hoursAgo(6),
    type: 'BLOCKER_REPORTED',
  },
  {
    id: 'act-9',
    projectId: 'proj-6',
    description: 'Sudhir Rao updated database migration progress to 65%',
    userId: 'w-54',
    userName: 'Sudhir Rao',
    timestamp: daysAgo(1),
    type: 'TASK_UPDATED',
  },
  {
    id: 'act-10',
    projectId: 'proj-5',
    description: 'Kavya Anand completed leave request workflow design',
    userId: 'w-46',
    userName: 'Kavya Anand',
    timestamp: daysAgo(1),
    type: 'TASK_COMPLETED',
  },
  {
    id: 'act-11',
    projectId: 'proj-11',
    description: 'Neha Kulkarni updated Payment Gateway deadline',
    userId: 'sup-4',
    userName: 'Neha Kulkarni',
    timestamp: daysAgo(2),
    type: 'PROJECT_UPDATED',
  },
  {
    id: 'act-12',
    projectId: 'proj-7',
    description: 'Bhavna Shukla reported compliance audit log blocker',
    userId: 'w-32',
    userName: 'Bhavna Shukla',
    timestamp: daysAgo(2),
    type: 'BLOCKER_REPORTED',
  },
  {
    id: 'act-13',
    projectId: 'proj-10',
    description: 'Nikhil Banerjee completed product catalog module',
    userId: 'w-37',
    userName: 'Nikhil Banerjee',
    timestamp: daysAgo(3),
    type: 'TASK_COMPLETED',
  },
  {
    id: 'act-14',
    projectId: 'proj-4',
    description: 'Deepak Tiwari reported ERP vendor API documentation blocker',
    userId: 'w-4',
    userName: 'Deepak Tiwari',
    timestamp: daysAgo(3),
    type: 'BLOCKER_REPORTED',
  },
  {
    id: 'act-15',
    projectId: 'proj-2',
    description: 'Priya Deshmukh added Rekha Nambiar to Resort Management project',
    userId: 'sup-2',
    userName: 'Priya Deshmukh',
    timestamp: daysAgo(4),
    type: 'MEMBER_ADDED',
  },
];
