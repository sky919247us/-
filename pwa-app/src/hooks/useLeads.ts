import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export interface Lead {
  id: string;
  platform: string;
  post_date: string;
  category: string;
  content_summary: string;
  image_url: string | null;
  ai_tags: string | null;
  url: string;
  status: '未處理' | '已回覆' | '略過';
}

export function useLeads() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 初次載入
  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from('leads')
        .select('*')
        .order('post_date', { ascending: false });
      
      if (error) throw error;
      setLeads((data as Lead[]) || []);
    } catch (err: any) {
      setError(err.message || '無法取得名單資料');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id: string, newStatus: Lead['status']) => {
    try {
      // 樂觀更新 UI
      setLeads((prev) => 
        prev.map((lead) => (lead.id === id ? { ...lead, status: newStatus } : lead))
      );
      
      const { error } = await supabase
        .from('leads')
        .update({ status: newStatus })
        .eq('id', id);

      if (error) throw error;
    } catch (err: any) {
      console.error('更新狀態失敗:', err);
      // 若失敗可以呼叫 fetchLeads() 回復，這裡為簡化先印錯誤
    }
  };

  return { leads, loading, error, updateStatus, refetch: fetchLeads };
}
