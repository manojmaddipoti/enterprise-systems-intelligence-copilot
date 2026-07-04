import type { Metadata } from 'next';
import Link from 'next/link';
import { Activity, Bot, ClipboardList, FileClock, Gauge, ShieldCheck, Users } from 'lucide-react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Enterprise Systems Intelligence Copilot',
  description: 'Local-first governed enterprise AI copilot over synthetic systems data.',
};

const navItems = [
  { href: '/', label: 'Chat', icon: Bot },
  { href: '/dashboard', label: 'Workflow Health', icon: Gauge },
  { href: '/exceptions', label: 'Exceptions', icon: Activity },
  { href: '/supplier', label: 'Supplier 360', icon: Users },
  { href: '/drafts', label: 'Draft Actions', icon: ClipboardList },
  { href: '/audit', label: 'Audit Log', icon: ShieldCheck },
  { href: '/evals', label: 'Eval Results', icon: FileClock },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <div className="brand">
              <ShieldCheck size={24} />
              <span>Enterprise Systems Intelligence Copilot</span>
            </div>
            <nav className="nav" aria-label="Primary">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.href} href={item.href}>
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
