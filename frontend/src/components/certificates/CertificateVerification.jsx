import React, { useState } from 'react';
import { apiService } from '../../services/api';

const CertificateVerification = () => {
  const [verificationCode, setVerificationCode] = useState('');
  const [certificateId, setCertificateId] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verificationMethod, setVerificationMethod] = useState('code'); // 'code' or 'id'

  const handleVerifyByCode = async (e) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      setError('Please enter a verification code');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/certificates/verify-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ verification_code: verificationCode.trim() })
      });

      const data = await response.json();
      
      if (response.ok && data.valid) {
        setVerificationResult({
          valid: true,
          certificate: data.certificate
        });
      } else {
        setVerificationResult({
          valid: false,
          message: data.message || 'Certificate not found or invalid'
        });
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('Failed to verify certificate. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyById = async (e) => {
    e.preventDefault();
    if (!certificateId.trim()) {
      setError('Please enter a certificate ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/certificates/verify/${certificateId.trim()}`, {
        method: 'GET'
      });

      const data = await response.json();
      
      if (response.ok && data.valid) {
        setVerificationResult({
          valid: true,
          certificate: data.certificate
        });
      } else {
        setVerificationResult({
          valid: false,
          message: data.message || 'Certificate not found or invalid'
        });
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('Failed to verify certificate. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const resetForm = () => {
    setVerificationCode('');
    setCertificateId('');
    setVerificationResult(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="text-4xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Certificate Verification
          </h2>
          <p className="text-gray-600">
            Verify the authenticity of Qryti Learn certificates
          </p>
        </div>

        {/* Verification Method Selector */}
        <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => {
              setVerificationMethod('code');
              resetForm();
            }}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              verificationMethod === 'code'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Verification Code
          </button>
          <button
            onClick={() => {
              setVerificationMethod('id');
              resetForm();
            }}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              verificationMethod === 'id'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Certificate ID
          </button>
        </div>

        {/* Verification Form */}
        {verificationMethod === 'code' ? (
          <form onSubmit={handleVerifyByCode} className="space-y-4">
            <div>
              <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700 mb-2">
                Verification Code
              </label>
              <input
                type="text"
                id="verificationCode"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.toUpperCase())}
                placeholder="Enter 8-character verification code"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                maxLength={8}
              />
              <p className="text-xs text-gray-500 mt-1">
                Example: ABC12345
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Verifying...' : 'Verify Certificate'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyById} className="space-y-4">
            <div>
              <label htmlFor="certificateId" className="block text-sm font-medium text-gray-700 mb-2">
                Certificate ID
              </label>
              <input
                type="text"
                id="certificateId"
                value={certificateId}
                onChange={(e) => setCertificateId(e.target.value)}
                placeholder="Enter full certificate ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Example: QRYTI-2025-A1B2C3D4
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Verifying...' : 'Verify Certificate'}
            </button>
          </form>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Verification Result */}
        {verificationResult && (
          <div className="mt-6">
            {verificationResult.valid ? (
              <div className="bg-green-50 border border-green-200 rounded-md p-6">
                <div className="flex items-center mb-4">
                  <svg className="w-6 h-6 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-lg font-semibold text-green-800">
                    Certificate Verified ✓
                  </h3>
                </div>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-green-700">Certificate Holder</p>
                      <p className="text-green-900">{verificationResult.certificate.user_name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-green-700">Course</p>
                      <p className="text-green-900">{verificationResult.certificate.course_title}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-green-700">Level</p>
                      <p className="text-green-900">{verificationResult.certificate.course_level}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-green-700">Final Score</p>
                      <p className="text-green-900">{verificationResult.certificate.final_score}%</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-green-700">Issue Date</p>
                      <p className="text-green-900">{formatDate(verificationResult.certificate.issued_at)}</p>
                    </div>
                    {verificationResult.certificate.expires_at && (
                      <div>
                        <p className="text-sm font-medium text-green-700">Expires</p>
                        <p className="text-green-900">{formatDate(verificationResult.certificate.expires_at)}</p>
                      </div>
                    )}
                  </div>
                  
                  {verificationResult.certificate.organization && (
                    <div>
                      <p className="text-sm font-medium text-green-700">Organization</p>
                      <p className="text-green-900">{verificationResult.certificate.organization}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-red-50 border border-red-200 rounded-md p-6">
                <div className="flex items-center mb-2">
                  <svg className="w-6 h-6 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-lg font-semibold text-red-800">
                    Certificate Not Valid ✗
                  </h3>
                </div>
                <p className="text-red-700">
                  {verificationResult.message || 'The certificate could not be verified. It may be invalid, expired, or revoked.'}
                </p>
              </div>
            )}
            
            <button
              onClick={resetForm}
              className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Verify Another Certificate
            </button>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h4 className="text-sm font-medium text-gray-900 mb-2">How to verify:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Use the verification code found on the certificate document</li>
            <li>• Or use the full certificate ID (QRYTI-YYYY-XXXXXXXX format)</li>
            <li>• Valid certificates will show holder details and course information</li>
            <li>• Contact support if you encounter any issues</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CertificateVerification;

