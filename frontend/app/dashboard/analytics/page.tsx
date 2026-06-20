'use client';
import { useEffect, useState } from 'react';
import { getOverview, getSentimentBreakdown } from '../../../lib/api';
import { BarChart2, TrendingUp, MessageCircle, Bot, Zap } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function AnalyticsPage() {
    const [overview, setOverview] = useState<any>(null);
    const [sentiment, setSentiment] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const [ov, sent] = await Promise.all([
                getOverview(INFLUENCER_ID),
                getSentimentBreakdown(INFLUENCER_ID)
            ]);
            setOverview(ov);
            setSentiment(sent.sentiment_breakdown);
            setLoading(false);
        }
        load();
    }, []);

    if (loading) return (
        <div className="p-8 text-white">
            <p className="text-gray-400 animate-pulse">Loading analytics...</p>
        </div>
    );

    const total = overview?.overview?.total_comments || 0;
    const aiHandled = overview?.breakdown?.ai_handled || 0;
    const ruleHandled = overview?.breakdown?.rule_handled || 0;
    const pending = overview?.overview?.pending_review || 0;

    return (
        <div className="p-8 text-white">
            <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <BarChart2 className="text-purple-400" size={24} />
                Analytics
            </h1>

            {/* Top Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                    { label: 'Total Comments', value: total, color: 'blue', icon: <MessageCircle size={18} /> },
                    { label: 'AI Replied', value: aiHandled, color: 'purple', icon: <Bot size={18} /> },
                    { label: 'Rule Replied', value: ruleHandled, color: 'yellow', icon: <Zap size={18} /> },
                    { label: 'Pending', value: pending, color: 'orange', icon: <TrendingUp size={18} /> },
                ].map((stat) => (
                    <div key={stat.label} className={`rounded-xl p-4 border ${stat.color === 'blue' ? 'bg-blue-900/30 border-blue-800' :
                            stat.color === 'purple' ? 'bg-purple-900/30 border-purple-800' :
                                stat.color === 'yellow' ? 'bg-yellow-900/30 border-yellow-800' :
                                    'bg-orange-900/30 border-orange-800'
                        }`}>
                        <div className="flex items-center gap-2 mb-2 text-gray-400">
                            {stat.icon}
                            <span className="text-xs">{stat.label}</span>
                        </div>
                        <div className="text-3xl font-bold">{stat.value}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* AI vs Rule Breakdown */}
                <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h2 className="text-lg font-semibold mb-4">Handling Breakdown</h2>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">🤖 AI Handled</span>
                                <span className="text-purple-400 font-medium">
                                    {overview?.breakdown?.ai_percentage || 0}%
                                </span>
                            </div>
                            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-purple-500 rounded-full transition-all"
                                    style={{ width: `${overview?.breakdown?.ai_percentage || 0}%` }}
                                />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">⚡ Rule Handled</span>
                                <span className="text-yellow-400 font-medium">
                                    {overview?.breakdown?.rule_percentage || 0}%
                                </span>
                            </div>
                            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-yellow-500 rounded-full transition-all"
                                    style={{ width: `${overview?.breakdown?.rule_percentage || 0}%` }}
                                />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">⏳ Pending</span>
                                <span className="text-orange-400 font-medium">
                                    {total > 0 ? Math.round((pending / total) * 100) : 0}%
                                </span>
                            </div>
                            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-orange-500 rounded-full transition-all"
                                    style={{ width: `${total > 0 ? (pending / total) * 100 : 0}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Summary */}
                    <div className="mt-6 pt-4 border-t border-gray-800">
                        <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold text-green-400">
                                    {total > 0 ? Math.round(((aiHandled + ruleHandled) / total) * 100) : 0}%
                                </div>
                                <div className="text-xs text-gray-500 mt-1">Auto-handled</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-blue-400">
                                    {overview?.overview?.this_week || 0}
                                </div>
                                <div className="text-xs text-gray-500 mt-1">This week</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Sentiment Breakdown */}
                <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h2 className="text-lg font-semibold mb-4">Sentiment Breakdown</h2>
                    <div className="space-y-3">
                        {sentiment && Object.entries(sentiment).map(([key, value]: any) => {
                            const emoji: any = {
                                question: '❓',
                                compliment: '❤️',
                                complaint: '😤',
                                spam: '🚫',
                                collab: '🤝',
                                troll: '👹',
                                other: '💬'
                            };
                            const pct = total > 0 ? Math.round((value / total) * 100) : 0;
                            return (
                                <div key={key}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400 capitalize">
                                            {emoji[key]} {key}
                                        </span>
                                        <span className="text-white font-medium">{value} ({pct}%)</span>
                                    </div>
                                    <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-purple-500 rounded-full"
                                            style={{ width: `${pct}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Key Insights */}
                    <div className="mt-6 pt-4 border-t border-gray-800">
                        <h3 className="text-sm font-medium text-gray-400 mb-3">
                            Key Insights
                        </h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex items-center gap-2 text-gray-300">
                                <span>📊</span>
                                <span>
                                    {sentiment?.question || 0} questions need detailed answers
                                </span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-300">
                                <span>🤝</span>
                                <span>
                                    {overview?.overview?.collab_requests || 0} collab opportunities
                                </span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-300">
                                <span>🚫</span>
                                <span>
                                    {overview?.overview?.auto_hidden || 0} spam comments hidden
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}