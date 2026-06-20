'use client';
import { useEffect, useState } from 'react';
import { getRecentReplies } from '../../../lib/api';
import { MessageCircle } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function RepliesPage() {
    const [replies, setReplies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const data = await getRecentReplies(INFLUENCER_ID);
            setReplies(data.replies || []);
            setLoading(false);
        }
        load();
    }, []);

    return (
        <div className="p-8 text-white">
            <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <MessageCircle className="text-purple-400" size={24} />
                Recent Replies
            </h1>

            {loading && <p className="text-gray-500 animate-pulse">Loading...</p>}

            <div className="space-y-4">
                {!loading && replies.length === 0 && (
                    <p className="text-gray-500">No replies yet.</p>
                )}
                {replies.map((reply) => (
                    <div
                        key={reply.reply_id}
                        className="bg-gray-900 rounded-xl p-5 border border-gray-800"
                    >
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-purple-400 font-medium text-sm">
                                @{reply.username}
                            </span>
                            <div className="flex items-center gap-2">
                                <span className={`text-xs px-2 py-1 rounded-full ${reply.source === 'ai'
                                        ? 'bg-purple-900 text-purple-300'
                                        : 'bg-yellow-900 text-yellow-300'
                                    }`}>
                                    {reply.source === 'ai' ? '🤖 AI' : '⚡ Rule'}
                                </span>
                                <span className="text-xs text-gray-500">
                                    {new Date(reply.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <div className="bg-gray-800 rounded-lg px-4 py-3">
                                <p className="text-xs text-gray-500 mb-1">Comment</p>
                                <p className="text-gray-300 text-sm">"{reply.comment_text}"</p>
                            </div>
                            <div className="bg-purple-900/20 border border-purple-800/30 rounded-lg px-4 py-3">
                                <p className="text-xs text-purple-400 mb-1">Reply Sent</p>
                                <p className="text-white text-sm">{reply.reply_text}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}