    expect(result.search_time_ms).toBeGreaterThan(0);
  });

  test('should handle invalid queries gracefully', async () => {
    await expect(client.queryPlugins({
      text: '', // Empty query
      max_results: 3
    })).rejects.toThrow();
  });

  test('should add plugin chain successfully', async () => {
    const chain = {
      name: 'Test Chain',
      description: 'Test description',
      plugins: [
        {
          name: 'Test Plugin',
          manufacturer: 'Test Manufacturer',
          category: 'compressor',
          order: 1
        }
      ],
      tags: ['test']
    };

    const result = await client.addPluginChain(chain);
    expect(result).toHaveProperty('id');
    expect(result).toHaveProperty('message');
  });

  test('health check should return healthy status', async () => {
    const health = await client.healthCheck();
    expect(health.status).toBe('healthy');
    expect(health.database).toBe('connected');
  });
});
```

### Integration Testing

```typescript
// Cypress E2E test example
describe('Plugin Recommendation Flow', () => {
  it('should complete full search flow', () => {
    cy.visit('/plugin-search');
    
    // Enter search query
    cy.get('[data-testid="search-input"]')
      .type('warm vocal compressor for indie rock');
    
    // Select filters
    cy.get('[data-testid="genre-select"]').select('indie rock');
    cy.get('[data-testid="instrument-select"]').select('vocals');
    
    // Submit search
    cy.get('[data-testid="search-button"]').click();
    
    // Wait for results
    cy.get('[data-testid="loading"]').should('be.visible');
    cy.get('[data-testid="results"]').should('be.visible');
    
    // Verify results
    cy.get('[data-testid="recommendation"]').should('have.length.greaterThan', 0);
    cy.get('[data-testid="recommendation"]').first().should('contain', 'compressor');
    
    // Test recommendation interaction
    cy.get('[data-testid="recommendation"]').first().click();
    cy.get('[data-testid="plugin-details"]').should('be.visible');
  });
});
```

---

## 📊 Rate Limiting & Usage Guidelines

### Rate Limits
- **Query endpoint**: 60 requests per minute per IP
- **Add chain endpoint**: 10 requests per minute per IP
- **Search endpoint**: 100 requests per minute per IP
- **Health check**: No limit

### Usage Guidelines

```typescript
// Implement client-side rate limiting
class RateLimitedClient {
  private lastRequest = 0;
  private minInterval = 1000; // 1 second between requests

  async makeRequest(requestFn: () => Promise<any>) {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    
    if (timeSinceLastRequest < this.minInterval) {
      await new Promise(resolve => 
        setTimeout(resolve, this.minInterval - timeSinceLastRequest)
      );
    }
    
    this.lastRequest = Date.now();
    return await requestFn();
  }
}

// Usage
const rateLimitedClient = new RateLimitedClient();

await rateLimitedClient.makeRequest(() => 
  client.queryPlugins({ text: 'vocal chain' })
);
```

---

## 🎨 UI/UX Recommendations

### Search Interface

```typescript
interface SearchComponentProps {
  onResults: (results: RAGResponse) => void;
  onError: (error: string) => void;
}

function AdvancedSearchComponent({ onResults, onError }: SearchComponentProps) {
  const [query, setQuery] = useState({
    text: '',
    genre: '',
    instrument: '',
    owned_plugins: [] as string[],
    max_results: 5
  });

  const genres = ['rock', 'pop', 'electronic', 'jazz', 'classical', 'hip-hop'];
  const instruments = ['vocals', 'guitar', 'bass', 'drums', 'piano', 'synth'];
  const popularPlugins = [
    'Waves CLA-2A', 'FabFilter Pro-Q 3', 'SSL G-Master Bus',
    'Universal Audio 1176', 'Soundtoys Decapitator', 'Valhalla VintageVerb'
  ];

  return (
    <div className="search-form">
      <div className="search-input-group">
        <textarea
          value={query.text}
          onChange={(e) => setQuery(prev => ({ ...prev, text: e.target.value }))}
          placeholder="Describe your desired plugin chain... (e.g., 'warm analog vocal processing for indie rock')"
          rows={3}
          className="search-textarea"
        />
      </div>

      <div className="filters-grid">
        <div className="filter-group">
          <label>Genre</label>
          <select
            value={query.genre}
            onChange={(e) => setQuery(prev => ({ ...prev, genre: e.target.value }))}
          >
            <option value="">All Genres</option>
            {genres.map(genre => (
              <option key={genre} value={genre}>{genre}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Instrument</label>
          <select
            value={query.instrument}
            onChange={(e) => setQuery(prev => ({ ...prev, instrument: e.target.value }))}
          >
            <option value="">All Instruments</option>
            {instruments.map(instrument => (
              <option key={instrument} value={instrument}>{instrument}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="owned-plugins">
        <label>Owned Plugins (optional)</label>
        <div className="plugin-chips">
          {popularPlugins.map(plugin => (
            <button
              key={plugin}
              type="button"
              className={`plugin-chip ${
                query.owned_plugins.includes(plugin) ? 'selected' : ''
              }`}
              onClick={() => {
                setQuery(prev => ({
                  ...prev,
                  owned_plugins: prev.owned_plugins.includes(plugin)
                    ? prev.owned_plugins.filter(p => p !== plugin)
                    : [...prev.owned_plugins, plugin]
                }));
              }}
            >
              {plugin}
            </button>
          ))}
        </div>
      </div>

      <div className="search-controls">
        <label>
          Max Results: {query.max_results}
          <input
            type="range"
            min="1"
            max="10"
            value={query.max_results}
            onChange={(e) => setQuery(prev => ({ 
              ...prev, 
              max_results: parseInt(e.target.value) 
            }))}
          />
        </label>
      </div>
    </div>
  );
}
```

### Results Display

```typescript
function RecommendationCard({ recommendation }: { recommendation: PluginRecommendation }) {
  const { chain, similarity_score, explanation, confidence } = recommendation;

  return (
    <div className="recommendation-card">
      <div className="card-header">
        <h3 className="chain-name">{chain.name}</h3>
        <div className="scores">
          <span className="similarity">
            Match: {(similarity_score * 100).toFixed(0)}%
          </span>
          <span className="confidence">
            Confidence: {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <p className="description">{chain.description}</p>

      <div className="tags">
        {chain.tags.map(tag => (
          <span key={tag} className="tag">{tag}</span>
        ))}
      </div>

      <div className="plugin-chain">
        {chain.plugins
          .sort((a, b) => a.order - b.order)
          .map((plugin, index) => (
            <div key={index} className="plugin-step">
              <div className="plugin-info">
                <span className="plugin-order">{plugin.order}</span>
                <div className="plugin-details">
                  <h4 className="plugin-name">{plugin.name}</h4>
                  <p className="plugin-manufacturer">{plugin.manufacturer}</p>
                  <span className="plugin-category">{plugin.category}</span>
                  {plugin.settings && (
                    <p className="plugin-settings">{plugin.settings}</p>
                  )}
                </div>
              </div>
              {index < chain.plugins.length - 1 && (
                <div className="chain-arrow">→</div>
              )}
            </div>
          ))}
      </div>

      <div className="explanation">
        <h4>Why this chain?</h4>
        <p>{explanation}</p>
      </div>

      <div className="card-actions">
        <button className="btn-secondary">Save Chain</button>
        <button className="btn-primary">Use Chain</button>
      </div>
    </div>
  );
}
```

---

## 🔧 Advanced Features

### Real-time Search

```typescript
import { useEffect, useRef } from 'react';
import { debounce } from 'lodash';

function useRealtimeSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PluginRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const client = useRef(new PluginAgentClient());

  const debouncedSearch = useRef(
    debounce(async (searchQuery: string) => {
      if (searchQuery.length < 3) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const response = await client.current.queryPlugins({
          text: searchQuery,
          max_results: 5
        });
        setResults(response.recommendations);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500)
  ).current;

  useEffect(() => {
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query, debouncedSearch]);

  return { query, setQuery, results, loading };
}
```

### Offline Support

```typescript
import { openDB, DBSchema } from 'idb';

interface CacheDB extends DBSchema {
  searches: {
    key: string;
    value: {
      query: PluginQuery;
      response: RAGResponse;
      timestamp: number;
    };
  };
}

class OfflinePluginClient {
  private db: Promise<IDBPDatabase<CacheDB>>;
  private online = navigator.onLine;

  constructor() {
    this.db = openDB<CacheDB>('plugin-cache', 1, {
      upgrade(db) {
        db.createObjectStore('searches');
      },
    });

    window.addEventListener('online', () => this.online = true);
    window.addEventListener('offline', () => this.online = false);
  }

  async queryPlugins(query: PluginQuery): Promise<RAGResponse> {
    const cacheKey = JSON.stringify(query);
    
    // Try cache first
    const db = await this.db;
    const cached = await db.get('searches', cacheKey);
    
    if (cached && Date.now() - cached.timestamp < 3600000) { // 1 hour cache
      return cached.response;
    }

    // If offline, return cached or throw error
    if (!this.online) {
      if (cached) return cached.response;
      throw new Error('Offline and no cached results available');
    }

    // Make API request
    const client = new PluginAgentClient();
    const response = await client.queryPlugins(query);

    // Cache the response
    await db.put('searches', {
      query,
      response,
      timestamp: Date.now()
    }, cacheKey);

    return response;
  }
}
```

---

## 📱 Mobile Considerations

### Responsive Design

```typescript
// Mobile-optimized search component
function MobileSearchComponent() {
  const [showFilters, setShowFilters] = useState(false);
  const [query, setQuery] = useState('');

  return (
    <div className="mobile-search">
      <div className="search-bar">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search plugin chains..."
          className="mobile-search-input"
        />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="filter-toggle"
          aria-label="Toggle filters"
        >
          🔧
        </button>
      </div>

      {showFilters && (
        <div className="mobile-filters">
          <select className="mobile-select">
            <option value="">All Genres</option>
            <option value="rock">Rock</option>
            <option value="pop">Pop</option>
          </select>
          <select className="mobile-select">
            <option value="">All Instruments</option>
            <option value="vocals">Vocals</option>
            <option value="guitar">Guitar</option>
          </select>
        </div>
      )}
    </div>
  );
}
```

### Touch Interactions

```typescript
// Touch-friendly plugin chain display
function TouchPluginChain({ plugins }: { plugins: Plugin[] }) {
  return (
    <div className="touch-plugin-chain">
      {plugins.map((plugin, index) => (
        <div
          key={index}
          className="touch-plugin"
          onTouchStart={(e) => e.currentTarget.classList.add('touching')}
          onTouchEnd={(e) => e.currentTarget.classList.remove('touching')}
        >
          <div className="plugin-icon">{getPluginIcon(plugin.category)}</div>
          <div className="plugin-name">{plugin.name}</div>
          <div className="plugin-manufacturer">{plugin.manufacturer}</div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🚀 Performance Optimization

### Request Batching

```typescript
class BatchedPluginClient {
  private batchQueue: Array<{
    query: PluginQuery;
    resolve: (result: RAGResponse) => void;
    reject: (error: Error) => void;
  }> = [];
  private batchTimeout: NodeJS.Timeout | null = null;

  async queryPlugins(query: PluginQuery): Promise<RAGResponse> {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({ query, resolve, reject });
      
      if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => this.processBatch(), 100);
      }
    });
  }

  private async processBatch() {
    const batch = [...this.batchQueue];
    this.batchQueue.length = 0;
    this.batchTimeout = null;

    // For now, process individually
    // In the future, the API could support batch queries
    for (const item of batch) {
      try {
        const client = new PluginAgentClient();
        const result = await client.queryPlugins(item.query);
        item.resolve(result);
      } catch (error) {
        item.reject(error instanceof Error ? error : new Error(String(error)));
      }
    }
  }
}
```

### Memory Management

```typescript
class OptimizedPluginClient {
  private cache = new Map<string, { data: RAGResponse; timestamp: number }>();
  private maxCacheSize = 100;
  private cacheTimeout = 300000; // 5 minutes

  async queryPlugins(query: PluginQuery): Promise<RAGResponse> {
    const key = JSON.stringify(query);
    const cached = this.cache.get(key);

    // Check cache
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    // Clean old cache entries
    this.cleanCache();

    // Make request
    const client = new PluginAgentClient();
    const result = await client.queryPlugins(query);

    // Cache result
    this.cache.set(key, { data: result, timestamp: Date.now() });

    return result;
  }

  private cleanCache() {
    if (this.cache.size < this.maxCacheSize) return;

    const now = Date.now();
    const entries = Array.from(this.cache.entries());
    
    // Remove expired entries
    entries.forEach(([key, value]) => {
      if (now - value.timestamp > this.cacheTimeout) {
        this.cache.delete(key);
      }
    });

    // Remove oldest entries if still over limit
    if (this.cache.size >= this.maxCacheSize) {
      const sortedEntries = entries
        .filter(([key]) => this.cache.has(key))
        .sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      const toRemove = sortedEntries.slice(0, this.cache.size - this.maxCacheSize + 1);
      toRemove.forEach(([key]) => this.cache.delete(key));
    }
  }
}
```

---

## 📋 Deployment Checklist

### Pre-deployment
- [ ] API endpoints tested and working
- [ ] Error handling implemented
- [ ] Loading states configured
- [ ] Rate limiting considered
- [ ] Offline support (if needed)
- [ ] Mobile responsiveness verified
- [ ] Accessibility tested
- [ ] Performance optimized

### Go-live
- [ ] Health check endpoint monitored
- [ ] Error tracking configured
- [ ] Analytics implemented
- [ ] User feedback collection ready
- [ ] Documentation accessible to team

---

## 📞 Support & Troubleshooting

### Common Issues

1. **CORS Errors**
   - The API includes CORS headers for all origins
   - Ensure you're making requests from HTTPS in production

2. **Empty Results**
   - Check query is descriptive enough (minimum 3 characters)
   - Verify genre/instrument filters aren't too restrictive

3. **Slow Responses**
   - Implement loading states
   - Consider reducing `max_results`
   - Cache frequent queries

4. **Rate Limiting**
   - Implement client-side debouncing
   - Cache results locally
   - Show user-friendly error messages

### Debug Mode

```typescript
const DEBUG_MODE = process.env.NODE_ENV === 'development';

class DebugPluginClient extends PluginAgentClient {
  async queryPlugins(query: PluginQuery): Promise<RAGResponse> {
    if (DEBUG_MODE) {
      console.group('Plugin Query Debug');
      console.log('Query:', query);
      console.time('API Response Time');
    }

    try {
      const result = await super.queryPlugins(query);
      
      if (DEBUG_MODE) {
        console.log('Response:', result);
        console.timeEnd('API Response Time');
        console.groupEnd();
      }

      return result;
    } catch (error) {
      if (DEBUG_MODE) {
        console.error('Query failed:', error);
        console.groupEnd();
      }
      throw error;
    }
  }
}
```

---

## 🎯 Next Steps

1. **Implement basic query functionality** using the examples above
2. **Add error handling and loading states** for better UX
3. **Test with real user queries** to validate integration
4. **Optimize performance** with caching and debouncing
5. **Add advanced features** like saved searches or favorites
6. **Monitor usage** and gather user feedback

---

**API Base URL:** `https://pluginagent.alluristdesign.dev/api/v1`

**Documentation:** Available at `https://pluginagent.alluristdesign.dev/docs`

**Support:** Check `/health` endpoint for API status

---

*This documentation covers all aspects of integrating with the Audio Plugin RAG Agent API. The API is ready for production use and optimized for audio engineering applications.*