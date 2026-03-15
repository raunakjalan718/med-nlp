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
    // Dark background with a subtle gradient mesh
    <div className="min-h-screen bg-slate-950 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black flex items-center justify-center p-6 font-sans text-slate-200">
      
      {/* The Glass Container */}
      <div className="max-w-2xl w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl shadow-[0_0_40px_rgba(30,58,138,0.15)] p-8 relative overflow-hidden">
        
        {/* Glow effect blob behind the glass */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-32 bg-cyan-500/20 blur-[100px] -z-10 rounded-full pointer-events-none"></div>

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
                <p className="text-center text-xs font-bold text-slate-500 mb-5 uppercase tracking-widest">Select NLP Processing Route</p>
                <div className="grid grid-cols-2 gap-4">
                <button 
                    onClick={() => handleProcess("DOCUMENT")}
                    disabled={!file || isLoading}
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-4 px-4 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-all duration-300"
                >
                    {isLoading ? 'Running NLP...' : 'Extract Entities'}
                </button>
                <button 
                    onClick={() => handleProcess("SCAN")}
                    disabled={!file || isLoading}
                    className="bg-white/5 border border-white/10 text-slate-300 font-bold py-4 px-4 rounded-xl hover:bg-white/10 disabled:opacity-50 transition-all duration-300"
                >
                    Save as Image
                </button>
                </div>
            </div>
          </div>
        )}

        {/* STEP 2: RESULTS */}
        {step === 2 && extractedData && (
          <div className="space-y-6 animate-fade-in relative z-10">
            <div className="flex justify-between items-end border-b border-white/10 pb-4">
              <h2 className="text-xl font-bold text-white tracking-wide">Structured Output</h2>
              <button onClick={() => {setStep(1); setFile(null); setExtractedData(null);}} className="text-sm font-semibold text-cyan-400 hover:text-cyan-300 transition">Scan Another</button>
            </div>

            <div className="grid gap-4">
              {Object.entries(extractedData).map(([key, value]) => (
                <div key={key} className="bg-slate-900/50 border border-white/5 rounded-xl p-5 hover:bg-slate-900/70 transition duration-300">
                  <h3 className="text-[10px] font-bold text-cyan-500/80 uppercase tracking-widest mb-3">{key.replace(/_/g, ' ')}</h3>
                  
                  {/* Handle Objects (like Patient Details) */}
                  {value !== null && typeof value === 'object' && !Array.isArray(value) ? (
                     <div className="grid grid-cols-2 gap-2">
                        {Object.entries(value).map(([subKey, subVal]) => (
                            <div key={subKey} className="text-sm">
                                <span className="text-slate-400">{subKey.replace(/_/g, ' ')}: </span>
                                <span className="text-slate-100 font-medium">{subVal}</span>
                            </div>
                        ))}
                     </div>
                  ) : 
                  /* Handle Arrays (like Medicines or Doctors) */
                  Array.isArray(value) ? (
                    <div className="flex flex-col gap-2">
                      {value.map((tag, i) => (
                        <div key={i} className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-100 shadow-sm text-sm font-medium px-4 py-2 rounded-lg">
                            {tag}
                        </div>
                      ))}
                    </div>
                  ) : 
                  /* Handle plain strings (like Document Type) */
                  (
                    <p className="text-slate-100 font-medium text-sm">{value}</p>
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