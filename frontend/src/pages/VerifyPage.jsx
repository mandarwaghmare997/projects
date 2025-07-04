import React from 'react';
import CertificateVerification from '../components/certificates/CertificateVerification';

const VerifyPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                <img 
                  src="/src/assets/qryti-logo.png" 
                  alt="Qryti" 
                  className="h-8 w-auto"
                />
              </a>
            </div>
            <nav className="flex space-x-4">
              <a
                href="/"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Home
              </a>
              <a
                href="/auth"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </a>
            </nav>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Certificate Verification
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Verify the authenticity of certificates issued by Qryti Learn. 
            Enter a verification code or certificate ID to confirm validity.
          </p>
        </div>

        <CertificateVerification />

        {/* Additional Information */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              About Certificate Verification
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Why Verify Certificates?
                </h3>
                <ul className="text-gray-600 space-y-2">
                  <li>• Confirm authenticity and prevent fraud</li>
                  <li>• Validate professional qualifications</li>
                  <li>• Check certificate status and expiration</li>
                  <li>• Ensure compliance with industry standards</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Certificate Features
                </h3>
                <ul className="text-gray-600 space-y-2">
                  <li>• Unique verification codes</li>
                  <li>• Tamper-proof digital signatures</li>
                  <li>• Real-time verification status</li>
                  <li>• Detailed holder information</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Need help with certificate verification? 
            <a href="mailto:support@qryti.com" className="text-blue-600 hover:text-blue-800 ml-1">
              Contact our support team
            </a>
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <img 
              src="/src/assets/qryti-logo.png" 
              alt="Qryti" 
              className="h-6 w-auto filter brightness-0 invert"
            />
          </div>
          <p className="text-gray-400">
            &copy; 2025 Qryti.com. All rights reserved. | 
            <a href="/privacy" className="hover:text-white ml-1">Privacy Policy</a> | 
            <a href="/terms" className="hover:text-white ml-1">Terms of Service</a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default VerifyPage;

