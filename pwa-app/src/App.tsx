import { RefreshCw, Radar, AlertCircle } from 'lucide-react';
import { useLeads } from './hooks/useLeads';
import { LeadCard } from './components/LeadCard';

function App() {
  const { leads, loading, error, updateStatus, refetch } = useLeads();

  const pendingLeads = (leads || []).filter(l => l.status === '未處理');
  const processedCount = (leads || []).filter(l => l.status === '已回覆').length;

  return (
    <div className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f]">
      {/* 頂部導航 - 極簡隱形 */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-black/5 px-6 py-4 transition-all">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radar size={22} className="text-[#0071e3]" />
            <span className="text-lg font-bold tracking-tight text-[#1d1d1f]">鎧鉅獵漏雷達</span>
          </div>
          <button 
            onClick={refetch}
            disabled={loading}
            className="text-sm font-medium text-[#0071e3] hover:text-[#0077ed] transition-colors flex items-center gap-2"
          >
            {loading ? <RefreshCw size={16} className="animate-spin" /> : '重新掃描'}
          </button>
        </div>
      </nav>

      {/* 英雄區塊 - Apple 演講氛圍 */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
            <span className="text-[#1d1d1f]">潛在客源。</span><br/>
            <span className="text-[#86868b]">掌握在指尖。</span>
          </h1>
          <p className="text-xl md:text-2xl font-medium text-[#86868b] mb-12 tracking-normal max-w-2xl mx-auto">
            自動化掃描中台灣所有修繕求救貼文，<br className="hidden md:block"/>
            讓每一筆需求都成為您的下一個訂單。
          </p>
          
          <div className="flex justify-center gap-12 text-center border-t border-black/5 pt-12">
            <div>
              <p className="text-xs text-[#86868b] uppercase tracking-widest mb-1">待處理</p>
              <p className="text-5xl font-bold tabular-nums text-[#1d1d1f]">{pendingLeads.length}</p>
            </div>
            <div className="w-px h-16 bg-black/5 self-center"></div>
            <div>
              <p className="text-xs text-[#86868b] uppercase tracking-widest mb-1">本月已轉換</p>
              <p className="text-5xl font-bold tabular-nums text-[#1d1d1f]">{processedCount}</p>
            </div>
          </div>
        </div>
      </section>

      {/* 主要內容區 - 居中平鋪佈局 */}
      <main className="max-w-2xl mx-auto px-6 pb-40">
        <div className="flex items-center justify-between mb-10 border-b border-black/5 pb-6">
          <h2 className="text-2xl font-bold text-[#1d1d1f]">最新雷達回報</h2>
          <span className="text-sm font-medium text-[#86868b]">
            {loading ? '掃描中...' : `共 ${leads.length} 筆回報`}
          </span>
        </div>

        {error && (
          <div className="mb-10 p-6 rounded-3xl border border-red-500/20 bg-red-50 flex items-start gap-4 text-red-600">
            <AlertCircle className="shrink-0 mt-1" size={24} />
            <div>
              <p className="font-bold mb-1">連線異常</p>
              <p className="text-sm opacity-90">{error}</p>
            </div>
          </div>
        )}

        <div className="space-y-8">
          {loading && leads.length === 0 ? (
            <div className="py-20 flex flex-col items-center gap-4 text-center">
              <RefreshCw size={40} className="animate-spin text-[#0071e3] opacity-40 mb-2" />
              <p className="text-[#86868b] font-medium">正在對接中台灣雷達站...</p>
              <p className="text-xs text-[#86868b]/70">正在擷取最新 Facebook 與 Threads 文章</p>
            </div>
          ) : leads.length === 0 ? (
            <div className="py-20 text-center bg-white border border-black/5 shadow-sm rounded-3xl p-12">
              <p className="text-[#86868b] text-lg font-medium">目前雷達範圍內尚無需求</p>
            </div>
          ) : (
            leads.map(lead => (
              <LeadCard 
                key={lead.id} 
                lead={lead} 
                onStatusChange={updateStatus} 
              />
            ))
          )}
        </div>
      </main>

      {/* 底部裝飾 */}
      <footer className="py-16 text-center border-t border-black/5 bg-[#f5f5f7]">
        <p className="text-[#86868b] text-xs font-semibold uppercase tracking-widest">© 2026 鎧鉅工程行. 精準、專業、使命必達.</p>
      </footer>
    </div>
  );
}

export default App;
