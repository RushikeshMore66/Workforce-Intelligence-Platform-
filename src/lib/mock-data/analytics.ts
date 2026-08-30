import { AnalyticsData } from '@/types';

export const ANALYTICS_DATA: AnalyticsData = {
  taskCompletion: [
    { month: 'Mar', completed: 28, inProgress: 18, blocked: 2 },
    { month: 'Apr', completed: 35, inProgress: 22, blocked: 3 },
    { month: 'May', completed: 42, inProgress: 26, blocked: 4 },
    { month: 'Jun', completed: 51, inProgress: 31, blocked: 5 },
    { month: 'Jul', completed: 63, inProgress: 35, blocked: 6 },
    { month: 'Aug', completed: 65, inProgress: 38, blocked: 8 },
  ],

  teamWorkload: [
    { team: 'Backend',  tasks: 36, completed: 18, blocked: 3 },
    { team: 'Frontend', tasks: 28, completed: 14, blocked: 2 },
    { team: 'QA',       tasks: 22, completed: 12, blocked: 1 },
    { team: 'DevOps',   tasks: 14, completed:  8, blocked: 1 },
    { team: 'UI/UX',    tasks: 12, completed:  6, blocked: 1 },
    { team: 'Product',  tasks: 18, completed:  8, blocked: 0 },
  ],

  projectProgress: [
    { name: 'Hotel Billing',    progress: 76, target: 80 },
    { name: 'Resort Mgmt',      progress: 48, target: 55 },
    { name: 'CRM Dev',          progress: 28, target: 50 },
    { name: 'Automation',       progress: 18, target: 30 },
    { name: 'Employee Portal',  progress: 62, target: 65 },
    { name: 'Cloud Migration',  progress: 55, target: 60 },
    { name: 'Client Portal',    progress: 41, target: 50 },
    { name: 'Payment Gateway',  progress: 22, target: 25 },
    { name: 'Design System',    progress: 44, target: 70 },
    { name: 'Support Platform', progress: 58, target: 60 },
  ],

  workloadTrend: [
    { week: 'Jul W1', backend: 28, frontend: 22, qa: 18, devops: 10, uiux: 9 },
    { week: 'Jul W2', backend: 30, frontend: 24, qa: 19, devops: 11, uiux: 10 },
    { week: 'Jul W3', backend: 32, frontend: 25, qa: 20, devops: 12, uiux: 10 },
    { week: 'Jul W4', backend: 34, frontend: 26, qa: 21, devops: 13, uiux: 11 },
    { week: 'Aug W1', backend: 35, frontend: 27, qa: 21, devops: 13, uiux: 12 },
    { week: 'Aug W2', backend: 36, frontend: 28, qa: 22, devops: 14, uiux: 12 },
    { week: 'Aug W3', backend: 36, frontend: 28, qa: 22, devops: 14, uiux: 12 },
  ],
};
