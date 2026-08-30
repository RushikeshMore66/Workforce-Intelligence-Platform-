import { Task } from '@/types';

export const TASKS: Task[] = [
  // ── Project 1: Hotel Billing System ──
  { id: 't-1',  projectId: 'proj-1', title: 'Design database schema for billing module',   assigneeId: 'w-9',  teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-03-15', createdAt: '2026-01-15T09:00:00Z' },
  { id: 't-2',  projectId: 'proj-1', title: 'Implement invoice generation API',             assigneeId: 'w-1',  teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-04-30', createdAt: '2026-02-01T09:00:00Z' },
  { id: 't-3',  projectId: 'proj-1', title: 'Payment gateway integration (Razorpay)',       assigneeId: 'w-8',  teamId: 'team-1', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-05-15', createdAt: '2026-03-01T09:00:00Z' },
  { id: 't-4',  projectId: 'proj-1', title: 'GST calculation engine',                      assigneeId: 'w-3',  teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-05-30', createdAt: '2026-03-15T09:00:00Z' },
  { id: 't-5',  projectId: 'proj-1', title: 'POS terminal integration',                    assigneeId: 'w-6',  teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-30', createdAt: '2026-04-01T09:00:00Z' },
  { id: 't-6',  projectId: 'proj-1', title: 'Automated daily billing reports',              assigneeId: 'w-14', teamId: 'team-1', status: 'COMPLETED', priority: 'MEDIUM',   dueDate: '2026-07-15', createdAt: '2026-05-01T09:00:00Z' },
  { id: 't-7',  projectId: 'proj-1', title: 'Room service billing module',                  assigneeId: 'w-2',  teamId: 'team-1', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-01', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-8',  projectId: 'proj-1', title: 'Multi-currency support',                      assigneeId: 'w-9',  teamId: 'team-1', status: 'IN_PROGRESS', priority: 'MEDIUM', dueDate: '2026-09-30', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-9',  projectId: 'proj-1', title: 'Audit trail and compliance logging',          assigneeId: 'w-14', teamId: 'team-1', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-15', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-10', projectId: 'proj-1', title: 'Performance optimization for billing engine',  assigneeId: 'w-6',  teamId: 'team-1', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-10-20', createdAt: '2026-08-10T09:00:00Z' },

  // ── Project 2: Resort Management Platform ──
  { id: 't-11', projectId: 'proj-2', title: 'Reservation engine core logic',               assigneeId: 'w-19', teamId: 'team-2', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-04-30', createdAt: '2026-03-05T09:00:00Z' },
  { id: 't-12', projectId: 'proj-2', title: 'Guest check-in/check-out workflow',           assigneeId: 'w-26', teamId: 'team-2', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-05-31', createdAt: '2026-03-15T09:00:00Z' },
  { id: 't-13', projectId: 'proj-2', title: 'Housekeeping task management module',         assigneeId: 'w-22', teamId: 'team-2', status: 'COMPLETED', priority: 'MEDIUM',   dueDate: '2026-06-15', createdAt: '2026-04-01T09:00:00Z' },
  { id: 't-14', projectId: 'proj-2', title: 'Spa & F&B billing integration',               assigneeId: 'w-24', teamId: 'team-2', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-15', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-15', projectId: 'proj-2', title: 'Guest self-service portal',                   assigneeId: 'w-20', teamId: 'team-2', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-10-01', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-16', projectId: 'proj-2', title: 'Analytics and occupancy dashboard',           assigneeId: 'w-30', teamId: 'team-2', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-11-01', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-17', projectId: 'proj-2', title: 'OTA channel manager integration',             assigneeId: 'w-33', teamId: 'team-2', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-11-30', createdAt: '2026-08-15T09:00:00Z' },

  // ── Project 3: CRM Development (DELAYED) ──
  { id: 't-18', projectId: 'proj-3', title: 'Contact management data model',               assigneeId: 'w-34', teamId: 'team-3', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-01', createdAt: '2026-05-05T09:00:00Z' },
  { id: 't-19', projectId: 'proj-3', title: 'Deal pipeline and stage tracking',            assigneeId: 'w-36', teamId: 'team-3', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-30', createdAt: '2026-05-15T09:00:00Z' },
  { id: 't-20', projectId: 'proj-3', title: 'Email integration (IMAP/SMTP)',               assigneeId: 'w-35', teamId: 'team-3', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-15', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-21', projectId: 'proj-3', title: 'Activity tracking and timeline',              assigneeId: 'w-40', teamId: 'team-3', status: 'IN_PROGRESS', priority: 'MEDIUM', dueDate: '2026-09-20', createdAt: '2026-07-10T09:00:00Z' },
  { id: 't-22', projectId: 'proj-3', title: 'Bulk import/export via CSV',                  assigneeId: 'w-42', teamId: 'team-3', status: 'BLOCKED',    priority: 'MEDIUM',   dueDate: '2026-09-25', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-23', projectId: 'proj-3', title: 'Sales analytics reporting module',            assigneeId: 'w-45', teamId: 'team-3', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-09-28', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-24', projectId: 'proj-3', title: 'User roles and permission management',       assigneeId: 'w-38', teamId: 'team-3', status: 'TODO',       priority: 'CRITICAL', dueDate: '2026-09-30', createdAt: '2026-08-05T09:00:00Z' },

  // ── Project 4: Workflow Automation (AT_RISK) ──
  { id: 't-25', projectId: 'proj-4', title: 'Drag-and-drop workflow builder UI',           assigneeId: 'w-4',  teamId: 'team-1', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-07-31', createdAt: '2026-06-05T09:00:00Z' },
  { id: 't-26', projectId: 'proj-4', title: 'Trigger and action engine',                   assigneeId: 'w-5',  teamId: 'team-1', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-30', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-27', projectId: 'proj-4', title: 'Third-party ERP integration adapters',       assigneeId: 'w-10', teamId: 'team-1', status: 'BLOCKED',    priority: 'HIGH',     dueDate: '2026-10-15', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-28', projectId: 'proj-4', title: 'Notification engine (email, SMS, push)',     assigneeId: 'w-15', teamId: 'team-1', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-10-30', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-29', projectId: 'proj-4', title: 'Workflow version control and history',       assigneeId: 'w-7',  teamId: 'team-1', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-11-15', createdAt: '2026-08-10T09:00:00Z' },

  // ── Project 5: Employee Self-Service Portal ──
  { id: 't-30', projectId: 'proj-5', title: 'Employee dashboard wireframes',               assigneeId: 'w-46', teamId: 'team-4', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-05-15', createdAt: '2026-04-20T09:00:00Z' },
  { id: 't-31', projectId: 'proj-5', title: 'Leave request and approval flow',             assigneeId: 'w-49', teamId: 'team-4', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-30', createdAt: '2026-05-01T09:00:00Z' },
  { id: 't-32', projectId: 'proj-5', title: 'Payslip viewer and download',                assigneeId: 'w-51', teamId: 'team-4', status: 'COMPLETED', priority: 'MEDIUM',   dueDate: '2026-07-15', createdAt: '2026-05-15T09:00:00Z' },
  { id: 't-33', projectId: 'proj-5', title: 'HR request ticketing module',                assigneeId: 'w-47', teamId: 'team-4', status: 'IN_PROGRESS', priority: 'MEDIUM', dueDate: '2026-08-31', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-34', projectId: 'proj-5', title: 'Company announcements portal',               assigneeId: 'w-46', teamId: 'team-4', status: 'IN_PROGRESS', priority: 'LOW',    dueDate: '2026-09-15', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-35', projectId: 'proj-5', title: 'Mobile-responsive design implementation',    assigneeId: 'w-51', teamId: 'team-4', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-09-30', createdAt: '2026-08-01T09:00:00Z' },

  // ── Project 6: Cloud Infrastructure Migration ──
  { id: 't-36', projectId: 'proj-6', title: 'Infrastructure audit and assessment',        assigneeId: 'w-54', teamId: 'team-5', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-05-31', createdAt: '2026-05-05T09:00:00Z' },
  { id: 't-37', projectId: 'proj-6', title: 'VPC and network architecture setup',         assigneeId: 'w-55', teamId: 'team-5', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-30', createdAt: '2026-05-20T09:00:00Z' },
  { id: 't-38', projectId: 'proj-6', title: 'Database migration (RDS)',                   assigneeId: 'w-57', teamId: 'team-5', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-15', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-39', projectId: 'proj-6', title: 'Application containerization (Docker)',      assigneeId: 'w-54', teamId: 'team-5', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-30', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-40', projectId: 'proj-6', title: 'CI/CD pipeline with GitHub Actions',        assigneeId: 'w-59', teamId: 'team-5', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-31', createdAt: '2026-08-10T09:00:00Z' },

  // ── Project 7: Client Portal (AT_RISK) ──
  { id: 't-41', projectId: 'proj-7', title: 'Secure login and 2FA implementation',        assigneeId: 'w-29', teamId: 'team-2', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-05-15', createdAt: '2026-04-05T09:00:00Z' },
  { id: 't-42', projectId: 'proj-7', title: 'Account dashboard and statement viewer',    assigneeId: 'w-21', teamId: 'team-2', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-06-30', createdAt: '2026-04-20T09:00:00Z' },
  { id: 't-43', projectId: 'proj-7', title: 'Document upload and management',             assigneeId: 'w-23', teamId: 'team-2', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-30', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-44', projectId: 'proj-7', title: 'Advisor messaging module',                  assigneeId: 'w-25', teamId: 'team-2', status: 'IN_PROGRESS', priority: 'MEDIUM', dueDate: '2026-10-01', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-45', projectId: 'proj-7', title: 'Audit log and compliance reports',           assigneeId: 'w-32', teamId: 'team-2', status: 'BLOCKED',    priority: 'HIGH',     dueDate: '2026-10-10', createdAt: '2026-07-20T09:00:00Z' },

  // ── Project 8: Design System (DELAYED) ──
  { id: 't-46', projectId: 'proj-8', title: 'Design token specification',                 assigneeId: 'w-48', teamId: 'team-4', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-04-30', createdAt: '2026-03-20T09:00:00Z' },
  { id: 't-47', projectId: 'proj-8', title: 'Core component library (Figma)',             assigneeId: 'w-52', teamId: 'team-4', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-08-20', createdAt: '2026-05-01T09:00:00Z' },
  { id: 't-48', projectId: 'proj-8', title: 'React component implementation',             assigneeId: 'w-50', teamId: 'team-4', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-08-25', createdAt: '2026-06-01T09:00:00Z' },
  { id: 't-49', projectId: 'proj-8', title: 'Documentation site (Storybook)',             assigneeId: 'w-48', teamId: 'team-4', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-08-31', createdAt: '2026-07-01T09:00:00Z' },

  // ── Project 9: Customer Support Platform ──
  { id: 't-50', projectId: 'proj-9', title: 'Ticket creation and routing engine',         assigneeId: 'w-12', teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-04-30', createdAt: '2026-02-20T09:00:00Z' },
  { id: 't-51', projectId: 'proj-9', title: 'Live chat integration (WebSocket)',           assigneeId: 'w-18', teamId: 'team-1', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-05-31', createdAt: '2026-03-15T09:00:00Z' },
  { id: 't-52', projectId: 'proj-9', title: 'Knowledge base article management',         assigneeId: 'w-11', teamId: 'team-1', status: 'IN_PROGRESS', priority: 'MEDIUM', dueDate: '2026-09-15', createdAt: '2026-07-01T09:00:00Z' },
  { id: 't-53', projectId: 'proj-9', title: 'SLA monitoring and escalation engine',       assigneeId: 'w-13', teamId: 'team-1', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-31', createdAt: '2026-08-01T09:00:00Z' },

  // ── Project 10: Inventory Management ──
  { id: 't-54', projectId: 'proj-10', title: 'Product catalog and SKU management',       assigneeId: 'w-37', teamId: 'team-3', status: 'COMPLETED', priority: 'HIGH',     dueDate: '2026-07-15', createdAt: '2026-06-05T09:00:00Z' },
  { id: 't-55', projectId: 'proj-10', title: 'Real-time stock tracking module',          assigneeId: 'w-43', teamId: 'team-3', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-10-01', createdAt: '2026-07-15T09:00:00Z' },
  { id: 't-56', projectId: 'proj-10', title: 'Supplier management and PO system',       assigneeId: 'w-41', teamId: 'team-3', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-11-15', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-57', projectId: 'proj-10', title: 'Reorder automation and alerts',            assigneeId: 'w-39', teamId: 'team-3', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-12-01', createdAt: '2026-08-15T09:00:00Z' },

  // ── Project 11: Payment Gateway (AT_RISK) ──
  { id: 't-58', projectId: 'proj-11', title: 'Unified payment API architecture',         assigneeId: 'w-64', teamId: 'team-6', status: 'COMPLETED', priority: 'CRITICAL', dueDate: '2026-08-15', createdAt: '2026-07-05T09:00:00Z' },
  { id: 't-59', projectId: 'proj-11', title: 'Razorpay integration',                    assigneeId: 'w-62', teamId: 'team-6', status: 'IN_PROGRESS', priority: 'CRITICAL',dueDate: '2026-09-30', createdAt: '2026-08-01T09:00:00Z' },
  { id: 't-60', projectId: 'proj-11', title: 'PayU integration',                         assigneeId: 'w-65', teamId: 'team-6', status: 'BLOCKED',    priority: 'HIGH',     dueDate: '2026-10-01', createdAt: '2026-08-05T09:00:00Z' },
  { id: 't-61', projectId: 'proj-11', title: 'Stripe integration',                       assigneeId: 'w-68', teamId: 'team-6', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-15', createdAt: '2026-08-10T09:00:00Z' },
  { id: 't-62', projectId: 'proj-11', title: 'Reconciliation dashboard',                assigneeId: 'w-61', teamId: 'team-6', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-10-25', createdAt: '2026-08-15T09:00:00Z' },
  { id: 't-63', projectId: 'proj-11', title: 'Automated refund processing',              assigneeId: 'w-67', teamId: 'team-6', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-31', createdAt: '2026-08-20T09:00:00Z' },

  // ── Project 12: Kubernetes Setup ──
  { id: 't-64', projectId: 'proj-12', title: 'Cluster architecture design',              assigneeId: 'w-56', teamId: 'team-5', status: 'IN_PROGRESS', priority: 'HIGH',   dueDate: '2026-09-30', createdAt: '2026-09-01T09:00:00Z' },
  { id: 't-65', projectId: 'proj-12', title: 'Prometheus and Grafana monitoring setup', assigneeId: 'w-60', teamId: 'team-5', status: 'TODO',       priority: 'HIGH',     dueDate: '2026-10-31', createdAt: '2026-09-05T09:00:00Z' },
  { id: 't-66', projectId: 'proj-12', title: 'ArgoCD GitOps configuration',             assigneeId: 'w-58', teamId: 'team-5', status: 'TODO',       priority: 'MEDIUM',   dueDate: '2026-11-30', createdAt: '2026-09-10T09:00:00Z' },
];
