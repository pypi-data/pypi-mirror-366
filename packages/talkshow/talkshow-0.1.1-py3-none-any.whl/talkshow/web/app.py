"""
TalkShow FastAPI Application

Main web application for serving TalkShow API and frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
import json
import os
import yaml
from pathlib import Path
import re # Added for markdown filename generation

# Import TalkShow components
from ..storage.json_storage import JSONStorage
from ..models.chat import ChatSession
from ..config.manager import ConfigManager

# Create FastAPI app
app = FastAPI(
    title="TalkShow API",
    description="Chat History Analysis and Visualization API",
    version="0.2.0"
)

# Initialize configuration manager
config_manager = ConfigManager()

# Data storage
storage_path = config_manager.get_data_file_path()
print(f"Using data file: {storage_path}")
storage = JSONStorage(str(storage_path))

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    try:
        # 读取HTML文件
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            return HTMLResponse(content=html_path.read_text(encoding='utf-8'))
        else:
            # 如果文件不存在，返回简单的HTML
            return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TalkShow - Chat History Viewer</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div id="app">
            <h1>🎭 TalkShow</h1>
            <p>Loading chat history...</p>
        </div>
        <script src="/static/script.js"></script>
    </body>
    </html>
            """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load page: {str(e)}")


@app.get("/api/sessions", response_model=List[Dict[str, Any]])
async def get_sessions():
    """Get all chat sessions with metadata."""
    try:
        sessions = storage.load_all_sessions()
        
        session_list = []
        for session in sessions:
            # 直接使用会话的filename作为markdown文件名
            # 因为session.meta.filename应该就是实际的Markdown文件名
            markdown_filename = session.meta.filename
            
            session_data = {
                "filename": session.meta.filename,
                "theme": session.meta.theme,
                "markdown_filename": markdown_filename,  # 使用原始filename
                "created_time": session.meta.ctime.isoformat() if session.meta.ctime else None,
                "qa_count": len(session.qa_pairs),
                "has_summaries": any(qa.question_summary or qa.answer_summary for qa in session.qa_pairs),
                "first_question": session.qa_pairs[0].question[:50] + "..." if session.qa_pairs else None,
                "timestamp": session.qa_pairs[0].timestamp.isoformat() if session.qa_pairs and session.qa_pairs[0].timestamp else None
            }
            session_list.append(session_data)
        
        # Sort by created_time
        session_list.sort(key=lambda x: x["created_time"] or "", reverse=False)
        
        return session_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sessions: {str(e)}")


@app.get("/api/sessions/{filename}", response_model=Dict[str, Any])
async def get_session_details(filename: str):
    """Get detailed information for a specific session."""
    try:
        sessions = storage.load_all_sessions()
        
        # Find the session
        target_session = None
        for session in sessions:
            if session.meta.filename == filename:
                target_session = session
                break
        
        if not target_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build detailed response
        qa_pairs = []
        for qa in target_session.qa_pairs:
            qa_data = {
                "question": qa.question,
                "answer": qa.answer,
                "question_summary": qa.question_summary,
                "answer_summary": qa.answer_summary,
                "timestamp": qa.timestamp.isoformat() if qa.timestamp else None
            }
            qa_pairs.append(qa_data)
        
        session_detail = {
            "filename": target_session.meta.filename,
            "theme": target_session.meta.theme,
            "created_time": target_session.meta.ctime.isoformat() if target_session.meta.ctime else None,
            "qa_pairs": qa_pairs,
            "qa_count": len(qa_pairs),
            "has_summaries": any(qa.question_summary or qa.answer_summary for qa in target_session.qa_pairs)
        }
        
        return session_detail
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load session details: {str(e)}")


@app.get("/api/stats", response_model=Dict[str, Any])
async def get_stats():
    """Get overall statistics about the chat history."""
    try:
        sessions = storage.load_all_sessions()
        
        total_sessions = len(sessions)
        total_qa_pairs = sum(len(session.qa_pairs) for session in sessions)
        
        # Count summaries
        question_summaries = 0
        answer_summaries = 0
        
        # Date range
        all_dates = []
        
        for session in sessions:
            if session.meta.ctime:
                all_dates.append(session.meta.ctime)
            
            for qa in session.qa_pairs:
                if qa.question_summary:
                    question_summaries += 1
                if qa.answer_summary:
                    answer_summaries += 1
                
                if qa.timestamp:
                    all_dates.append(qa.timestamp)
        
        date_range = {
            "start": min(all_dates).isoformat() if all_dates else None,
            "end": max(all_dates).isoformat() if all_dates else None
        }
        
        # File size
        file_size = 0
        if os.path.exists(storage_path):
            file_size = os.path.getsize(storage_path)
        
        stats = {
            "total_sessions": total_sessions,
            "total_qa_pairs": total_qa_pairs,
            "question_summaries": question_summaries,
            "answer_summaries": answer_summaries,
            "average_qa_per_session": round(total_qa_pairs / total_sessions, 1) if total_sessions > 0 else 0,
            "date_range": date_range,
            "storage_file_size": file_size,
            "storage_info": storage.get_storage_info()
        }
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.get("/api/timeline", response_model=List[Dict[str, Any]])
async def get_timeline():
    """Get timeline data for visualization."""
    try:
        sessions = storage.load_all_sessions()
        
        timeline_data = []
        
        for session in sessions:
            if not session.qa_pairs:
                continue
            
            # Get session start time from first QA pair or meta
            session_time = session.meta.ctime
            if not session_time and session.qa_pairs:
                session_time = session.qa_pairs[0].timestamp
            
            if not session_time:
                continue
            
            session_entry = {
                "filename": session.meta.filename,
                "theme": session.meta.theme,
                "time": session_time.isoformat(),
                "qa_count": len(session.qa_pairs),
                "type": "session_start",
                "summary": f"{session.meta.theme} ({len(session.qa_pairs)} Q&As)"
            }
            timeline_data.append(session_entry)
            
            # Add individual QA pairs for detailed timeline
            for i, qa in enumerate(session.qa_pairs):
                if qa.timestamp:
                    qa_entry = {
                        "filename": session.meta.filename,
                        "theme": session.meta.theme,
                        "time": qa.timestamp.isoformat(),
                        "qa_index": i,
                        "type": "qa_pair",
                        "question": qa.question_summary or qa.question[:50] + "..." if len(qa.question) > 50 else qa.question,
                        "answer": qa.answer_summary or qa.answer[:100] + "..." if len(qa.answer) > 100 else qa.answer
                    }
                    timeline_data.append(qa_entry)
        
        # Sort by time
        timeline_data.sort(key=lambda x: x["time"])
        
        return timeline_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate timeline: {str(e)}")


@app.get("/view/{filename}")
async def view_markdown(filename: str):
    """View markdown content as a rendered HTML page."""
    try:
        # 解码URL编码的文件名
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        # 构建MD文件路径
        md_path = Path("history") / decoded_filename
        
        if not md_path.exists():
            raise HTTPException(status_code=404, detail=f"Markdown file not found: {decoded_filename}")
        
        # 读取文件内容
        content = md_path.read_text(encoding='utf-8')
        
        # 生成HTML页面
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{decoded_filename} - TalkShow</title>
    <link rel="stylesheet" href="/static/style.css">
    <!-- Markdown 渲染器 -->
    <script src="https://cdn.jsdelivr.net/npm/showdown@2.1.0/dist/showdown.min.js"></script>
    <!-- 代码高亮 -->
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css">
    <style>
        .md-viewer {{
            max-width: 1000px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .md-header {{
            border-bottom: 2px solid #667eea;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        .md-header h1 {{
            margin: 0;
            color: #2c3e50;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 1rem;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        body {{
            background: #f5f5f5;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
    </style>
</head>
<body>
    <div class="md-viewer">
        <a href="/" class="back-link">← 返回时间轴</a>
        <div class="md-header">
            <h1>📄 {decoded_filename}</h1>
        </div>
        <div id="md-content">
            <div style="text-align: center; padding: 2rem; color: #666;">正在渲染 Markdown 内容...</div>
        </div>
    </div>
    
    <script>
        // 渲染Markdown内容
        document.addEventListener('DOMContentLoaded', function() {{
            const content = {repr(content)};
            const mdContent = document.getElementById('md-content');
            
            if (typeof showdown !== 'undefined') {{
                try {{
                    const converter = new showdown.Converter({{
                        tables: true,
                        tasklists: true,
                        strikethrough: true,
                        emoji: true,
                        headerLevelStart: 1,
                        simplifiedAutoLink: true,
                        openLinksInNewWindow: true,
                        backslashEscapesHTMLTags: true
                    }});
                    
                    const htmlContent = converter.makeHtml(content);
                    mdContent.innerHTML = htmlContent;
                    
                    // 使用Prism.js高亮代码块
                    if (typeof Prism !== 'undefined') {{
                        setTimeout(() => {{
                            Prism.highlightAllUnder(mdContent);
                        }}, 100);
                    }}
                    
                    console.log('Markdown rendered successfully');
                }} catch (error) {{
                    console.error('Markdown rendering error:', error);
                    mdContent.innerHTML = '<pre style="white-space: pre-wrap; font-family: monospace;">' + 
                                         content.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</pre>';
                }}
            }} else {{
                mdContent.innerHTML = '<pre style="white-space: pre-wrap; font-family: monospace;">' + 
                                     content.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</pre>';
            }}
        }});
    </script>
</body>
</html>
        """
        
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render markdown: {str(e)}")


@app.get("/api/markdown/{filename}")
async def get_markdown_content(filename: str):
    """Get original markdown content of a chat session file."""
    try:
        # 解码URL编码的文件名
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        # 构建MD文件路径
        md_path = Path("history") / decoded_filename
        
        if not md_path.exists():
            raise HTTPException(status_code=404, detail=f"Markdown file not found: {decoded_filename}")
        
        # 读取文件内容
        content = md_path.read_text(encoding='utf-8')
        
        return {
            "filename": decoded_filename,
            "content": content,
            "size": len(content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read markdown file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)