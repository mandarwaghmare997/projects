import React, { useState, useEffect } from 'react';

const OrganizationManagement = () => {
  const [organizations, setOrganizations] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [usageData, setUsageData] = useState(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/enterprise/organizations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setOrganizations(data.organizations);
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageData = async (orgId) => {
    try {
      const response = await fetch('/api/enterprise/subscription/usage', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsageData(data);
      }
    } catch (error) {
      console.error('Error fetching usage data:', error);
    }
  };

  const createOrganization = async (orgData) => {
    try {
      const response = await fetch('/api/enterprise/organizations', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orgData)
      });

      if (response.ok) {
        await fetchOrganizations();
        setShowCreateModal(false);
        alert('Organization created successfully');
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error creating organization:', error);
      alert('Failed to create organization');
    }
  };

  const updateOrganization = async (orgId, updates) => {
    try {
      const response = await fetch(`/api/enterprise/organizations/${orgId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        await fetchOrganizations();
        alert('Organization updated successfully');
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error updating organization:', error);
      alert('Failed to update organization');
    }
  };

  const requestUpgrade = async (newTier) => {
    try {
      const response = await fetch('/api/enterprise/subscription/upgrade', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ new_tier: newTier })
      });

      if (response.ok) {
        setShowUpgradeModal(false);
        alert('Upgrade request submitted successfully');
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error requesting upgrade:', error);
      alert('Failed to submit upgrade request');
    }
  };

  const CreateOrganizationModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      domain: '',
      subscription_tier: 'basic',
      max_users: 100,
      is_active: true
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      createOrganization(formData);
    };

    if (!showCreateModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Organization</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Domain
              </label>
              <input
                type="text"
                required
                value={formData.domain}
                onChange={(e) => setFormData({...formData, domain: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="company.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subscription Tier
              </label>
              <select
                value={formData.subscription_tier}
                onChange={(e) => setFormData({...formData, subscription_tier: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="basic">Basic</option>
                <option value="professional">Professional</option>
                <option value="enterprise">Enterprise</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Users
              </label>
              <input
                type="number"
                value={formData.max_users}
                onChange={(e) => setFormData({...formData, max_users: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                className="mr-2"
              />
              <label htmlFor="is_active" className="text-sm text-gray-700">
                Active Organization
              </label>
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Organization
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const UpgradeModal = () => {
    const [selectedTier, setSelectedTier] = useState('professional');

    const tiers = [
      { id: 'basic', name: 'Basic', price: '$29/month', features: ['Up to 100 users', 'Basic analytics', 'Email support'] },
      { id: 'professional', name: 'Professional', price: '$99/month', features: ['Up to 500 users', 'Advanced analytics', 'Priority support', 'Custom branding'] },
      { id: 'enterprise', name: 'Enterprise', price: '$299/month', features: ['Unlimited users', 'Full analytics suite', 'Dedicated support', 'White-labeling', 'SSO integration'] },
      { id: 'custom', name: 'Custom', price: 'Contact us', features: ['Custom user limits', 'Tailored features', 'On-premise deployment', 'Custom integrations'] }
    ];

    if (!showUpgradeModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upgrade Subscription</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {tiers.map((tier) => (
              <div
                key={tier.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedTier === tier.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedTier(tier.id)}
              >
                <div className="text-center">
                  <h4 className="font-semibold text-gray-900">{tier.name}</h4>
                  <p className="text-lg font-bold text-blue-600 my-2">{tier.price}</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {tier.features.map((feature, index) => (
                      <li key={index}>• {feature}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowUpgradeModal(false)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={() => requestUpgrade(selectedTier)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Request Upgrade
            </button>
          </div>
        </div>
      </div>
    );
  };

  const UsageOverview = () => {
    if (!usageData) return null;

    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Subscription Usage</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">User Usage</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Current Users:</span>
                <span className="font-semibold">{usageData.usage.users.current}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Active Users:</span>
                <span className="font-semibold">{usageData.usage.users.active}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>User Limit:</span>
                <span className="font-semibold">{usageData.usage.users.limit}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    usageData.usage.users.usage_percent > 80 ? 'bg-red-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${Math.min(usageData.usage.users.usage_percent, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">
                {usageData.usage.users.usage_percent.toFixed(1)}% of limit used
              </p>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Monthly Activity</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>New Enrollments:</span>
                <span className="font-semibold">{usageData.usage.monthly_activity.enrollments}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Subscription</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Current Tier:</span>
                <span className="font-semibold capitalize">{usageData.organization.subscription_tier}</span>
              </div>
              {usageData.limits.approaching_user_limit && (
                <div className="p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                  ⚠️ Approaching user limit
                </div>
              )}
              {usageData.limits.at_user_limit && (
                <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
                  🚫 User limit reached
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setShowUpgradeModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Upgrade Subscription
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Organization Management</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => fetchUsageData()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            View Usage
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Organization
          </button>
        </div>
      </div>

      {/* Usage Overview */}
      <UsageOverview />

      {/* Organizations List */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Organizations</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Domain</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {organizations.map((org) => (
                <tr key={org.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-gray-900">{org.name}</div>
                      <div className="text-sm text-gray-500">ID: {org.id}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{org.domain}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 capitalize">
                      {org.subscription_tier}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    <div>{org.statistics.active_users} / {org.statistics.total_users}</div>
                    <div className="text-xs text-gray-500">
                      {org.statistics.activation_rate}% active
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      org.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {org.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setSelectedOrg(org)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Details
                      </button>
                      <button
                        onClick={() => {
                          const newName = prompt('Enter new organization name:', org.name);
                          if (newName && newName !== org.name) {
                            updateOrganization(org.id, { name: newName });
                          }
                        }}
                        className="text-green-600 hover:text-green-800 text-sm font-medium"
                      >
                        Edit
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Organization Details Modal */}
      {selectedOrg && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Organization Details</h3>
              <button
                onClick={() => setSelectedOrg(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <p className="text-sm text-gray-900">{selectedOrg.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Domain</label>
                  <p className="text-sm text-gray-900">{selectedOrg.domain}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subscription Tier</label>
                  <p className="text-sm text-gray-900 capitalize">{selectedOrg.subscription_tier}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Created</label>
                  <p className="text-sm text-gray-900">
                    {selectedOrg.created_at ? new Date(selectedOrg.created_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Statistics</label>
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{selectedOrg.statistics.total_users}</p>
                    <p className="text-sm text-gray-600">Total Users</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{selectedOrg.statistics.active_users}</p>
                    <p className="text-sm text-gray-600">Active Users</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{selectedOrg.statistics.activation_rate}%</p>
                    <p className="text-sm text-gray-600">Activation Rate</p>
                  </div>
                </div>
              </div>

              {selectedOrg.settings && Object.keys(selectedOrg.settings).length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Settings</label>
                  <pre className="text-xs bg-gray-100 p-3 rounded-lg overflow-x-auto">
                    {JSON.stringify(selectedOrg.settings, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <CreateOrganizationModal />
      <UpgradeModal />
    </div>
  );
};

export default OrganizationManagement;

