import React from 'react';

const CertificateCard = ({ certificate, onDownload, onView, onVerify }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getCertificateIcon = (courseTitle) => {
    if (courseTitle.includes('Foundation')) return '🏅';
    if (courseTitle.includes('Practitioner')) return '🎖️';
    if (courseTitle.includes('Lead')) return '🏆';
    if (courseTitle.includes('Auditor')) return '👑';
    return '📜';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <span className="text-3xl mr-3">
              {getCertificateIcon(certificate.course?.title || '')}
            </span>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {certificate.course?.title || 'Course Certificate'}
              </h3>
              <p className="text-sm text-gray-500">
                Certificate ID: {certificate.certificate_id}
              </p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            certificate.is_valid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {certificate.is_valid ? 'Valid' : 'Revoked'}
          </div>
        </div>

        {/* Score */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Final Score</span>
            <span className={`px-2 py-1 rounded-full text-sm font-medium ${getScoreColor(certificate.final_score)}`}>
              {certificate.final_score}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                certificate.final_score >= 90 ? 'bg-green-500' :
                certificate.final_score >= 80 ? 'bg-blue-500' :
                certificate.final_score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${certificate.final_score}%` }}
            ></div>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Issued Date:</span>
            <span className="text-gray-900 font-medium">
              {formatDate(certificate.issued_at)}
            </span>
          </div>
          {certificate.expires_at && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Expires:</span>
              <span className="text-gray-900 font-medium">
                {formatDate(certificate.expires_at)}
              </span>
            </div>
          )}
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Level:</span>
            <span className="text-gray-900 font-medium">
              {certificate.course?.level ? `Level ${certificate.course.level}` : 'N/A'}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onView && onView(certificate)}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            View Certificate
          </button>
          <button
            onClick={() => onDownload && onDownload(certificate)}
            className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            Download PDF
          </button>
          <button
            onClick={() => onVerify && onVerify(certificate)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Verify
          </button>
        </div>

        {/* Verification URL */}
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <p className="text-xs text-gray-600 mb-1">Verification URL:</p>
          <p className="text-xs text-blue-600 break-all">
            {certificate.verification_url || `https://learn.qryti.com/verify/${certificate.certificate_id}`}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CertificateCard;

