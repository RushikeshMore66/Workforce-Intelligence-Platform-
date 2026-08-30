import { DashboardMetrics, AttentionItem } from '@/types';

function delay(ms = 200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class DashboardRepository {
  async getMetrics(): Promise<DashboardMetrics> {
    await delay();
    return {
      activeProjects: 12,
      completedProjects: 3,
      totalWorkers: 70,
      workersActive: 61,
      workersOnLeave: 5,
      workersUnavailable: 4,
      tasksCompleted: 284,
      tasksInProgress: 91,
      tasksPending: 64,
      tasksBlocked: 8,
      projectsOnTrack: 6,
      projectsAtRisk: 3,
      projectsDelayed: 2,
    };
  }

  async getAttentionItems(): Promise<AttentionItem[]> {
    await delay(150);
    return [
      {
        id: 'att-1',
        title: 'CRM Development deadline approaching',
        description: 'Project is only 28% complete with 30 days to deadline. Significant risk of delay.',
        priority: 'HIGH',
        projectId: 'proj-3',
        type: 'DEADLINE',
      },
      {
        id: 'att-2',
        title: 'Payment Gateway Integration has 2 open blockers',
        description: 'Razorpay and PayU integrations blocked. Client credentials still pending.',
        priority: 'HIGH',
        projectId: 'proj-11',
        type: 'BLOCKER',
      },
      {
        id: 'att-3',
        title: 'Workflow Automation Platform behind target',
        description: '18% progress against 30% target. ERP vendor documentation still unresolved.',
        priority: 'HIGH',
        projectId: 'proj-4',
        type: 'RISK',
      },
      {
        id: 'att-4',
        title: 'Design System project past deadline',
        description: 'Deadline was August 31. Project at 44% completion. Deadline extension needed.',
        priority: 'MEDIUM',
        projectId: 'proj-8',
        type: 'DEADLINE',
      },
      {
        id: 'att-5',
        title: 'Backend Engineering team at high workload',
        description: 'Team handling 3 simultaneous projects. Monitor for quality and delivery risk.',
        priority: 'MEDIUM',
        type: 'OVERLOAD',
      },
      {
        id: 'att-6',
        title: 'Client Portal progress review required',
        description: 'Supervisor Priya Deshmukh flagged the project for owner review at next milestone.',
        priority: 'LOW',
        projectId: 'proj-7',
        type: 'REVIEW',
      },
    ];
  }
}

export const mockDashboardRepo = new DashboardRepository();
