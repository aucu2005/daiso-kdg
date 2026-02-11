import { create } from 'zustand';
import { searchProducts, Product, SearchResponse } from '@/lib/api';

interface SearchState {
    query: string;
    response: SearchResponse | null;
    selectedProduct: Product | null;
    isLoading: boolean;
    error: string | null;

    setQuery: (query: string) => void;
    performSearch: (query: string) => Promise<void>;
    selectProduct: (product: Product) => void;
    clearResults: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
    query: '',
    response: null,
    selectedProduct: null,
    isLoading: false,
    error: null,

    setQuery: (query) => set({ query }),

    performSearch: async (query) => {
        set({ isLoading: true, error: null, query });
        try {
            const data = await searchProducts(query);
            // Auto-select the first product or the reranked one
            let selected: Product | null = null;

            if (data.rerank?.selected_id && data.products.length > 0) {
                selected = data.products.find(p => String(p.id) === String(data.rerank?.selected_id)) || data.products[0];
            } else if (data.products.length > 0) {
                selected = data.products[0];
            }

            set({
                response: data,
                selectedProduct: selected,
                isLoading: false
            });
        } catch (err) {
            console.error(err);
            set({
                error: '검색 중 오류가 발생했습니다.',
                isLoading: false,
                response: null
            });
        }
    },

    selectProduct: (selectedProduct) => set({ selectedProduct }),

    clearResults: () => set({
        query: '',
        response: null,
        selectedProduct: null,
        error: null
    }),
}));
