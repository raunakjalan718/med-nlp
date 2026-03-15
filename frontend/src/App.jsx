import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [step, setStep] = useState(1);
  const [extractedData, setExtractedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleProcess = async (documentType) => {
    if (!file) return;
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);

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
    <div className="min-h-screen bg-slate-950 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black flex items-center justify-center p-6 font-sans text-slate-200">
      
      <div className="max-w-3xl w-full bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-[0_0_50px_rgba(6,182,212,0.1)] p-8 relative overflow-hidden">
        
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-40 bg-cyan-600/10 blur-[120px] -z-10 rounded-full pointer-events-none"></div>

        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 tracking-tight drop-shadow-sm">
            EvoDoc NLP
          </h1>
          <p className="text-slate-400 text-sm mt-2 font-medium tracking-wide">AI-Powered Document Structuring</p>
        </div>

        {/* STEP 1: UPLOAD */}
        {step === 1 && (
          <div className="space-y-8 animate-fade-in">
            <div className="relative group cursor-pointer">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative border-2 border-dashed border-white/20 rounded-2xl p-12 text-center bg-slate-900/50 hover:bg-slate-900/80 transition-all duration-300">
                <input 
                  type="file" 
                  accept="image/*,.pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="w-full text-slate-300 file:mr-4 file:py-2.5 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20 cursor-pointer outline-none"
                />
              </div>
            </div>
            
            <div className="pt-6 border-t border-white/10">
                <div className="flex justify-center">
                    <button 
                        onClick={() => handleProcess("DOCUMENT")}
                        disabled={!file || isLoading}
                        className="w-full max-w-md bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-4 px-4 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-all duration-300 tracking-wide"
                    >
                        {isLoading ? 'Running NLP Engine...' : 'Extract & Structure Data'}
                    </button>
                </div>
            </div>
          </div>
        )}

        {/* STEP 2: RESULTS (THE TABLE STRUCTURE) */}
        {step === 2 && extractedData && (
          <div className="space-y-8 animate-fade-in relative z-10">
            <div className="flex justify-between items-end border-b border-white/10 pb-4">
              <h2 className="text-2xl font-bold text-white tracking-wide">Clinical Extraction Report</h2>
              <button onClick={() => {setStep(1); setFile(null); setExtractedData(null);}} className="text-sm font-semibold text-cyan-400 hover:text-cyan-300 transition">Upload New</button>
            </div>

            {/* Patient & Doctor Table */}
            <div className="bg-slate-900/60 border border-white/10 rounded-2xl overflow-hidden shadow-inner">
                <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-white/5 text-cyan-400/90 text-xs uppercase font-bold tracking-widest border-b border-white/10">
                        <tr>
                            <th className="px-6 py-4 w-1/3">Category</th>
                            <th className="px-6 py-4">Extracted Details</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        <tr className="hover:bg-white/5 transition">
                            <td className="px-6 py-4 font-semibold text-slate-400">Patient Name</td>
                            <td className="px-6 py-4 text-white font-medium">{extractedData.Patient_Name}</td>
                        </tr>
                        <tr className="hover:bg-white/5 transition">
                            <td className="px-6 py-4 font-semibold text-slate-400">Age / Sex</td>
                            <td className="px-6 py-4 text-white font-medium">{extractedData.Patient_Age_Sex}</td>
                        </tr>
                        <tr className="hover:bg-white/5 transition">
                            <td className="px-6 py-4 font-semibold text-slate-400">Attending Doctor(s)</td>
                            <td className="px-6 py-4 text-white font-medium">
                                {extractedData.Doctor_Details?.map((doc, i) => (
                                    <div key={i} className="mb-1 last:mb-0">{doc}</div>
                                ))}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* Medicines Table */}
            <div className="bg-slate-900/60 border border-white/10 rounded-2xl overflow-hidden shadow-inner">
                <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-white/5 text-cyan-400/90 text-xs uppercase font-bold tracking-widest border-b border-white/10">
                        <tr>
                            <th className="px-6 py-4">Prescribed Medications & Dosages</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {extractedData.Prescribed_Medicines?.map((med, i) => (
                            <tr key={i} className="hover:bg-white/5 transition">
                                <td className="px-6 py-4 flex items-center">
                                    <span className="h-2 w-2 rounded-full bg-cyan-500 mr-3 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                                    <span className="text-white font-medium text-[15px]">{med}</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default App;