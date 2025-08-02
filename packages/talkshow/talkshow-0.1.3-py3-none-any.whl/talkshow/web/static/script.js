// TalkShow Frontend JavaScript

class TalkShowApp {
    constructor() {
        this.sessions = [];
        this.stats = {};
        this.dailyInsights = {}; // 新的数据结构：按日期分组的问题
        this.selectedSession = null;
        this.currentTimeFilter = 'all';
        this.searchQuery = '';
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            this.processDailyInsights(); // 处理数据为按日期分组的格式
            this.renderApp();
            this.setupEventListeners();
        } catch (error) {
            this.showError('Failed to initialize app: ' + error.message);
        }
    }
    
    async loadData() {
        try {
            // Load all data needed for daily insights in a single request
            const [insightsResponse, statsResponse] = await Promise.all([
                fetch('/api/sessions/insights'),  // Use optimized endpoint
                fetch('/api/stats')
            ]);
            
            if (!insightsResponse.ok || !statsResponse.ok) {
                throw new Error('Failed to fetch data from API');
            }
            
            const insightsData = await insightsResponse.json();
            this.stats = await statsResponse.json();
            
            // Use the insights data directly - it already contains qa_pairs
            this.sessions = insightsData;
            
            console.log('Loaded data:', {
                sessions: this.sessions.length,
                stats: this.stats,
                totalApiCalls: 2  // Only 2 API calls instead of N+1!
            });
            
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }
    
    // 基于 daily_insights.py 的逻辑处理数据
    processDailyInsights() {
        this.dailyInsights = {};
        
        for (const session of this.sessions) {
            const sessionStartTime = new Date(session.created_time);
            const dateStr = sessionStartTime.toISOString().split('T')[0]; // YYYY-MM-DD
            
            if (!this.dailyInsights[dateStr]) {
                this.dailyInsights[dateStr] = [];
            }
            
            // 为每个QA pair创建时间条目
            for (const qaPair of session.qa_pairs) {
                const question = qaPair.question?.trim();
                if (question) {
                    // 使用QA pair的时间戳，如果没有则使用会话开始时间
                    const qaTime = qaPair.timestamp ? new Date(qaPair.timestamp) : sessionStartTime;
                    
                    // 归整时间到最近的半点或整点
                    const roundedTime = this.roundToHalfHour(qaTime);
                    
                    // 使用已有的摘要，如果没有则使用原问题
                    const qSummary = qaPair.question_summary || question;
                    
                    this.dailyInsights[dateStr].push({
                        time: roundedTime,
                        timeStr: roundedTime.toTimeString().slice(0, 5), // HH:MM
                        original: question,
                        summary: qSummary,
                        sessionTheme: session.theme,
                        sessionFilename: session.filename,
                        markdownFilename: session.markdown_filename  // 新增字段
                    });
                }
            }
        }
        
        // 对每天的问题按时间排序
        for (const dateStr in this.dailyInsights) {
            this.dailyInsights[dateStr].sort((a, b) => a.time - b.time);
        }
    }
    
    // 归整时间到最近的半点或整点
    roundToHalfHour(dt) {
        const minutes = dt.getMinutes();
        let roundedMinutes;
        
        if (minutes <= 15) {
            // 归整到整点
            roundedMinutes = 0;
        } else if (minutes <= 45) {
            // 归整到半点
            roundedMinutes = 30;
        } else {
            // 归整到下一个整点
            roundedMinutes = 0;
            dt = new Date(dt.getTime() + 60 * 60 * 1000); // 加一小时
        }
        
        return new Date(dt.getFullYear(), dt.getMonth(), dt.getDate(), dt.getHours(), roundedMinutes, 0, 0);
    }
    
    renderApp() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="container">
                ${this.renderHeader()}
                ${this.renderStats()}
                ${this.renderControls()}
                <div id="daily-insights" class="daily-insights">
                    ${this.renderDailyInsights()}
                </div>
            </div>
        `;
    }
    
    renderHeader() {
        return `
            <div class="header">
                <h1>🎭 TalkShow - 思维日记</h1>
                <p>Chat History Analysis and Visualization</p>
            </div>
        `;
    }
    
    renderStats() {
        const totalDays = Object.keys(this.dailyInsights).length;
        const totalQuestions = Object.values(this.dailyInsights).reduce((sum, questions) => sum + questions.length, 0);
        
        return `
            <div class="stats-panel">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">${totalDays}</div>
                        <div class="stat-label">总天数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${totalQuestions}</div>
                        <div class="stat-label">总问题数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.total_sessions || 0}</div>
                        <div class="stat-label">总会话数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.total_qa_pairs || 0}</div>
                        <div class="stat-label">Q&A对话</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.question_summaries || 0}</div>
                        <div class="stat-label">问题摘要</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.formatFileSize(this.stats.storage_file_size || 0)}</div>
                        <div class="stat-label">数据文件大小</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderControls() {
        const dateOptions = this.getDateFilterOptions();
        
        return `
            <div class="controls">
                <div class="control-group">
                    <label for="dateFilter">日期筛选:</label>
                    <select id="dateFilter">
                        <option value="all">全部日期</option>
                        ${dateOptions.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('')}
                    </select>
                </div>
                <div class="control-group">
                    <label for="searchInput">搜索:</label>
                    <input type="text" id="searchInput" placeholder="搜索问题或主题...">
                </div>
                <div class="control-group">
                    <button onclick="app.refreshData()">刷新数据</button>
                    <button onclick="app.exportData()">导出数据</button>
                </div>
            </div>
        `;
    }
    
    renderDailyInsights() {
        if (!this.dailyInsights || Object.keys(this.dailyInsights).length === 0) {
            return '<div class="empty-state">暂无数据</div>';
        }
        
        const sortedDates = Object.keys(this.dailyInsights).sort();
        const totalQuestions = Object.values(this.dailyInsights).reduce((sum, questions) => sum + questions.length, 0);
        
        let html = `
            <div class="daily-insights-header">
                <h3>📊 思维日记 (Daily Insights)</h3>
                <div class="scroll-hint">💡 左右滑动查看更多日期</div>
            </div>
            <div class="daily-insights-container">
        `;
        
        sortedDates.forEach(date => {
            const questions = this.dailyInsights[date];
            const questionCount = questions.length;
            
            html += `
                <div class="daily-column">
                    <div class="daily-column-header">
                        <h4>${date}</h4>
                        <span class="question-count">${questionCount} 个问题</span>
                    </div>
                    <div class="daily-column-content">
            `;
            
            questions.forEach(question => {
                html += `
                    <div class="daily-question">
                        <div class="question-summary">${question.summary}</div>
                        <div class="question-time">${question.timeStr}</div>
                        ${question.markdownFilename ? `<div class="question-theme"><a href="/view/${encodeURIComponent(question.markdownFilename)}" target="_blank" class="theme-link">${question.sessionTheme || question.markdownFilename}</a></div>` : ''}
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        html += `
            </div>
            <div class="daily-insights-footer">
                <small>显示 ${sortedDates.length} 天，共 ${totalQuestions} 个问题</small>
            </div>
        `;
        
        return html;
    }
    
    getFilteredDailyInsights() {
        let filtered = { ...this.dailyInsights };
        
        // Apply date filter
        if (this.currentTimeFilter !== 'all') {
            const filterDate = this.currentTimeFilter;
            filtered = Object.fromEntries(
                Object.entries(filtered).filter(([date]) => date >= filterDate)
            );
        }
        
        // Apply search filter
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filtered = Object.fromEntries(
                Object.entries(filtered).map(([date, questions]) => [
                    date,
                    questions.filter(q => 
                        q.summary.toLowerCase().includes(query) ||
                        q.original.toLowerCase().includes(query) ||
                        q.sessionTheme.toLowerCase().includes(query)
                    )
                ]).filter(([date, questions]) => questions.length > 0)
            );
        }
        
        return filtered;
    }
    
    getDateFilterOptions() {
        const dates = Object.keys(this.dailyInsights).sort();
        if (!dates.length) return [];
        
        const options = [];
        const now = new Date();
        const oneDay = 24 * 60 * 60 * 1000;
        
        // Last 7 days
        options.push({
            value: new Date(now - 7 * oneDay).toISOString().split('T')[0],
            label: '过去一周'
        });
        
        // Last 30 days
        options.push({
            value: new Date(now - 30 * oneDay).toISOString().split('T')[0],
            label: '过去一月'
        });
        
        return options;
    }
    
    setupEventListeners() {
        // Date filter
        const dateFilter = document.getElementById('dateFilter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.currentTimeFilter = e.target.value;
                this.updateDailyInsights();
            });
        }
        
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.updateDailyInsights();
            });
        }
        
        // Setup question row click events
        this.setupQuestionRowEvents();
    }
    
    setupQuestionRowEvents() {
        // 为问题行添加点击事件，可以查看详细会话
        document.querySelectorAll('.question-row').forEach(row => {
            row.addEventListener('click', () => {
                const filename = row.dataset.filename;
                if (filename) {
                    window.open(`/view/${encodeURIComponent(filename)}`, '_blank');
                }
            });
        });
    }
    
    updateDailyInsights() {
        const container = document.querySelector('.daily-insights-container');
        if (container) {
            container.outerHTML = this.renderDailyInsights();
            this.setupQuestionRowEvents();
        }
    }
    
    async refreshData() {
        try {
            this.showLoading();
            await this.loadData();
            this.processDailyInsights();
            this.renderApp();
            this.setupEventListeners();
        } catch (error) {
            this.showError('刷新数据失败: ' + error.message);
        }
    }
    
    exportData() {
        const data = {
            daily_insights: this.dailyInsights,
            stats: this.stats,
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `talkshow_daily_insights_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }
    
    // Utility functions
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
    
    showLoading() {
        const app = document.getElementById('app');
        app.innerHTML = '<div class="loading">加载中...</div>';
    }
    
    showError(message) {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="container">
                <div class="error">
                    <strong>错误:</strong> ${message}
                </div>
                <button onclick="location.reload()">重新加载</button>
            </div>
        `;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TalkShowApp();
});

// Global functions for button clicks
window.app = null;