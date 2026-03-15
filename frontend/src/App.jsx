import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [step, setStep] = useState(1); // 1: Upload, 2: Results
  const [extractedData, setExtractedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleProcess = async (documentType) => {
    if (!file) return;
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType); // User tells the backend what it is

    try {
      const response = await fetch("http://localhost:8000/api/extract", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setExtractedData(data.data);
      setStep(2);
    } catch (error) {
      alert("Processing failed. Ensure the FastAPI backend is running.");
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans text-slate-800">
      <div className="max-w-xl w-full bg-white rounded-3xl shadow-xl border border-slate-100 p-8">
        
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-500 to-blue-600 tracking-tight">
            EvoDoc Analyzer
          </h1>
          <p className="text-slate-500 text-sm mt-1">Smart Medical Document Structuring</p>
        </div>

        {/* STEP 1: UPLOAD & SELECT */}
        {step === 1 && (
          <div className="space-y-6 animate-fade-in">
            <div className="border-2 border-dashed border-slate-300 rounded-2xl p-10 text-center hover:bg-slate-50 transition-all duration-300">
              <input 
                type="file" 
                accept="image/*,.pdf"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full text-slate-600 file:mr-4 file:py-2.5 file:px-5 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
              />
            </div>
            
            <div className="pt-4 border-t border-slate-100">
                <p className="text-center text-sm font-semibold text-slate-500 mb-4 uppercase tracking-wider">How should we process this?</p>
                <div className="grid grid-cols-2 gap-4">
                <button 
                    onClick={() => handleProcess("DOCUMENT")}
                    disabled={!file || isLoading}
                    className="bg-blue-600 text-white font-bold py-3.5 px-4 rounded-xl shadow-md shadow-blue-200 hover:bg-blue-700 disabled:opacity-50 transition-all"
                >
                    {isLoading ? 'Processing...' : 'Read Text Document'}
                </button>
                <button 
                    onClick={() => handleProcess("SCAN")}
                    disabled={!file || isLoading}
                    className="bg-white border-2 border-slate-200 text-slate-600 font-bold py-3.5 px-4 rounded-xl hover:bg-slate-50 disabled:opacity-50 transition-all"
                >
                    Save as Medical Scan
                </button>
                </div>
            </div>
          </div>
        )}

        {/* STEP 2: RESULTS */}
        {step === 2 && extractedData && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-end border-b border-slate-200 pb-4">
              <h2 className="text-xl font-bold text-slate-800">Structured Extraction</h2>
              <button onClick={() => {setStep(1); setFile(null); setExtractedData(null);}} className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition">Upload Another</button>
            </div>

            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 space-y-5">
              {Object.entries(extractedData).map(([key, value]) => (
                <div key={key}>
                  <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-1">{key.replace(/_/g, ' ')}</h3>
                  {Array.isArray(value) ? (
                    <div className="flex flex-wrap gap-2 mt-1.5">
                      {value.map((tag, i) => (
                        <span key={i} className="bg-white border border-slate-200 text-slate-700 shadow-sm text-xs font-semibold px-3 py-1 rounded-md">{tag}</span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-800 font-medium text-sm leading-relaxed">{value}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;