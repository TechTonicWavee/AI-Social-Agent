'use client';
import { useEffect, useState } from 'react';
import { Users } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function CollabPage() {
    const [collabs, setCollabs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const res = await fetch(
                `${API_URL}/analytics/${INFLUENCER_ID}/collab-requests`
            );
            const data = await res.json();
            setCollabs(data.collab_requests || []);
            setLoading(false);
        }
        load();
    }, []);

    return (
        <div className="p-8 text-white">
            <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <Users className="text-green-400" size={24} />
                Collaboration Requests
            </h1>
            <p className="text-gray-400 text-sm mb-6">
                Brand deals and collaboration requests detected from comments
            </p>

            {loading && <p className="text-gray-500 animate-pulse">Loading...</p>}

            {!loading && collabs.length === 0 && (
                <div className="bg-gray-900 rounded-xl p-8 border border-gray-800 text-center">
                    <Users size={32} className="text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-400">No collaboration requests yet</p>
                    <p className="text-gray-600 text-sm mt-1">
                        When brands comment asking to collaborate, they'll appear here
                    </p>
                </div>
            )}

            <div className="space-y-4">
                {collabs.map((collab) => (
                    <div
                        key={collab.id}
                        className="bg-gray-900 rounded-xl p-6 border border-gray-800"
                    >
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-green-400 font-medium">
                                        @{collab.username}
                                    </span>
                                    <span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded-full">
                                        🤝 Collab Request
                                    </span>
                                </div>
                                <p className="text-gray-300 text-sm mb-3">"{collab.text}"</p>
                                <p className="text-gray-500 text-xs">
                                    {new Date(collab.created_at).toLocaleDateString()}
                                </p>
                            </div>
                            <div className="flex gap-2">
                                <button className="bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1.5 rounded-lg transition-colors">
                                    Interested
                                </button>
                                <button className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1.5 rounded-lg transition-colors">
                                    Pass
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}