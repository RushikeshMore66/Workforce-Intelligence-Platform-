import { Lightbulb, TrendingUp, AlertTriangle, Users } from 'lucide-react';
import Link from 'next/link';

export const metadata = { title: 'Intelligence' };

const INSIGHTS = [
  {
    id: 'ins-1', priority: 'HIGH', icon: AlertTriangle,
    bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]',
    title: 'CRM Development is critically behind schedule',
    body: 'At 28% completion with the deadline 30 days away, the CRM project requires immediate intervention. The email integration blocker has been unresolved for 3 days and is delaying the entire milestone chain.',
    action: { label: 'Review CRM Project', href: '/projects/proj-3' },
  },
  {
    id: 'ins-2', priority: 'HIGH', icon: AlertTriangle,
    bg: 'bg-[#FFFAEB]', border: 'border-[#FEDF89]', iconColor: 'text-[#B54708]',
    title: 'Workflow Automation Platform at risk of significant delay',
    body: 'Progress at 18% vs a 30% target. The ERP vendor documentation blocker has persisted for 8 days. Without resolution within 3 business days, the November deadline becomes unachievable.',
    action: { label: 'View Project', href: '/projects/proj-4' },
  },
  {
    id: 'ins-3', priority: 'HIGH', icon: Users,
    bg: 'bg-[#EEF1FA]', border: 'border-[#c7d0f0]', iconColor: 'text-[#263B80]',
    title: 'Backend Engineering team is overloaded',
    body: 'The Backend team is simultaneously delivering 3 projects (Hotel Billing, Workflow Automation, Customer Support). With 36 active tasks, this is the highest workload of any team. Consider redistributing lower-priority tasks.',
    action: { label: 'View Team', href: '/teams/team-1' },
  },
  {
    id: 'ins-4', priority: 'MEDIUM', icon: TrendingUp,
    bg: 'bg-[#ECFDF3]', border: 'border-[#ABEFC6]', iconColor: 'text-[#027A48]',
    title: 'Hotel Billing System on track for October delivery',
    body: 'At 76% completion with a strong velocity trend, the Hotel Billing System remains your best-performing active project. Rohan Verma\'s team has maintained consistent output. No action required.',
    action: { label: 'View Project', href: '/projects/proj-1' },
  },
  {
    id: 'ins-5', priority: 'MEDIUM', icon: AlertTriangle,
    bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]',
    title: 'Payment Gateway Integration has critical blockers',
    body: 'With a CRITICAL priority and an October 31 deadline, the PayU credential blocker and Stripe integration not yet started represent a significant delivery risk for QuickPay Systems.',
    action: { label: 'View Project', href: '/projects/proj-11' },
  },
  {
    id: 'ins-6', priority: 'LOW', icon: Lightbulb,
    bg: 'bg-[#FBF5E8]', border: 'border-[#e8d9be]', iconColor: 'text-[#B08A3E]',
    title: 'Design System project needs deadline extension',
    body: 'The Design System project missed its August 31 deadline at 44% completion. A realistic revised target based on current velocity would be October 15. Recommend formal timeline revision.',
    action: { label: 'View Project', href: '/projects/proj-8' },
  },
];

const PRIORITY_BADGE = {
  HIGH:   'bg-[#FEF3F2] text-[#B42318] border border-[#FECDCA]',
  MEDIUM: 'bg-[#FFFAEB] text-[#B54708] border border-[#FEDF89]',
  LOW:    'bg-[#F3F4F6] text-[#667085] border border-[#E7E8EC]',
};

export default function IntelligencePage() {
  return (
    <div className="max-w-[900px] mx-auto space-y-5">
      <div>
        <h1 className="wi-page-title">Intelligence</h1>
        <p className="text-sm text-[#667085] mt-0.5">AI-generated insights and risk signals for leadership decision-making.</p>
      </div>

      <div className="bg-[#EEF1FA] border border-[#c7d0f0] rounded-xl px-5 py-3.5 flex items-start gap-3">
        <Lightbulb className="w-4 h-4 text-[#263B80] flex-shrink-0 mt-0.5" />
        <p className="text-sm text-[#263B80]">
          <strong>Intelligence Engine:</strong> These insights are generated from project health signals, velocity trends, blocker patterns, and team workload analysis. Backend integration will enable real-time ML-powered recommendations.
        </p>
      </div>

      <div className="space-y-4">
        {INSIGHTS.map(ins => {
          const Icon = ins.icon;
          return (
            <div key={ins.id} className={`border ${ins.border} rounded-xl p-5 ${ins.bg}`}>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/60 flex items-center justify-center flex-shrink-0">
                  <Icon className={`w-4 h-4 ${ins.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <h3 className="text-sm font-semibold text-[#172033]">{ins.title}</h3>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${PRIORITY_BADGE[ins.priority as keyof typeof PRIORITY_BADGE]}`}>
                      {ins.priority}
                    </span>
                  </div>
                  <p className="text-sm text-[#374151] leading-relaxed">{ins.body}</p>
                  {ins.action && (
                    <Link href={ins.action.href} className="inline-flex items-center gap-1.5 text-xs font-medium text-[#263B80] hover:underline mt-3">
                      {ins.action.label} →
                    </Link>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
