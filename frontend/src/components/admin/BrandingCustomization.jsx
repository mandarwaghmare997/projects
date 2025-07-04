import React, { useState, useEffect } from 'react';

const BrandingCustomization = () => {
  const [brandSettings, setBrandSettings] = useState({
    primary_color: '#3B82F6',
    secondary_color: '#1E40AF',
    accent_color: '#10B981',
    background_color: '#FFFFFF',
    text_color: '#1F2937',
    font_family: 'Inter, sans-serif',
    logo_url: null,
    favicon_url: null,
    custom_css: '',
    theme_mode: 'light',
    show_powered_by: true,
    custom_domain: '',
    email_template_header: ''
  });

  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');
  const [organizationInfo, setOrganizationInfo] = useState(null);
  const [activeTab, setActiveTab] = useState('colors');

  useEffect(() => {
    fetchBrandSettings();
  }, []);

  const fetchBrandSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/branding/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBrandSettings(data.branding_settings);
        setOrganizationInfo(data);
      }
    } catch (error) {
      console.error('Error fetching brand settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateBrandSettings = async (settings) => {
    try {
      const response = await fetch('/api/branding/settings', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        setBrandSettings(prev => ({ ...prev, ...settings }));
        alert('Brand settings updated successfully');
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error updating brand settings:', error);
      alert('Failed to update brand settings');
    }
  };

  const uploadAsset = async (file, type) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`/api/branding/upload/${type}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        const urlKey = type === 'logo' ? 'logo_url' : 'favicon_url';
        setBrandSettings(prev => ({ ...prev, [urlKey]: data[urlKey] }));
        alert(`${type.charAt(0).toUpperCase() + type.slice(1)} uploaded successfully`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error(`Error uploading ${type}:`, error);
      alert(`Failed to upload ${type}`);
    }
  };

  const generatePreview = async () => {
    try {
      const response = await fetch('/api/branding/white-label/preview', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ branding_settings: brandSettings })
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewHtml(data.preview_html);
        setPreviewMode(true);
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      alert('Failed to generate preview');
    }
  };

  const validateDomain = async (domain) => {
    try {
      const response = await fetch('/api/branding/domain/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ domain })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Domain validation: ${data.validation_results.is_valid ? 'Valid' : 'Invalid'}`);
        return data.validation_results;
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
        return null;
      }
    } catch (error) {
      console.error('Error validating domain:', error);
      alert('Failed to validate domain');
      return null;
    }
  };

  const ColorPicker = ({ label, value, onChange, description }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="flex items-center space-x-3">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-12 h-12 border border-gray-300 rounded-lg cursor-pointer"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="#000000"
        />
      </div>
      {description && <p className="text-xs text-gray-500">{description}</p>}
    </div>
  );

  const FileUpload = ({ label, accept, onUpload, currentUrl, type }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="flex items-center space-x-4">
        <input
          type="file"
          accept={accept}
          onChange={(e) => {
            const file = e.target.files[0];
            if (file) onUpload(file, type);
          }}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {currentUrl && (
          <div className="flex items-center space-x-2">
            <img src={currentUrl} alt="Current" className="w-8 h-8 object-contain" />
            <span className="text-xs text-green-600">✓ Uploaded</span>
          </div>
        )}
      </div>
    </div>
  );

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 font-medium text-sm rounded-lg transition-colors ${
        isActive
          ? 'bg-blue-600 text-white'
          : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
      }`}
    >
      {label}
    </button>
  );

  const ColorsTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ColorPicker
          label="Primary Color"
          value={brandSettings.primary_color}
          onChange={(color) => setBrandSettings(prev => ({ ...prev, primary_color: color }))}
          description="Main brand color used for buttons, links, and highlights"
        />
        <ColorPicker
          label="Secondary Color"
          value={brandSettings.secondary_color}
          onChange={(color) => setBrandSettings(prev => ({ ...prev, secondary_color: color }))}
          description="Secondary color for hover states and accents"
        />
        <ColorPicker
          label="Accent Color"
          value={brandSettings.accent_color}
          onChange={(color) => setBrandSettings(prev => ({ ...prev, accent_color: color }))}
          description="Accent color for success states and progress indicators"
        />
        <ColorPicker
          label="Background Color"
          value={brandSettings.background_color}
          onChange={(color) => setBrandSettings(prev => ({ ...prev, background_color: color }))}
          description="Main background color for the application"
        />
        <ColorPicker
          label="Text Color"
          value={brandSettings.text_color}
          onChange={(color) => setBrandSettings(prev => ({ ...prev, text_color: color }))}
          description="Primary text color for content"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Font Family</label>
        <select
          value={brandSettings.font_family}
          onChange={(e) => setBrandSettings(prev => ({ ...prev, font_family: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="Inter, sans-serif">Inter (Default)</option>
          <option value="Roboto, sans-serif">Roboto</option>
          <option value="Open Sans, sans-serif">Open Sans</option>
          <option value="Lato, sans-serif">Lato</option>
          <option value="Montserrat, sans-serif">Montserrat</option>
          <option value="Poppins, sans-serif">Poppins</option>
          <option value="Source Sans Pro, sans-serif">Source Sans Pro</option>
          <option value="Arial, sans-serif">Arial</option>
          <option value="Helvetica, sans-serif">Helvetica</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Theme Mode</label>
        <div className="flex space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="light"
              checked={brandSettings.theme_mode === 'light'}
              onChange={(e) => setBrandSettings(prev => ({ ...prev, theme_mode: e.target.value }))}
              className="mr-2"
            />
            Light Mode
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="dark"
              checked={brandSettings.theme_mode === 'dark'}
              onChange={(e) => setBrandSettings(prev => ({ ...prev, theme_mode: e.target.value }))}
              className="mr-2"
            />
            Dark Mode
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="auto"
              checked={brandSettings.theme_mode === 'auto'}
              onChange={(e) => setBrandSettings(prev => ({ ...prev, theme_mode: e.target.value }))}
              className="mr-2"
            />
            Auto (System)
          </label>
        </div>
      </div>
    </div>
  );

  const AssetsTab = () => (
    <div className="space-y-6">
      <FileUpload
        label="Organization Logo"
        accept=".png,.jpg,.jpeg,.svg"
        onUpload={uploadAsset}
        currentUrl={brandSettings.logo_url}
        type="logo"
      />
      
      <FileUpload
        label="Favicon"
        accept=".png,.ico"
        onUpload={uploadAsset}
        currentUrl={brandSettings.favicon_url}
        type="favicon"
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Email Template Header</label>
        <input
          type="text"
          value={brandSettings.email_template_header || ''}
          onChange={(e) => setBrandSettings(prev => ({ ...prev, email_template_header: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Custom header text for email templates"
        />
      </div>

      {/* Asset Preview */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-4">Asset Preview</h4>
        <div className="flex items-center space-x-6">
          {brandSettings.logo_url && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Logo</p>
              <img src={brandSettings.logo_url} alt="Logo" className="h-12 object-contain" />
            </div>
          )}
          {brandSettings.favicon_url && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Favicon</p>
              <img src={brandSettings.favicon_url} alt="Favicon" className="w-8 h-8 object-contain" />
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const AdvancedTab = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Custom CSS</label>
        <textarea
          value={brandSettings.custom_css}
          onChange={(e) => setBrandSettings(prev => ({ ...prev, custom_css: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          rows="10"
          placeholder="/* Add your custom CSS here */
.custom-button {
  background-color: #your-color;
  border-radius: 8px;
}"
        />
        <p className="text-xs text-gray-500 mt-1">
          Add custom CSS to further customize the appearance of your platform
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Custom Domain</label>
        <div className="flex space-x-3">
          <input
            type="text"
            value={brandSettings.custom_domain || ''}
            onChange={(e) => setBrandSettings(prev => ({ ...prev, custom_domain: e.target.value }))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="learn.yourcompany.com"
          />
          <button
            onClick={() => validateDomain(brandSettings.custom_domain)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            disabled={!brandSettings.custom_domain}
          >
            Validate
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {organizationInfo?.white_labeling_enabled 
            ? "Configure a custom domain for your learning platform"
            : "Custom domain requires Enterprise subscription"
          }
        </p>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="show_powered_by"
          checked={brandSettings.show_powered_by}
          onChange={(e) => setBrandSettings(prev => ({ ...prev, show_powered_by: e.target.checked }))}
          className="mr-3"
          disabled={!organizationInfo?.white_labeling_enabled}
        />
        <label htmlFor="show_powered_by" className="text-sm text-gray-700">
          Show "Powered by Qryti Learn" footer
        </label>
        {!organizationInfo?.white_labeling_enabled && (
          <span className="ml-2 text-xs text-gray-500">(Enterprise feature)</span>
        )}
      </div>
    </div>
  );

  const PreviewModal = () => {
    if (!previewMode) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900">White-label Preview</h3>
            <button
              onClick={() => setPreviewMode(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <div className="h-[calc(90vh-80px)] overflow-auto">
            <iframe
              srcDoc={previewHtml}
              className="w-full h-full border-0"
              title="White-label Preview"
            />
          </div>
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
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Branding & Customization</h2>
          <p className="text-gray-600">Customize the look and feel of your learning platform</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={generatePreview}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Preview Changes
          </button>
          <button
            onClick={() => updateBrandSettings(brandSettings)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>

      {/* Subscription Notice */}
      {organizationInfo && (
        <div className={`p-4 rounded-lg ${
          organizationInfo.white_labeling_enabled 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-yellow-50 border border-yellow-200'
        }`}>
          <div className="flex items-center">
            <span className={`text-sm font-medium ${
              organizationInfo.white_labeling_enabled ? 'text-green-800' : 'text-yellow-800'
            }`}>
              {organizationInfo.white_labeling_enabled 
                ? `✓ Enterprise features enabled (${organizationInfo.subscription_tier})`
                : `⚠️ Some features require Enterprise subscription (Current: ${organizationInfo.subscription_tier})`
              }
            </span>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex flex-wrap gap-2">
          <TabButton
            id="colors"
            label="Colors & Theme"
            isActive={activeTab === 'colors'}
            onClick={setActiveTab}
          />
          <TabButton
            id="assets"
            label="Assets & Media"
            isActive={activeTab === 'assets'}
            onClick={setActiveTab}
          />
          <TabButton
            id="advanced"
            label="Advanced Settings"
            isActive={activeTab === 'advanced'}
            onClick={setActiveTab}
          />
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {activeTab === 'colors' && <ColorsTab />}
        {activeTab === 'assets' && <AssetsTab />}
        {activeTab === 'advanced' && <AdvancedTab />}
      </div>

      {/* Live Preview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Preview</h3>
        <div 
          className="border rounded-lg p-6 min-h-[200px]"
          style={{
            backgroundColor: brandSettings.background_color,
            color: brandSettings.text_color,
            fontFamily: brandSettings.font_family
          }}
        >
          <div 
            className="p-4 rounded-lg mb-4"
            style={{ backgroundColor: brandSettings.primary_color, color: 'white' }}
          >
            <h4 className="text-lg font-semibold">
              {organizationInfo?.organization_name || 'Your Organization'} Learning Platform
            </h4>
          </div>
          
          <div className="space-y-4">
            <p>This is how your platform will look with the current branding settings.</p>
            
            <button
              className="px-4 py-2 rounded-lg text-white font-medium"
              style={{ backgroundColor: brandSettings.primary_color }}
            >
              Primary Button
            </button>
            
            <button
              className="px-4 py-2 rounded-lg text-white font-medium ml-3"
              style={{ backgroundColor: brandSettings.accent_color }}
            >
              Accent Button
            </button>
            
            <div className="mt-4">
              <a href="#" style={{ color: brandSettings.primary_color }}>
                Sample link with primary color
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      <PreviewModal />
    </div>
  );
};

export default BrandingCustomization;

