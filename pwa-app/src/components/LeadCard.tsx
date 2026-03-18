import { ExternalLink, Check, MoreHorizontal } from 'lucide-react';
import type { Lead } from '../hooks/useLeads';

interface LeadCardProps {
  lead: Lead;
  onStatusChange: (id: string, status: Lead['status']) => void;
}

export function LeadCard({ lead, onStatusChange }: LeadCardProps) {
  const isProcessed = lead.status !== '未處理';

  const handleCopyAndReply = () => {
    const replyText = `您好，我們是鎧鉅工程行。針對您在「${lead.category}」的需求，我們具備專業證照與多年經驗。若需要評估，歡迎直接私訊，謝謝！`;
    navigator.clipboard.writeText(replyText).then(() => {
      window.open(lead.url, '_blank', 'noopener,noreferrer');
    });
  };

  return (
    <div className={`apple-card p-8 group ${isProcessed ? 'opacity-50 grayscale-[0.5]' : 'opacity-100'}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-[#0071e3] animate-pulse"></div>
          <span className="text-xs font-bold uppercase tracking-widest text-[#0071e3]">
            {lead.platform}
          </span>
        </div>
        <span className="text-xs font-medium text-[#86868b] tabular-nums">
          {new Date(lead.post_date).toLocaleDateString('zh-TW')}
        </span>
      </div>

      <h3 className="text-3xl font-bold mb-4 text-[#1d1d1f] group-hover:text-[#0071e3] transition-colors">
        {lead.category}
      </h3>

      <p className="text-[#515154] text-lg leading-relaxed mb-8 font-medium">
        {lead.content_summary}
      </p>

      {lead.image_url && (
        <div className="rounded-2xl overflow-hidden mb-8 border border-black/5 bg-[#f5f5f7]">
          <img src={lead.image_url} alt="貼文預覽" className="w-full h-auto mix-blend-multiply" />
        </div>
      )}

      <div className="flex items-center gap-4">
        {lead.status === '未處理' ? (
          <>
            <button 
              onClick={handleCopyAndReply}
              className="apple-button-primary flex-1 flex items-center justify-center gap-2 group/btn shadow-sm shadow-[#0071e3]/20"
            >
              一鍵回覆 <ExternalLink size={18} className="transition-transform group-hover/btn:translate-x-1" />
            </button>
            <button 
              onClick={() => onStatusChange(lead.id, '已回覆')}
              className="w-14 h-14 rounded-full flex items-center justify-center border border-black/10 hover:bg-black/5 text-[#86868b] hover:text-[#0071e3] transition-all bg-[#f5f5f7]"
              title="標記完成"
            >
              <Check size={24} />
            </button>
            <button 
              onClick={() => onStatusChange(lead.id, '略過')}
              className="w-14 h-14 rounded-full flex items-center justify-center border border-black/10 hover:bg-black/5 text-[#86868b] hover:text-[#1d1d1f] transition-all bg-[#f5f5f7]"
              title="略過"
            >
              <MoreHorizontal size={24} />
            </button>
          </>
        ) : (
          <div className="flex w-full items-center justify-between pt-6 border-t border-black/5">
            <span className="text-sm font-semibold text-[#86868b]">單據狀態：{lead.status}</span>
            <button 
              onClick={() => onStatusChange(lead.id, '未處理')}
              className="text-sm font-bold text-[#0071e3] hover:underline"
            >
              重新激活
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
