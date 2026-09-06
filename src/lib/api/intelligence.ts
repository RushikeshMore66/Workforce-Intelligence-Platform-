/**
 * Intelligence API module.
 * Provides management intelligence insights.
 *
 * In mock mode: returns hardcoded insights (same as current intelligence page).
 * In API mode: communicates with /api/v1/intelligence endpoints.
 *
 * Design intent: the UI depends on this interface, NOT on the implementation.
 * Replacing mock with real API requires only changing this file.
 */

import { apiClient } from './client';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export type InsightPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type InsightType = 'RISK' | 'OPPORTUNITY' | 'OVERLOAD' | 'DEADLINE' | 'BLOCKER';

export interface IntelligenceInsight {
  id: string;
  priority: InsightPriority;
  type: InsightType;
  title: string;
  body: string;
  projectId?: string;
  teamId?: string;
  workerId?: string;
  actionLabel?: string;
  actionHref?: string;
}

const MOCK_INSIGHTS: IntelligenceInsight[] = [
  {
    id: 'ins-1',
    priority: 'HIGH',
    type: 'RISK',
    title: 'CRM Development is critically behind schedule',
    body: 'At 28% completion with the deadline 30 days away, the CRM project requires immediate intervention. The email integration blocker has been unresolved for 3 days and is delaying the entire milestone chain.',
    projectId: 'proj-3',
    actionLabel: 'Review CRM Project',
    actionHref: '/projects/proj-3',
  },
  {
    id: 'ins-2',
    priority: 'HIGH',
    type: 'RISK',
    title: 'Workflow Automation Platform at risk of significant delay',
    body: 'Progress at 18% vs a 30% target. The ERP vendor documentation blocker has persisted for 8 days. Without resolution within 3 business days, the November deadline becomes unachievable.',
    projectId: 'proj-4',
    actionLabel: 'View Project',
    actionHref: '/projects/proj-4',
  },
  {
    id: 'ins-3',
    priority: 'HIGH',
    type: 'OVERLOAD',
    title: 'Backend Engineering team is overloaded',
    body: 'The Backend team is simultaneously delivering 3 projects (Hotel Billing, Workflow Automation, Customer Support). With 36 active tasks, this is the highest workload of any team. Consider redistributing lower-priority tasks.',
    teamId: 'team-1',
    actionLabel: 'View Team',
    actionHref: '/teams/team-1',
  },
  {
    id: 'ins-4',
    priority: 'MEDIUM',
    type: 'OPPORTUNITY',
    title: 'Hotel Billing System on track for October delivery',
    body: "At 76% completion with a strong velocity trend, the Hotel Billing System remains your best-performing active project. No action required.",
    projectId: 'proj-1',
    actionLabel: 'View Project',
    actionHref: '/projects/proj-1',
  },
  {
    id: 'ins-5',
    priority: 'MEDIUM',
    type: 'BLOCKER',
    title: 'Payment Gateway Integration has critical blockers',
    body: 'With a CRITICAL priority and an October 31 deadline, the PayU credential blocker and Stripe integration not yet started represent a significant delivery risk for QuickPay Systems.',
    projectId: 'proj-11',
    actionLabel: 'View Project',
    actionHref: '/projects/proj-11',
  },
  {
    id: 'ins-6',
    priority: 'LOW',
    type: 'DEADLINE',
    title: 'Design System project needs deadline extension',
    body: 'The Design System project missed its August 31 deadline at 44% completion. A realistic revised target based on current velocity would be October 15. Recommend formal timeline revision.',
    projectId: 'proj-8',
    actionLabel: 'View Project',
    actionHref: '/projects/proj-8',
  },
];

export async function getIntelligenceInsights(): Promise<IntelligenceInsight[]> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return MOCK_INSIGHTS;
  }
  return apiClient.get<IntelligenceInsight[]>('/intelligence');
}
