'use client';
import { useEffect, useState } from 'react';
import Sidebar from '../components/sidebar';
import { getOverview, getRecentReplies, getSentimentBreakdown } from '../lib/api';
import { MessageCircle, Bot, Zap, Clock, TrendingUp } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function Dashboard() {
    const [overview, setOverview] = useState<any>(null);
    const [replies, setReplies] = useState<any[]>([]);
    const [sentiment, setSentiment] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                const [ov, rep, sent] = await Promise.all([
                    getOverview(INFLUENCER_ID),
                    getRecentReplies(INFLUENCER_ID),
                    getSentimentBreakdown(INFLUENCER_ID)
                ]);
                setOverview(ov);
                setReplies(rep.replies || []);
                setSentiment(sent.sentiment_breakdown);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    if (loading) return (
        <div className="flex min-h-screen bg-gray-950">
            <Sidebar />
            <div className="flex-1 flex items-center justify-center">
                <div className="text-white text-xl animate-pulse">Loading...</div>
            </div>
        </div>
    );

    return (
        <div className="flex min-h-screen bg-gray-950 text-white">
            <Sidebar />
            <div className="flex-1 px-8 py-6">
                <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

                {/* Stats Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <StatCard icon={<MessageCircle size={20} />} label="Total Comments" value={overview?.overview?.total_comments || 0} color="blue" />
                    <StatCard icon={<Bot size={20} />} label="AI Handled" value={overview?.breakdown?.ai_handled || 0} sub={`${overview?.breakdown?.ai_percentage || 0}%`} color="purple" />
                    <StatCard icon={<Zap size={20} />} label="Rule Handled" value={overview?.breakdown?.rule_handled || 0} sub={`${overview?.breakdown?.rule_percentage || 0}%`} color="yellow" />
                    <StatCard icon={<Clock size={20} />} label="Pending Review" value={overview?.overview?.pending_review || 0} color="orange" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Recent Replies */}
                    <div className="md:col-span-2 bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <MessageCircle size={18} className="text-purple-400" />
                            Recent Replies
                        </h2>
                        <div className="space-y-4">
                            {replies.length === 0 && <p className="text-gray-500 text-sm">No replies yet</p>}
                            {replies.map((reply) => (
                                <div key={reply.reply_id} className="border border-gray-800 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-purple-400 font-medium">@{reply.username}</span>
                                        <span className={`text-xs px-2 py-1 rounded-full ${reply.source === 'ai' ? 'bg-purple-900 text-purple-300' : 'bg-yellow-900 text-yellow-300'}`}>
                                            {reply.source === 'ai' ? '🤖 AI' : '⚡ Rule'}
                                        </span>
                                    </div>
                                    <p className="text-gray-400 text-sm mb-2">"{reply.comment_text}"</p>
                                    <p className="text-white text-sm">↳ {reply.reply_text}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Sentiment */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <TrendingUp size={18} className="text-green-400" />
                            Sentiment
                        </h2>
                        <div className="space-y-3">
                            {sentiment && Object.entries(sentiment).map(([key, value]: any) => (
                                value > 0 && (
                                    <div key={key} className="flex items-center justify-between">
                                        <span className="text-gray-400 text-sm capitalize">{key}</span>
                                        <div className="flex items-center gap-2">
                                            <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                                                <div className="h-full bg-purple-500 rounded-full" style={{ width: `${Math.min((value / (overview?.overview?.total_comments || 1)) * 100, 100)}%` }} />
                                            </div>
                                            <span className="text-white text-sm font-medium w-4">{value}</span>
                                        </div>
                                    </div>
                                )
                            ))}
                        </div>
                        <div className="mt-6 pt-6 border-t border-gray-800">
                            <h3 className="text-sm font-medium text-gray-400 mb-3">Today</h3>
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">Comments</span>
                                    <span className="text-white font-medium">{overview?.overview?.today || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">This Week</span>
                                    <span className="text-white font-medium">{overview?.overview?.this_week || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">Collab Requests</span>
                                    <span className="text-yellow-400 font-medium">{overview?.overview?.collab_requests || 0}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, sub, color }: any) {
    const colors: any = {
        blue: 'bg-blue-900/30 border-blue-800 text-blue-400',
        purple: 'bg-purple-900/30 border-purple-800 text-purple-400',
        yellow: 'bg-yellow-900/30 border-yellow-800 text-yellow-400',
        orange: 'bg-orange-900/30 border-orange-800 text-orange-400',
    };
    return (
        <div className={`rounded-xl p-4 border ${colors[color]}`}>
            <div className="flex items-center gap-2 mb-2">{icon}<span className="text-xs text-gray-400">{label}</span></div>
            <div className="text-2xl font-bold text-white">{value}</div>
            {sub && <div className="text-xs mt-1">{sub}</div>}
        </div>
    );
}