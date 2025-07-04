import React from 'react';

const CertificateModal = ({ certificate, onClose, onDownload }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    }).catch(() => {
      alert('Failed to copy to clipboard');
    });
  };

  const shareOnLinkedIn = () => {
    const url = encodeURIComponent(certificate.verification_url || `https://learn.qryti.com/verify/${certificate.certificate_id}`);
    const title = encodeURIComponent(`I've earned a certificate in ${certificate.course?.title || 'ISO/IEC 42001'} from Qryti Learn!`);
    const summary = encodeURIComponent(`Just completed ${certificate.course?.title || 'ISO/IEC 42001'} certification with a score of ${certificate.final_score}%. Verify at: ${url}`);
    
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${summary}`;
    window.open(linkedInUrl, '_blank', 'width=600,height=400');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Certificate Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Certificate Preview */}
        <div className="p-6">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-8 mb-6">
            <div className="text-center">
              <div className="text-4xl mb-4">🏆</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                CERTIFICATE OF COMPLETION
              </h1>
              <p className="text-gray-600 mb-4">This is to certify that</p>
              <h2 className="text-xl font-bold text-blue-600 mb-4">
                {certificate.user?.full_name || `${certificate.user?.first_name} ${certificate.user?.last_name}`}
              </h2>
              <p className="text-gray-600 mb-2">has successfully completed the course</p>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {certificate.course?.title || 'ISO/IEC 42001 Course'}
              </h3>
              <p className="text-gray-600 mb-4">
                with a final score of <span className="font-semibold text-green-600">{certificate.final_score}%</span>
              </p>
              <p className="text-sm text-gray-500">
                Completed on {formatDate(certificate.issued_at)}
              </p>
            </div>
          </div>

          {/* Certificate Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Certificate ID
                </label>
                <div className="flex items-center">
                  <input
                    type="text"
                    value={certificate.certificate_id}
                    readOnly
                    className="flex-1 bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(certificate.certificate_id)}
                    className="ml-2 p-2 text-gray-500 hover:text-gray-700 transition-colors"
                    title="Copy to clipboard"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Verification URL
                </label>
                <div className="flex items-center">
                  <input
                    type="text"
                    value={certificate.verification_url || `https://learn.qryti.com/verify/${certificate.certificate_id}`}
                    readOnly
                    className="flex-1 bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(certificate.verification_url || `https://learn.qryti.com/verify/${certificate.certificate_id}`)}
                    className="ml-2 p-2 text-gray-500 hover:text-gray-700 transition-colors"
                    title="Copy to clipboard"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Course Level
                </label>
                <input
                  type="text"
                  value={certificate.course?.level ? `Level ${certificate.course.level}` : 'N/A'}
                  readOnly
                  className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Final Score
                </label>
                <input
                  type="text"
                  value={`${certificate.final_score}%`}
                  readOnly
                  className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Issue Date
                </label>
                <input
                  type="text"
                  value={formatDate(certificate.issued_at)}
                  readOnly
                  className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                  certificate.is_valid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {certificate.is_valid ? 'Valid' : 'Revoked'}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onDownload(certificate)}
              className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF
            </button>

            <button
              onClick={shareOnLinkedIn}
              className="flex items-center bg-blue-700 text-white px-4 py-2 rounded-md hover:bg-blue-800 transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              Share on LinkedIn
            </button>

            <button
              onClick={() => window.open(certificate.verification_url || `https://learn.qryti.com/verify/${certificate.certificate_id}`, '_blank')}
              className="flex items-center border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Verify Online
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CertificateModal;

