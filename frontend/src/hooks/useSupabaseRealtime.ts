import { useEffect, useRef, useState } from 'react';
import { RealtimeChannel } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';

// Hook for real-time company updates
export function useCompanyRealtime(symbol?: string) {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!symbol) return;

    // Subscribe to company updates
    const channel = supabase
      .channel(`company:${symbol}`)
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'companies', filter: `symbol=eq.${symbol}` },
        (payload) => {
          setData(payload);
        }
      )
      .on('presence', { event: 'sync' }, () => {
        setIsConnected(true);
      })
      .on('presence', { event: 'join' }, () => {
        setIsConnected(true);
      })
      .on('presence', { event: 'leave' }, () => {
        setIsConnected(false);
      })
      .subscribe();

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, [symbol]);

  return { data, isConnected };
}

// Hook for real-time market data updates
export function useMarketDataRealtime() {
  const [data, setData] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    // Subscribe to all company updates
    const channel = supabase
      .channel('market-data')
      .on('postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'companies' },
        (payload) => {
          setData(prev => {
            const newData = [...prev];
            const existingIndex = newData.findIndex(item => item.id === payload.new.id);
            if (existingIndex >= 0) {
              newData[existingIndex] = payload.new;
            } else {
              newData.push(payload.new);
            }
            return newData;
          });
        }
      )
      .on('presence', { event: 'sync' }, () => {
        setIsConnected(true);
      })
      .subscribe();

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, []);

  return { data, isConnected };
}

// Hook for real-time portfolio updates
export function usePortfolioRealtime(userId: string) {
  const [data, setData] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!userId) return;

    // Subscribe to portfolio updates
    const channel = supabase
      .channel(`portfolios:${userId}`)
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'portfolios', filter: `user_id=eq.${userId}` },
        (payload) => {
          setData(prev => {
            const newData = [...prev];
            if (payload.eventType === 'INSERT') {
              newData.push(payload.new);
            } else if (payload.eventType === 'UPDATE') {
              const index = newData.findIndex(item => item.id === payload.new.id);
              if (index >= 0) {
                newData[index] = payload.new;
              }
            } else if (payload.eventType === 'DELETE') {
              return newData.filter(item => item.id !== payload.old.id);
            }
            return newData;
          });
        }
      )
      .on('presence', { event: 'sync' }, () => {
        setIsConnected(true);
      })
      .subscribe();

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, [userId]);

  return { data, isConnected };
}

// Hook for real-time watchlist updates
export function useWatchlistRealtime(userId: string) {
  const [data, setData] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    if (!userId) return;

    // Subscribe to watchlist updates
    const channel = supabase
      .channel(`watchlist:${userId}`)
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'watchlist', filter: `user_id=eq.${userId}` },
        (payload) => {
          setData(prev => {
            const newData = [...prev];
            if (payload.eventType === 'INSERT') {
              newData.push(payload.new);
            } else if (payload.eventType === 'UPDATE') {
              const index = newData.findIndex(item => item.id === payload.new.id);
              if (index >= 0) {
                newData[index] = payload.new;
              }
            } else if (payload.eventType === 'DELETE') {
              return newData.filter(item => item.id !== payload.old.id);
            }
            return newData;
          });
        }
      )
      .on('presence', { event: 'sync' }, () => {
        setIsConnected(true);
      })
      .subscribe();

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, [userId]);

  return { data, isConnected };
}

// Generic hook for any table subscription
export function useTableRealtime<T = any>(
  table: string,
  filter?: { column: string; value: string }
) {
  const [data, setData] = useState<T[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    const channelName = filter
      ? `${table}:${filter.column}:${filter.value}`
      : table;

    const channel = supabase
      .channel(channelName)
      .on('postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: table,
          ...(filter && { filter: `${filter.column}=eq.${filter.value}` })
        },
        (payload) => {
          setData(prev => {
            const newData = [...prev];
            if (payload.eventType === 'INSERT') {
              newData.push(payload.new);
            } else if (payload.eventType === 'UPDATE') {
              const index = newData.findIndex(item => item.id === payload.new.id);
              if (index >= 0) {
                newData[index] = payload.new;
              }
            } else if (payload.eventType === 'DELETE') {
              return newData.filter(item => item.id !== payload.old.id);
            }
            return newData;
          });
        }
      )
      .on('presence', { event: 'sync' }, () => {
        setIsConnected(true);
      })
      .subscribe();

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, [table, filter?.column, filter?.value]);

  return { data, isConnected };
}

// Hook for presence (user online status)
export function usePresence(channelName: string) {
  const [presence, setPresence] = useState<any>({});
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<RealtimeChannel | null>(null);

  useEffect(() => {
    const channel = supabase
      .channel(channelName)
      .on('presence', { event: 'sync' }, () => {
        const newState = channel.presenceState();
        setPresence(newState);
        setIsConnected(true);
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        setPresence(prev => ({
          ...prev,
          [key]: newPresences[0],
        }));
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        setPresence(prev => {
          const newState = { ...prev };
          delete newState[key];
          return newState;
        });
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          await channel.track({ user_id: 'current-user', online_at: new Date().toISOString() });
        }
      });

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
      }
    };
  }, [channelName]);

  return { presence, isConnected };
}
