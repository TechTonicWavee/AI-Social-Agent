'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot, MessageCircle, Zap, Clock, Users, BarChart2 } from 'lucide-react';

const links = [
    { href: '/', label: 'Dashboard', icon: BarChart2 },
    { href: '/dashboard/replies', label: 'Recent Replies', icon: MessageCircle },
    { href: '/dashboard/approvals', label: 'Pending Approvals', icon: Clock },
    { href: '/dashboard/rule', label: 'Rules', icon: Zap },
    { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart2 },
    { href: '/dashboard/collab', label: 'Collabs', icon: Users },
    { href: '/dashboard/test', label: 'Test Agent', icon: Bot },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="w-56 min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col">
            {/* Logo */}
            <div className="px-6 py-5 border-b border-gray-800 flex items-center gap-3">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                    <Bot size={18} className="text-white" />
                </div>
                <span className="text-white font-bold text-lg">ReplyPilot</span>
            </div>

            {/* Nav Links */}
            <nav className="flex-1 px-3 py-4 space-y-1">
                {links.map(({ href, label, icon: Icon }) => {
                    const active = pathname === href;
                    return (
                        <Link
                            key={href}
                            href={href}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${active
                                ? 'bg-purple-600 text-white'
                                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                }`}
                        >
                            <Icon size={16} />
                            {label}
                        </Link>
                    );
                })}
            </nav>

            {/* Status */}
            <div className="px-6 py-4 border-t border-gray-800">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-gray-400">System Live</span>
                </div>
            </div>
        </div>
    );
}