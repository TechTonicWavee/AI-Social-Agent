'use client';
import { useEffect, useState } from 'react';
import { getPendingApprovals, approveReply } from '../../../lib/api';
import { Clock, Check, X, Edit } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function ApprovalsPage() {
    const [pending, setPending] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editText, setEditText] = useState('');

    useEffect(() => {
        loadPending();
    }, []);

    async function loadPending() {
        const data = await getPendingApprovals(INFLUENCER_ID);
        setPending(data.pending || []);
        setLoading(false);
    }

    async function handleApprove(replyId: string, text?: string) {
        await approveReply(INFLUENCER_ID, {
            reply_id: replyId,
            action: 'approve',
            text: text || undefined
        });
        await loadPending();
        setEditingId(null);
    }

    async function handleReject(replyId: string) {
        await approveReply(INFLUENCER_ID, {
            reply_id: replyId,
            action: 'reject'
        });
        await loadPending();
    }

    return (
        <div className="p-8 text-white">
            <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <Clock className="text-orange-400" size={24} />
                Pending Approvals
            </h1>
            <p className="text-gray-400 text-sm mb-6">
                Review and approve AI-generated replies before they go live
            </p>

            {loading && <p className="text-gray-500">Loading...</p>}

            {!loading && pending.length === 0 && (
                <div className="bg-gray-900 rounded-xl p-8 border border-gray-800 text-center">
                    <Clock size={32} className="text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-400">No pending approvals</p>
                    <p className="text-gray-600 text-sm mt-1">
                        Switch a post to Review mode to see replies here
                    </p>
                </div>
            )}

            <div className="space-y-4">
                {pending.map((item) => (
                    <div key={item.reply_id} className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <div className="mb-4">
                            <span className="text-sm text-purple-400 font-medium">
                                @{item.username}
                            </span>
                            <p className="text-gray-400 text-sm mt-1">
                                "{item.comment_text}"
                            </p>
                        </div>

                        <div className="bg-gray-800 rounded-lg p-4 mb-4">
                            <p className="text-xs text-gray-500 mb-2">AI Suggested Reply:</p>
                            {editingId === item.reply_id ? (
                                <textarea
                                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500 resize-none"
                                    rows={3}
                                    value={editText}
                                    onChange={e => setEditText(e.target.value)}
                                />
                            ) : (
                                <p className="text-white text-sm">{item.suggested_reply}</p>
                            )}
                        </div>

                        <div className="flex items-center gap-3">
                            {editingId === item.reply_id ? (
                                <>
                                    <button
                                        onClick={() => handleApprove(item.reply_id, editText)}
                                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        <Check size={14} />
                                        Send Edited
                                    </button>
                                    <button
                                        onClick={() => setEditingId(null)}
                                        className="text-gray-400 hover:text-white text-sm px-3 py-2 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button
                                        onClick={() => handleApprove(item.reply_id)}
                                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        <Check size={14} />
                                        Approve & Send
                                    </button>
                                    <button
                                        onClick={() => {
                                            setEditingId(item.reply_id);
                                            setEditText(item.suggested_reply);
                                        }}
                                        className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        <Edit size={14} />
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleReject(item.reply_id)}
                                        className="flex items-center gap-2 text-red-400 hover:text-red-300 px-3 py-2 text-sm transition-colors"
                                    >
                                        <X size={14} />
                                        Reject
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}