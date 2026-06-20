'use client';
import { useState } from 'react';
import { testAgent } from '../../../lib/api';
import { Bot, Send, Zap, MessageCircle } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function TestPage() {
    const [comment, setComment] = useState('');
    const [username, setUsername] = useState('test_user');
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    async function handleTest() {
        if (!comment.trim()) return;
        setLoading(true);
        setResult(null);
        try {
            const data = await testAgent({
                comment,
                influencer_id: INFLUENCER_ID,
                username
            });
            setResult(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }

    const sentimentColors: any = {
        question: 'text-blue-400',
        compliment: 'text-pink-400',
        complaint: 'text-red-400',
        spam: 'text-gray-400',
        collab: 'text-green-400',
        troll: 'text-red-600',
        other: 'text-gray-400'
    };

    const sentimentEmoji: any = {
        question: '❓',
        compliment: '❤️',
        complaint: '😤',
        spam: '🚫',
        collab: '🤝',
        troll: '👹',
        other: '💬'
    };

    return (
        <div className="p-8 text-white max-w-3xl">
            <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <Bot className="text-purple-400" size={24} />
                Test AI Agent
            </h1>
            <p className="text-gray-400 text-sm mb-8">
                Type any comment and see how the AI agent would handle it
            </p>

            {/* Input */}
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
                <div className="mb-4">
                    <label className="text-sm text-gray-400 mb-1 block">Username</label>
                    <input
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        placeholder="test_user"
                    />
                </div>
                <div className="mb-4">
                    <label className="text-sm text-gray-400 mb-1 block">Comment</label>
                    <textarea
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500 resize-none"
                        rows={3}
                        value={comment}
                        onChange={e => setComment(e.target.value)}
                        placeholder="Where can I buy this product?"
                        onKeyDown={e => {
                            if (e.key === 'Enter' && e.metaKey) handleTest();
                        }}
                    />
                </div>
                <button
                    onClick={handleTest}
                    disabled={loading || !comment.trim()}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors"
                >
                    <Send size={16} />
                    {loading ? 'Processing...' : 'Send to Agent'}
                </button>
            </div>

            {/* Loading */}
            {loading && (
                <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                        <p className="text-gray-400 text-sm">Agent is processing comment...</p>
                    </div>
                    <div className="mt-4 space-y-2 text-xs text-gray-600">
                        <p>→ Checking post mode...</p>
                        <p>→ Running rule engine...</p>
                        <p>→ Detecting sentiment...</p>
                        <p>→ Searching similar replies...</p>
                        <p>→ Generating reply with Ollama...</p>
                    </div>
                </div>
            )}

            {/* Result */}
            {result && (
                <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 space-y-4">
                    <h2 className="font-semibold text-lg">Agent Result</h2>

                    {/* Pipeline badges */}
                    <div className="flex flex-wrap gap-2">
                        <span className={`text-xs px-3 py-1 rounded-full bg-gray-800 ${sentimentColors[result.sentiment] || 'text-gray-400'}`}>
                            {sentimentEmoji[result.sentiment]} {result.sentiment}
                        </span>
                        <span className={`text-xs px-3 py-1 rounded-full ${result.rule_matched ? 'bg-yellow-900 text-yellow-300' : 'bg-gray-800 text-gray-400'}`}>
                            {result.rule_matched ? '⚡ Rule matched' : '🤖 Went to AI'}
                        </span>
                        <span className="text-xs px-3 py-1 rounded-full bg-gray-800 text-gray-400">
                            📋 {result.post_mode} mode
                        </span>
                        <span className={`text-xs px-3 py-1 rounded-full ${result.action_taken === 'ai_replied' ? 'bg-purple-900 text-purple-300' :
                                result.action_taken === 'rule_reply' ? 'bg-yellow-900 text-yellow-300' :
                                    result.action_taken === 'auto_hidden' ? 'bg-red-900 text-red-300' :
                                        'bg-gray-800 text-gray-400'
                            }`}>
                            ✅ {result.action_taken}
                        </span>
                    </div>

                    {/* Comment */}
                    <div className="bg-gray-800 rounded-lg px-4 py-3">
                        <p className="text-xs text-gray-500 mb-1">Comment from @{username}</p>
                        <p className="text-gray-300 text-sm">"{result.comment}"</p>
                    </div>

                    {/* Reply */}
                    {result.generated_reply && (
                        <div className="bg-purple-900/20 border border-purple-800/30 rounded-lg px-4 py-3">
                            <p className="text-xs text-purple-400 mb-1">AI Generated Reply</p>
                            <p className="text-white text-sm">{result.generated_reply}</p>
                        </div>
                    )}

                    {/* No reply cases */}
                    {!result.generated_reply && result.action_taken === 'auto_hidden' && (
                        <div className="bg-red-900/20 border border-red-800/30 rounded-lg px-4 py-3">
                            <p className="text-red-400 text-sm">🚫 Comment was auto-hidden (spam/troll detected)</p>
                        </div>
                    )}

                    {!result.generated_reply && result.action_taken === 'flagged_collab' && (
                        <div className="bg-green-900/20 border border-green-800/30 rounded-lg px-4 py-3">
                            <p className="text-green-400 text-sm">🤝 Flagged as collaboration request — check Collabs page</p>
                        </div>
                    )}
                </div>
            )}

            {/* Quick test examples */}
            <div className="mt-8">
                <p className="text-sm text-gray-500 mb-3">Quick test examples:</p>
                <div className="flex flex-wrap gap-2">
                    {[
                        "Where can I buy this?",
                        "You look so beautiful! ❤️",
                        "Hi I'm from a brand, would love to collab!",
                        "Buy followers cheap click here!!!",
                        "What moisturizer do you use for dry skin?",
                        "This is fake and scam!"
                    ].map((example) => (
                        <button
                            key={example}
                            onClick={() => setComment(example)}
                            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg transition-colors"
                        >
                            {example}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}