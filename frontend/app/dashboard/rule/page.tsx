'use client';
import { useEffect, useState } from 'react';
import { getRules, createRule } from '../../../lib/api';
import { Zap, Plus } from 'lucide-react';

const INFLUENCER_ID = 'c6eb89e9-152a-46b0-a0e2-bbc52ff31995';

export default function RulesPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    keywords: '',
    action: 'reply',
    template: '',
    priority: 0
  });

  useEffect(() => {
    loadRules();
  }, []);

  async function loadRules() {
    const data = await getRules(INFLUENCER_ID);
    setRules(data.rules || []);
    setLoading(false);
  }

  async function handleCreate() {
    if (!form.keywords || !form.template) return;
    setCreating(true);
    await createRule({
      influencer_id: INFLUENCER_ID,
      keywords: form.keywords.split(',').map(k => k.trim()),
      action: form.action,
      template: form.template,
      priority: form.priority
    });
    setForm({ keywords: '', action: 'reply', template: '', priority: 0 });
    await loadRules();
    setCreating(false);
  }

  return (
    <div className="p-8 text-white">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Zap className="text-yellow-400" size={24} />
        Automation Rules
      </h1>

      {/* Create Rule Form */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-8">
        <h2 className="text-lg font-semibold mb-4">Create New Rule</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">
              Keywords (comma separated)
            </label>
            <input
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
              placeholder="product, link, buy, price"
              value={form.keywords}
              onChange={e => setForm({ ...form, keywords: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Action</label>
            <select
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
              value={form.action}
              onChange={e => setForm({ ...form, action: e.target.value })}
            >
              <option value="reply">Reply with template</option>
              <option value="dm">Send DM</option>
              <option value="hide">Hide comment</option>
              <option value="flag">Flag for review</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="text-sm text-gray-400 mb-1 block">
              Reply Template
            </label>
            <input
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
              placeholder="Hey! Check my bio link for the product 🛍️"
              value={form.template}
              onChange={e => setForm({ ...form, template: e.target.value })}
            />
          </div>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating}
          className="mt-4 flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          {creating ? 'Creating...' : 'Create Rule'}
        </button>
      </div>

      {/* Rules List */}
      <div className="space-y-4">
        {loading && <p className="text-gray-500">Loading rules...</p>}
        {!loading && rules.length === 0 && (
          <p className="text-gray-500">No rules yet. Create one above.</p>
        )}
        {rules.map((rule) => (
          <div key={rule.id} className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs bg-yellow-900 text-yellow-300 px-2 py-1 rounded-full">
                    ⚡ {rule.action}
                  </span>
                  <span className="text-xs text-gray-500">
                    Priority: {rule.priority}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mb-3">
                  {rule.keywords?.map((kw: string) => (
                    <span key={kw} className="text-xs bg-gray-800 text-purple-300 px-2 py-1 rounded-full">
                      {kw}
                    </span>
                  ))}
                </div>
                {rule.template && (
                  <p className="text-sm text-gray-300">
                    ↳ &quot;{rule.template}&quot;
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
