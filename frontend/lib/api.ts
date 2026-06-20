const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getOverview(influencerId: string) {
    const res = await fetch(`${API_URL}/analytics/${influencerId}/overview`);
    return res.json();
}

export async function getRecentReplies(influencerId: string) {
    const res = await fetch(`${API_URL}/analytics/${influencerId}/recent-replies`);
    return res.json();
}

export async function getSentimentBreakdown(influencerId: string) {
    const res = await fetch(`${API_URL}/analytics/${influencerId}/sentiment-breakdown`);
    return res.json();
}

export async function getRules(influencerId: string) {
    const res = await fetch(`${API_URL}/rules/${influencerId}`);
    return res.json();
}

export async function createRule(data: object) {
    const res = await fetch(`${API_URL}/rules/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

export async function testAgent(data: object) {
    const res = await fetch(`${API_URL}/dashboard/test-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

export async function getPendingApprovals(influencerId: string) {
    const res = await fetch(`${API_URL}/analytics/${influencerId}/pending-approvals`);
    return res.json();
}

export async function approveReply(influencerId: string, data: object) {
    const res = await fetch(`${API_URL}/analytics/${influencerId}/approve-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}