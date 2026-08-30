/* eslint-disable @typescript-eslint/no-require-imports */
const fs = require('fs');
const path = require('path');

function ensureDirSync(dirpath) {
    if (!fs.existsSync(dirpath)) {
        fs.mkdirSync(dirpath, { recursive: true });
    }
}

const files = {
    'src/app/layout.tsx': `import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Workforce Intelligence',
  description: 'Executive Workforce Intelligence Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
`,
    'src/app/globals.css': `@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 210 40% 98%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 221.2 83.2% 23.3%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 43 74% 49%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 23.3%;

    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
`,
    'src/app/page.tsx': `import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/dashboard');
}`,
    'src/app/dashboard/layout.tsx': `import { Sidebar } from '@/components/layout/sidebar';
import { Topbar } from '@/components/layout/topbar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
}`,
    'src/app/dashboard/page.tsx': `import { getDashboardMetrics } from '@/lib/api/dashboard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default async function DashboardPage() {
  const metrics = await getDashboardMetrics();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-light text-slate-900 tracking-tight">Good morning, Owner</h1>
        <p className="text-slate-500 mt-1">Here's what's happening across your organization today.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Active Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold text-slate-900">{metrics.activeProjects}</div>
            <p className="text-xs text-slate-400 mt-1">64 active today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Team Members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold text-slate-900">{metrics.teamMembers}</div>
            <p className="text-xs text-slate-400 mt-1">All active today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Overall Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold text-slate-900">{metrics.overallProgress}%</div>
            <p className="text-xs text-slate-400 mt-1">+6.4% from last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Projects At Risk</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold text-red-600">{metrics.projectsAtRisk}</div>
            <p className="text-xs text-slate-400 mt-1">Requires attention</p>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-medium text-slate-900">Project Performance</h2>
            <Card>
                <div className="p-6">
                    <p className="text-slate-500">Project table will be rendered here.</p>
                </div>
            </Card>
        </div>
        <div className="space-y-6">
            <h2 className="text-xl font-medium text-slate-900">Attention Required</h2>
            <Card>
                <div className="p-6">
                    <p className="text-slate-500">Alerts will be rendered here.</p>
                </div>
            </Card>
        </div>
      </div>
    </div>
  );
}`,
    'src/components/layout/sidebar.tsx': `import Link from 'next/link';

export function Sidebar() {
  return (
    <div className="w-64 bg-slate-900 text-slate-300 flex flex-col h-full border-r border-slate-800">
      <div className="p-6 mb-4">
        <h2 className="text-xl font-semibold text-white tracking-wide">Workforce</h2>
        <p className="text-xs text-slate-500 uppercase tracking-widest mt-1">Intelligence</p>
      </div>
      
      <nav className="flex-1 px-4 space-y-6">
        <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">Overview</h3>
            <div className="space-y-1">
                <Link href="/dashboard" className="flex items-center px-2 py-2 text-sm bg-slate-800 text-white rounded-md">Dashboard</Link>
            </div>
        </div>
        
        <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">Management</h3>
            <div className="space-y-1">
                <Link href="/projects" className="flex items-center px-2 py-2 text-sm hover:text-white rounded-md transition-colors">Projects</Link>
                <Link href="/supervisors" className="flex items-center px-2 py-2 text-sm hover:text-white rounded-md transition-colors">Supervisors</Link>
                <Link href="/teams" className="flex items-center px-2 py-2 text-sm hover:text-white rounded-md transition-colors">Teams</Link>
                <Link href="/workforce" className="flex items-center px-2 py-2 text-sm hover:text-white rounded-md transition-colors">Workforce</Link>
            </div>
        </div>
      </nav>
    </div>
  );
}`,
    'src/components/layout/topbar.tsx': `export function Topbar() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
      <div className="flex-1 flex items-center">
        <input 
            type="text" 
            placeholder="Search across the organization..." 
            className="w-96 text-sm px-4 py-2 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900/10"
        />
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-sm font-medium text-slate-700">Owner</div>
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300"></div>
      </div>
    </header>
  );
}`,
    'src/components/ui/card.tsx': `import * as React from "react"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={\`rounded-xl border border-slate-200 bg-white text-slate-950 shadow-sm \${className || ''}\`} {...props} />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={\`flex flex-col space-y-1.5 p-6 \${className || ''}\`} {...props} />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(({ className, ...props }, ref) => (
  <h3 ref={ref} className={\`font-semibold leading-none tracking-tight \${className || ''}\`} {...props} />
))
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={\`p-6 pt-0 \${className || ''}\`} {...props} />
))
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }`,
    'src/lib/api/dashboard.ts': `export async function getDashboardMetrics() {
    return {
        activeProjects: 12,
        teamMembers: 70,
        overallProgress: 68,
        projectsAtRisk: 2
    };
}`
};

Object.keys(files).forEach(filepath => {
    ensureDirSync(path.dirname(filepath));
    fs.writeFileSync(filepath, files[filepath]);
});
console.log('Setup complete.');
