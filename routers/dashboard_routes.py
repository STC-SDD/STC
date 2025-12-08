# from fastapi import (
#     APIRouter,
#     WebSocket,
#     WebSocketDisconnect,
#     File,
#     UploadFile,
#     HTTPException,
#     Form,
# )
# from fastapi.responses import HTMLResponse
# from datetime import datetime
# import json
# import os
# import shutil

# import services.dashboard_state as ds

# router = APIRouter()

# # ---------------- ADMIN HTML ----------------

# ADMIN_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
#     <title>Admin Dashboard</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body { font-family: Arial, sans-serif; background: #f0f2f5; }
#         .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; }
#         .header h1 { font-size: 32px; margin-bottom: 8px; }
#         .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
#         .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
#         .stat-card { background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
#         .stat-card h3 { font-size: 14px; color: #666; text-transform: uppercase; margin-bottom: 10px; }
#         .stat-card .value { font-size: 42px; font-weight: bold; color: #667eea; }
#         .content { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
#         .upload-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
#         .upload-area { border: 2px dashed #667eea; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.3s; }
#         .upload-area:hover { background: #f8f9ff; border-color: #764ba2; }
#         .upload-area.dragover { background: #e7f3ff; border-color: #667eea; }
#         .btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 15px; }
#         .btn:hover { opacity: 0.9; }
#         #fileInput { display: none; }
#         .video-info { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; }
#         .video-preview { margin-top: 15px; }
#         .video-preview video { width: 100%; max-width: 400px; border-radius: 8px; }
#         table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
#         th { background: #f8f9fa; padding: 15px; text-align: left; font-size: 13px; color: #666; text-transform: uppercase; }
#         td { padding: 15px; border-top: 1px solid #eee; vertical-align: top; }
#         td:nth-child(1) { width: 15%; }
#         td:nth-child(2) { width: 12%; }
#         td:nth-child(3) { width: 12%; }
#         td:nth-child(4) { width: 40%; }
#         td:nth-child(5) { width: 21%; }
#         .badge { display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }
#         .badge-active { background: #d4edda; color: #155724; }
#         .badge-inactive { background: #f8d7da; color: #721c24; }
#         .badge-online { background: #d4edda; color: #155724; }
#         .badge-offline { background: #f8d7da; color: #721c24; }
#         .badge-typing { background: #fff3cd; color: #856404; }
#         .badge-idle { background: #e2e3e5; color: #383d41; }
#         .status { padding: 10px; border-radius: 8px; margin-top: 10px; font-weight: 600; }
#         .status-success { background: #d4edda; color: #155724; }
#         .status-error { background: #f8d7da; color: #721c24; }
#         .user-text { padding: 8px; background: #f8f9fa; border-radius: 6px; font-size: 13px; color: #495057; font-style: italic; word-wrap: break-word; }
#         .user-text.empty { color: #999; }
#         @media (max-width: 768px) {
#             .stats { grid-template-columns: repeat(2, 1fr); }
#             table { font-size: 12px; }
#             td, th { padding: 10px; }
#         }
#     </style>
# </head>
# <body>
#     <div class="header">
#         <h1>🎬 Admin Dashboard</h1>
#         <p>Collaborative Subtitling Platform</p>
#     </div>
    
#     <div class="container">
#         <div class="upload-section">
#             <h2>Upload Video</h2>
#             <div class="upload-area" id="uploadArea">
#                 <p>📹 Drag and drop video file here or click to browse</p>
#                 <p style="color: #999; font-size: 14px; margin-top: 10px;">Supported formats: MP4, AVI, MOV, MKV</p>
#                 <input type="file" id="fileInput" accept="video/*">
#                 <button class="btn" onclick="document.getElementById('fileInput').click()">Select Video</button>
#             </div>
#             <div id="uploadStatus"></div>
#             <div id="currentVideo"></div>
#         </div>

#         <div class="stats">
#             <div class="stat-card"><h3>Total Users</h3><div class="value" id="totalUsers">0</div></div>
#             <div class="stat-card"><h3>Active Users</h3><div class="value" id="activeUsers">0</div></div>
#             <div class="stat-card"><h3>Typing Now</h3><div class="value" id="typingUsers">0</div></div>
#             <div class="stat-card"><h3>With Text</h3><div class="value" id="usersWithText">0</div></div>
#         </div>

#         <div class="content">
#             <h2>Connected Users & Subtitles <span class="live"></span></h2>
#             <table>
#                 <thead>
#                     <tr>
#                         <th>USERNAME</th>
#                         <th>STATUS</th>
#                         <th>ACTIVITY</th>
#                         <th>CURRENT TEXT</th>
#                         <th>LAST SEEN</th>
#                     </tr>
#                 </thead>
#                 <tbody id="usersBody">
#                     <tr><td colspan="5" style="text-align:center; padding:40px;">No users connected</td></tr>
#                 </tbody>
#             </table>
#         </div>
#     </div>
    
#     <script>
#         let ws;
#         let updatePending = false;
#         let latestData = null;
        
#         function connectWebSocket() {
#             // SAME PATH as your original code
#             ws = new WebSocket('ws://' + window.location.host + '/ws/admin');
            
#             ws.onopen = () => {
#                 console.log('WebSocket connected');
#             };
            
#             ws.onmessage = (e) => { 
#                 const d = JSON.parse(e.data);
#                 latestData = d;
                
#                 if (!updatePending) {
#                     updatePending = true;
#                     requestAnimationFrame(() => {
#                         update(latestData);
#                         updatePending = false;
#                     });
#                 }
#             };
            
#             ws.onerror = (error) => {
#                 console.error('WebSocket error:', error);
#             };
            
#             ws.onclose = () => {
#                 console.log('WebSocket closed, reconnecting...');
#                 setTimeout(connectWebSocket, 3000);
#             };
#         }
        
#         connectWebSocket();
#         fetch('/api/metrics').then(r => r.json()).then(update);
        
#         const uploadArea = document.getElementById('uploadArea');
#         const fileInput = document.getElementById('fileInput');
        
#         uploadArea.addEventListener('dragover', (e) => {
#             e.preventDefault();
#             uploadArea.classList.add('dragover');
#         });
        
#         uploadArea.addEventListener('dragleave', () => {
#             uploadArea.classList.remove('dragover');
#         });
        
#         uploadArea.addEventListener('drop', (e) => {
#             e.preventDefault();
#             uploadArea.classList.remove('dragover');
#             if (e.dataTransfer.files.length) {
#                 uploadFile(e.dataTransfer.files[0]);
#             }
#         });
        
#         fileInput.addEventListener('change', (e) => {
#             if (e.target.files.length) {
#                 uploadFile(e.target.files[0]);
#             }
#         });
        
#         async function uploadFile(file) {
#             const statusDiv = document.getElementById('uploadStatus');
#             statusDiv.innerHTML = '<div class="status">Uploading... Please wait</div>';
            
#             const formData = new FormData();
#             formData.append('file', file);
            
#             try {
#                 const response = await fetch('/api/upload-video', {
#                     method: 'POST',
#                     body: formData
#                 });
#                 const result = await response.json();
                
#                 if (response.ok) {
#                     statusDiv.innerHTML = '<div class="status status-success">✓ Video uploaded successfully!</div>';
#                     setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
#                 } else {
#                     statusDiv.innerHTML = '<div class="status status-error">✗ Upload failed: ' + result.detail + '</div>';
#                 }
#             } catch (error) {
#                 statusDiv.innerHTML = '<div class="status status-error">✗ Upload error: ' + error.message + '</div>';
#             }
#         }
        
#         function update(data) {
#             if (data.user_stats) {
#                 document.getElementById('totalUsers').textContent = data.user_stats.total;
#                 document.getElementById('activeUsers').textContent = data.user_stats.active;
#                 document.getElementById('typingUsers').textContent = data.user_stats.typing;
#                 document.getElementById('usersWithText').textContent = data.user_stats.with_text;
#             }
            
#             if (data.video) {
#                 const videoDiv = document.getElementById('currentVideo');
#                 videoDiv.innerHTML = `
#                     <div class="video-info">
#                         <strong>Current Video:</strong> ${data.video.filename}<br>
#                         <strong>Size:</strong> ${(data.video.size / 1024 / 1024).toFixed(2)} MB<br>
#                         <strong>Uploaded:</strong> ${data.video.upload_time}<br>
#                         <div class="video-preview">
#                             <video controls preload="metadata" playsinline style="max-width: 400px; width: 100%;">
#                                 <source src="${data.video.url}">
#                             </video>
#                         </div>
#                     </div>
#                 `;
#             }

#             if (data.users && data.users.length > 0) {
#                 const usersBody = document.getElementById('usersBody');
#                 usersBody.innerHTML = '';
#                 data.users.forEach(u => {
#                     const row = document.createElement('tr');
                    
#                     const hasText = u.current_text && u.current_text.length > 0;
#                     const textPreview = hasText 
#                         ? `<div class="user-text">"${escapeHtml(u.current_text)}"</div>` 
#                         : '<div class="user-text empty">No text yet...</div>';
                    
#                     row.innerHTML = `
#                         <td><strong>${escapeHtml(u.username)}</strong></td>
#                         <td><span class="badge badge-${u.status}">${u.status === 'online' ? '● Online' : '○ Offline'}</span></td>
#                         <td><span class="badge badge-${u.typing_status}">${u.typing_status === 'typing' ? '✍️ Typing...' : '⏸ Idle'}</span></td>
#                         <td>${textPreview}</td>
#                         <td>${escapeHtml(u.last_seen)}</td>
#                     `;
#                     usersBody.appendChild(row);
#                 });
#             } else {
#                 const usersBody = document.getElementById('usersBody');
#                 usersBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:40px;">No users connected</td></tr>';
#             }
#         }
        
#         function escapeHtml(text) {
#             const div = document.createElement('div');
#             div.textContent = text;
#             return div.innerHTML;
#         }
#     </script>
# </body>
# </html>
# """

# # ---------------- LOGIN HTML ----------------

# LOGIN_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
#     <title>Login - Subtitler Workspace</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
#         .login-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.2); max-width: 400px; width: 100%; }
#         .login-container h1 { text-align: center; color: #667eea; margin-bottom: 10px; }
#         .login-container p { text-align: center; color: #666; margin-bottom: 30px; }
#         .form-group { margin-bottom: 20px; }
#         .form-group label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; }
#         .form-group input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; }
#         .form-group input:focus { outline: none; border-color: #667eea; }
#         .btn { width: 100%; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 14px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; }
#         .btn:hover { opacity: 0.9; }
#         .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
#     </style>
# </head>
# <body>
#     <div class="login-container">
#         <h1>🎬 Subtitler Login</h1>
#         <p>Enter your username to access the workspace</p>
#         <form action="/client/login" method="POST">
#             <div class="form-group">
#                 <label for="username">Username</label>
#                 <input type="text" id="username" name="username" required minlength="3" placeholder="Enter your username">
#             </div>
#             <button type="submit" class="btn">Login</button>
#         </form>
#     </div>
# </body>
# </html>
# """

# # ---------------- CLIENT HTML ----------------

# CLIENT_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
#     <title>Subtitler Workspace</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body { font-family: Arial, sans-serif; background: #f0f2f5; }
#         .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; position: relative; }
#         .username-display { position: absolute; right: 20px; top: 20px; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; }
#         .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
#         .video-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
#         video { width: 100%; max-width: 100%; border-radius: 8px; background: #000; }
#         .info { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; }
#         .no-video { text-align: center; padding: 60px; color: #999; }
#         .live { display: inline-block; width: 10px; height: 10px; background: #28a745; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
#         @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
#         .error { color: #721c24; background: #f8d7da; padding: 15px; border-radius: 8px; margin-top: 15px; }
#         .subtitle-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
#         .subtitle-editor { width: 100%; min-height: 150px; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; font-family: Arial, sans-serif; resize: vertical; }
#         .subtitle-editor:focus { outline: none; border-color: #667eea; }
#         .char-count { margin-top: 10px; color: #666; font-size: 14px; }
#         .save-btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 15px; }
#         .save-btn:hover { opacity: 0.9; }
#     </style>
# </head>
# <body>
#     <div class="header">
#         <h1>🎬 Subtitler Workspace</h1>
#         <p>Access video for subtitling</p>
#         <div class="username-display">👤 <span id="username"></span></div>
#     </div>
    
#     <div class="container">
#         <div class="video-section">
#             <h2><span class="live"></span>Current Video</h2>
#             <div id="videoContainer">
#                 <div class="no-video">⏳ Waiting for admin to upload video...</div>
#             </div>
#         </div>

#         <div class="subtitle-section">
#             <h2>✍️ Subtitle Editor</h2>
#             <textarea id="subtitleEditor" class="subtitle-editor" placeholder="Start typing your subtitles here..."></textarea>
#             <div class="char-count">Characters: <span id="charCount">0</span></div>
#             <button class="save-btn" onclick="saveSubtitle()">💾 Save Subtitle</button>
#         </div>
#     </div>
    
#     <script>
#         const username = '__USERNAME__';
#         document.getElementById('username').textContent = username;
        
#         let ws;
#         let videoElement = null;
#         let lastVideoUrl = null;
#         let typingTimeout;
#         let sendTimeout;
#         let lastSendTime = 0;
#         const throttleDelay = 250; // Send updates max every 250ms
        
#         const editor = document.getElementById('subtitleEditor');
#         const charCount = document.getElementById('charCount');
        
#         function connectWebSocket() {
#             // SAME PATH as your original code
#             ws = new WebSocket('ws://' + window.location.host + '/ws/client/' + encodeURIComponent(username));
            
#             ws.onopen = () => {
#                 console.log('WebSocket connected');
#             };
            
#             ws.onmessage = (e) => { 
#                 const d = JSON.parse(e.data); 
#                 updateVideo(d); 
#             };
            
#             ws.onerror = (error) => {
#                 console.error('WebSocket error:', error);
#             };
            
#             ws.onclose = () => {
#                 console.log('WebSocket closed, reconnecting...');
#                 setTimeout(connectWebSocket, 3000);
#             };
#         }
        
#         connectWebSocket();
#         fetch('/api/metrics').then(r => r.json()).then(d => updateVideo(d));
        
#         // Throttled typing handler
#         editor.addEventListener('input', () => {
#             const text = editor.value;
#             charCount.textContent = text.length;
            
#             clearTimeout(typingTimeout);
#             clearTimeout(sendTimeout);
            
#             const now = Date.now();
#             const elapsed = now - lastSendTime;
            
#             if (elapsed >= throttleDelay) {
#                 sendUpdate('typing', text);
#                 lastSendTime = now;
#             } else {
#                 sendTimeout = setTimeout(() => {
#                     sendUpdate('typing', text);
#                     lastSendTime = Date.now();
#                 }, throttleDelay - elapsed);
#             }
            
#             // Set idle after 2 seconds
#             typingTimeout = setTimeout(() => {
#                 sendUpdate('idle', text);
#             }, 2000);
#         });
        
#         function sendUpdate(type, text) {
#             if (ws && ws.readyState === WebSocket.OPEN) {
#                 ws.send(JSON.stringify({ type: type, text: text }));
#             }
#         }
        
#         function saveSubtitle() {
#             const text = editor.value;
#             if (ws && ws.readyState === WebSocket.OPEN) {
#                 ws.send(JSON.stringify({ type: 'save', text: text }));
#                 alert('Subtitle saved successfully!');
#             }
#         }
        
#         function updateVideo(data) {
#             const container = document.getElementById('videoContainer');
#             if (data.video) {
#                 if (lastVideoUrl !== data.video.url) {
#                     lastVideoUrl = data.video.url;
#                     container.innerHTML = `
#                         <video controls preload="metadata" playsinline webkit-playsinline id="mainVideo">
#                             <source src="${data.video.url}" type="video/mp4">
#                             Your browser does not support the video tag.
#                         </video>
#                         <div class="info">
#                             <strong>Filename:</strong> ${data.video.filename}<br>
#                             <strong>Size:</strong> ${(data.video.size / 1024 / 1024).toFixed(2)} MB<br>
#                             <strong>Uploaded:</strong> ${data.video.upload_time}
#                         </div>
#                     `;
                    
#                     videoElement = document.getElementById('mainVideo');
#                     videoElement.addEventListener('error', function(e) {
#                         console.error('Video error:', e);
#                         container.innerHTML += '<div class="error">⚠️ Video failed to load. Make sure the video format is MP4 (H.264).</div>';
#                     });
                    
#                     videoElement.addEventListener('loadedmetadata', function() {
#                         console.log('Video loaded successfully');
#                     });
#                 }
#             } else if (lastVideoUrl !== null) {
#                 lastVideoUrl = null;
#                 container.innerHTML = '<div class="no-video">⏳ Waiting for admin to upload video...</div>';
#             }
#         }
#     </script>
# </body>
# </html>
# """

# # ---------------- ROUTES ----------------


# @router.get("/admin", response_class=HTMLResponse)
# async def admin_dashboard():
#     # If you want to keep pages.py "/" for subtitler, change this path to "/admin"
#     return HTMLResponse(ADMIN_HTML)


# @router.get("/client", response_class=HTMLResponse)
# async def client_login_page():
#     return HTMLResponse(LOGIN_HTML)


# @router.post("/client/login")
# async def client_login(username: str = Form(...)):
#     if not username or len(username) < 3:
#         return HTMLResponse(
#             LOGIN_HTML.replace(
#                 "</form>",
#                 '<div class="error">Username must be at least 3 characters</div></form>',
#             )
#         )

#     ds.connected_users[username] = ds.ConnectedUser(
#         username=username,
#         connected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         status="online",
#         last_seen=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         typing_status="idle",
#         current_text="",
#     )

#     return HTMLResponse(CLIENT_HTML.replace("__USERNAME__", username))


# @router.get("/api/metrics")
# async def get_metrics():
#     return {
#         "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
#         "summary": ds.get_summary(),
#         "video": ds.current_video.model_dump() if ds.current_video else None,
#         "users": [u.model_dump() for u in ds.connected_users.values()],
#         "user_stats": ds.get_user_stats(),
#     }


# @router.post("/api/upload-video")
# async def upload_video(file: UploadFile = File(...)):
#     allowed_types = [
#         "video/mp4",
#         "video/avi",
#         "video/quicktime",
#         "video/x-msvideo",
#         "video/x-matroska",
#         "video/webm",
#     ]
#     if file.content_type not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid file type. Only video files are allowed.",
#         )

#     os.makedirs("uploads", exist_ok=True)
#     file_path = os.path.join("uploads", file.filename)

#     try:
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         file_size = os.path.getsize(file_path)
#         video_url = f"/videos/{file.filename}"

#         ds.current_video = ds.VideoInfo(
#             filename=file.filename,
#             upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             size=file_size,
#             url=video_url,
#         )

#         data = {
#             "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
#             "summary": ds.get_summary(),
#             "video": ds.current_video.model_dump(),
#             "users": [u.model_dump() for u in ds.connected_users.values()],
#             "user_stats": ds.get_user_stats(),
#         }

#         for username, ws in list(ds.active_websockets.items()):
#             try:
#                 await ws.send_json(data)
#             except Exception:
#                 pass

#         return {"message": "Video uploaded successfully", "video": ds.current_video}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# @router.websocket("/ws/admin")
# async def websocket_admin(websocket: WebSocket):
#     await websocket.accept()
#     ds.active_websockets["admin"] = websocket

#     initial_data = {
#         "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
#         "summary": ds.get_summary(),
#         "video": ds.current_video.model_dump() if ds.current_video else None,
#         "users": [u.model_dump() for u in ds.connected_users.values()],
#         "user_stats": ds.get_user_stats(),
#     }
#     await websocket.send_json(initial_data)

#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         if "admin" in ds.active_websockets:
#             del ds.active_websockets["admin"]
#     except Exception as e:
#         print(f"Admin WebSocket error: {e}")
#         if "admin" in ds.active_websockets:
#             del ds.active_websockets["admin"]


# @router.websocket("/ws/client/{username}")
# async def websocket_client(websocket: WebSocket, username: str):
#     await websocket.accept()
#     ds.active_websockets[username] = websocket

#     if username in ds.connected_users:
#         ds.connected_users[username].status = "online"
#         ds.connected_users[username].last_seen = datetime.now().strftime(
#             "%Y-%m-%d %H:%M:%S"
#         )

#     initial_data = {
#         "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
#         "summary": ds.get_summary(),
#         "video": ds.current_video.model_dump() if ds.current_video else None,
#         "users": [u.model_dump() for u in ds.connected_users.values()],
#         "user_stats": ds.get_user_stats(),
#     }
#     await websocket.send_json(initial_data)

#     try:
#         while True:
#             message = await websocket.receive_text()
#             data = json.loads(message)

#             if username in ds.connected_users:
#                 if data["type"] == "typing":
#                     ds.connected_users[username].typing_status = "typing"
#                     ds.connected_users[username].current_text = data["text"]
#                 elif data["type"] == "idle":
#                     ds.connected_users[username].typing_status = "idle"
#                     ds.connected_users[username].current_text = data["text"]
#                 elif data["type"] == "save":
#                     ds.connected_users[username].current_text = data["text"]
#                     print(
#                         f"User {username} saved subtitle: {data['text'][:50]}..."
#                     )
#                 ds.connected_users[username].last_seen = datetime.now().strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 )

#                 await ds.broadcast_user_update()

#     except WebSocketDisconnect:
#         if username in ds.active_websockets:
#             del ds.active_websockets[username]
#         if username in ds.connected_users:
#             ds.connected_users[username].status = "offline"
#             ds.connected_users[username].typing_status = "idle"
#             ds.connected_users[username].last_seen = datetime.now().strftime(
#                 "%Y-%m-%d %H:%M:%S"
#             )
#             await ds.broadcast_user_update()
#     except Exception as e:
#         print(f"Client {username} WebSocket error: {e}")
#         if username in ds.active_websockets:
#             del ds.active_websockets[username]
#         if username in ds.connected_users:
#             ds.connected_users[username].status = "offline"
#             ds.connected_users[username].typing_status = "idle"
#             ds.connected_users[username].last_seen = datetime.now().strftime(
#                 "%Y-%m-%d %H:%M:%S"
#             )
#             await ds.broadcast_user_update()


from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    File,
    UploadFile,
    HTTPException,
    Form,
)
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import os
import shutil

import services.dashboard_state as ds

router = APIRouter()

# ---------------- ADMIN HTML (unchanged) ----------------

# ADMIN_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
#     <title>Admin Dashboard</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <!-- full CSS and HTML as in previous working version -->
#     <!-- ... omitted here for brevity, keep exactly as before ... -->
# </head>
# <body>
#     <!-- body content exactly as in previous working ADMIN_HTML -->
# </body>
# </html>
# """


ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; }
        .header h1 { font-size: 32px; margin-bottom: 8px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 14px; color: #666; text-transform: uppercase; margin-bottom: 10px; }
        .stat-card .value { font-size: 42px; font-weight: bold; color: #667eea; }
        .content { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .upload-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .upload-area { border: 2px dashed #667eea; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { background: #f8f9ff; border-color: #764ba2; }
        .upload-area.dragover { background: #e7f3ff; border-color: #667eea; }
        .btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 15px; }
        .btn:hover { opacity: 0.9; }
        #fileInput { display: none; }
        .video-info { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; }
        .video-preview { margin-top: 15px; }
        .video-preview video { width: 100%; max-width: 400px; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
        th { background: #f8f9fa; padding: 15px; text-align: left; font-size: 13px; color: #666; text-transform: uppercase; }
        td { padding: 15px; border-top: 1px solid #eee; vertical-align: top; }
        td:nth-child(1) { width: 15%; }
        td:nth-child(2) { width: 12%; }
        td:nth-child(3) { width: 12%; }
        td:nth-child(4) { width: 40%; }
        td:nth-child(5) { width: 21%; }
        .badge { display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }
        .badge-active { background: #d4edda; color: #155724; }
        .badge-inactive { background: #f8d7da; color: #721c24; }
        .badge-online { background: #d4edda; color: #155724; }
        .badge-offline { background: #f8d7da; color: #721c24; }
        .badge-typing { background: #fff3cd; color: #856404; }
        .badge-idle { background: #e2e3e5; color: #383d41; }
        .status { padding: 10px; border-radius: 8px; margin-top: 10px; font-weight: 600; }
        .status-success { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .user-text { padding: 8px; background: #f8f9fa; border-radius: 6px; font-size: 13px; color: #495057; font-style: italic; word-wrap: break-word; }
        .user-text.empty { color: #999; }
        @media (max-width: 768px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            table { font-size: 12px; }
            td, th { padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Admin Dashboard</h1>
        <p>Collaborative Subtitling Platform</p>
    </div>
    
    <div class="container">
        <div class="upload-section">
            <h2>Upload Video</h2>
            <div class="upload-area" id="uploadArea">
                <p>📹 Drag and drop video file here or click to browse</p>
                <p style="color: #999; font-size: 14px; margin-top: 10px;">Supported formats: MP4, AVI, MOV, MKV</p>
                <input type="file" id="fileInput" accept="video/*">
                <button class="btn" onclick="document.getElementById('fileInput').click()">Select Video</button>
            </div>
            <div id="uploadStatus"></div>
            <div id="currentVideo"></div>
        </div>

        <div class="stats">
            <div class="stat-card"><h3>Total Users</h3><div class="value" id="totalUsers">0</div></div>
            <div class="stat-card"><h3>Active Users</h3><div class="value" id="activeUsers">0</div></div>
            <div class="stat-card"><h3>Typing Now</h3><div class="value" id="typingUsers">0</div></div>
            <div class="stat-card"><h3>With Text</h3><div class="value" id="usersWithText">0</div></div>
        </div>

        <div class="content">
            <h2>Connected Users & Subtitles <span class="live"></span></h2>
            <table>
                <thead>
                    <tr>
                        <th>USERNAME</th>
                        <th>STATUS</th>
                        <th>ACTIVITY</th>
                        <th>CURRENT TEXT</th>
                        <th>LAST SEEN</th>
                    </tr>
                </thead>
                <tbody id="usersBody">
                    <tr><td colspan="5" style="text-align:center; padding:40px;">No users connected</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        let ws;
        let updatePending = false;
        let latestData = null;
        
        function connectWebSocket() {
            // SAME PATH as your original code
            ws = new WebSocket('ws://' + window.location.host + '/ws/admin');
            
            ws.onopen = () => {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = (e) => { 
                const d = JSON.parse(e.data);
                latestData = d;
                
                if (!updatePending) {
                    updatePending = true;
                    requestAnimationFrame(() => {
                        update(latestData);
                        updatePending = false;
                    });
                }
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = () => {
                console.log('WebSocket closed, reconnecting...');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        connectWebSocket();
        fetch('/api/metrics').then(r => r.json()).then(update);
        
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                uploadFile(e.dataTransfer.files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                uploadFile(e.target.files[0]);
            }
        });
        
        async function uploadFile(file) {
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.innerHTML = '<div class="status">Uploading... Please wait</div>';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/upload-video', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = '<div class="status status-success">✓ Video uploaded successfully!</div>';
                    setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
                } else {
                    statusDiv.innerHTML = '<div class="status status-error">✗ Upload failed: ' + result.detail + '</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status status-error">✗ Upload error: ' + error.message + '</div>';
            }
        }
        
        function update(data) {
            if (data.user_stats) {
                document.getElementById('totalUsers').textContent = data.user_stats.total;
                document.getElementById('activeUsers').textContent = data.user_stats.active;
                document.getElementById('typingUsers').textContent = data.user_stats.typing;
                document.getElementById('usersWithText').textContent = data.user_stats.with_text;
            }
            
            if (data.video) {
                const videoDiv = document.getElementById('currentVideo');
                videoDiv.innerHTML = `
                    <div class="video-info">
                        <strong>Current Video:</strong> ${data.video.filename}<br>
                        <strong>Size:</strong> ${(data.video.size / 1024 / 1024).toFixed(2)} MB<br>
                        <strong>Uploaded:</strong> ${data.video.upload_time}<br>
                        <div class="video-preview">
                            <video controls preload="metadata" playsinline style="max-width: 400px; width: 100%;">
                                <source src="${data.video.url}">
                            </video>
                        </div>
                    </div>
                `;
            }

            if (data.users && data.users.length > 0) {
                const usersBody = document.getElementById('usersBody');
                usersBody.innerHTML = '';
                data.users.forEach(u => {
                    const row = document.createElement('tr');
                    
                    const hasText = u.current_text && u.current_text.length > 0;
                    const textPreview = hasText 
                        ? `<div class="user-text">"${escapeHtml(u.current_text)}"</div>` 
                        : '<div class="user-text empty">No text yet...</div>';
                    
                    row.innerHTML = `
                        <td><strong>${escapeHtml(u.username)}</strong></td>
                        <td><span class="badge badge-${u.status}">${u.status === 'online' ? '● Online' : '○ Offline'}</span></td>
                        <td><span class="badge badge-${u.typing_status}">${u.typing_status === 'typing' ? '✍️ Typing...' : '⏸ Idle'}</span></td>
                        <td>${textPreview}</td>
                        <td>${escapeHtml(u.last_seen)}</td>
                    `;
                    usersBody.appendChild(row);
                });
            } else {
                const usersBody = document.getElementById('usersBody');
                usersBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:40px;">No users connected</td></tr>';
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""


# ---------------- LOGIN HTML (updated with password) ----------------

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - Subtitler Workspace</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.2); max-width: 400px; width: 100%; }
        .login-container h1 { text-align: center; color: #667eea; margin-bottom: 10px; }
        .login-container p { text-align: center; color: #666; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 14px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; }
        .btn:hover { opacity: 0.9; }
        .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🎬 Subtitler Login</h1>
        <p>Enter your credentials to access the workspace</p>
        <form action="/client/login" method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required minlength="3" placeholder="Enter your username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required minlength="3" placeholder="Enter your password">
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>
"""

# ---------------- CLIENT HTML (unchanged) ----------------

# CLIENT_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
#     <title>Subtitler Workspace</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <!-- full CSS and HTML as in previous working version -->
#     <!-- ... omitted here for brevity, keep exactly as before ... -->
# </head>
# <body>
#     <!-- body content exactly as in previous working CLIENT_HTML -->
# </body>
# </html>
# """



CLIENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Subtitler Workspace</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; position: relative; }
        .username-display { position: absolute; right: 20px; top: 20px; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .video-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        video { width: 100%; max-width: 100%; border-radius: 8px; background: #000; }
        .info { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; }
        .no-video { text-align: center; padding: 60px; color: #999; }
        .live { display: inline-block; width: 10px; height: 10px; background: #28a745; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        .error { color: #721c24; background: #f8d7da; padding: 15px; border-radius: 8px; margin-top: 15px; }
        .subtitle-section { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .subtitle-editor { width: 100%; min-height: 150px; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; font-family: Arial, sans-serif; resize: vertical; }
        .subtitle-editor:focus { outline: none; border-color: #667eea; }
        .char-count { margin-top: 10px; color: #666; font-size: 14px; }
        .save-btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 15px; }
        .save-btn:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Subtitler Workspace</h1>
        <p>Access video for subtitling</p>
        <div class="username-display">👤 <span id="username"></span></div>
    </div>
    
    <div class="container">
        <div class="video-section">
            <h2><span class="live"></span>Current Video</h2>
            <div id="videoContainer">
                <div class="no-video">⏳ Waiting for admin to upload video...</div>
            </div>
        </div>

        <div class="subtitle-section">
            <h2>✍️ Subtitle Editor</h2>
            <textarea id="subtitleEditor" class="subtitle-editor" placeholder="Start typing your subtitles here..."></textarea>
            <div class="char-count">Characters: <span id="charCount">0</span></div>
            <button class="save-btn" onclick="saveSubtitle()">💾 Save Subtitle</button>
        </div>
    </div>
    
    <script>
        const username = '__USERNAME__';
        document.getElementById('username').textContent = username;
        
        let ws;
        let videoElement = null;
        let lastVideoUrl = null;
        let typingTimeout;
        let sendTimeout;
        let lastSendTime = 0;
        const throttleDelay = 250; // Send updates max every 250ms
        
        const editor = document.getElementById('subtitleEditor');
        const charCount = document.getElementById('charCount');
        
        function connectWebSocket() {
            // SAME PATH as your original code
            ws = new WebSocket('ws://' + window.location.host + '/ws/client/' + encodeURIComponent(username));
            
            ws.onopen = () => {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = (e) => { 
                const d = JSON.parse(e.data); 
                updateVideo(d); 
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = () => {
                console.log('WebSocket closed, reconnecting...');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        connectWebSocket();
        fetch('/api/metrics').then(r => r.json()).then(d => updateVideo(d));
        
        // Throttled typing handler
        editor.addEventListener('input', () => {
            const text = editor.value;
            charCount.textContent = text.length;
            
            clearTimeout(typingTimeout);
            clearTimeout(sendTimeout);
            
            const now = Date.now();
            const elapsed = now - lastSendTime;
            
            if (elapsed >= throttleDelay) {
                sendUpdate('typing', text);
                lastSendTime = now;
            } else {
                sendTimeout = setTimeout(() => {
                    sendUpdate('typing', text);
                    lastSendTime = Date.now();
                }, throttleDelay - elapsed);
            }
            
            // Set idle after 2 seconds
            typingTimeout = setTimeout(() => {
                sendUpdate('idle', text);
            }, 2000);
        });
        
        function sendUpdate(type, text) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: type, text: text }));
            }
        }
        
        function saveSubtitle() {
            const text = editor.value;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'save', text: text }));
                alert('Subtitle saved successfully!');
            }
        }
        
        function updateVideo(data) {
            const container = document.getElementById('videoContainer');
            if (data.video) {
                if (lastVideoUrl !== data.video.url) {
                    lastVideoUrl = data.video.url;
                    container.innerHTML = `
                        <video controls preload="metadata" playsinline webkit-playsinline id="mainVideo">
                            <source src="${data.video.url}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                        <div class="info">
                            <strong>Filename:</strong> ${data.video.filename}<br>
                            <strong>Size:</strong> ${(data.video.size / 1024 / 1024).toFixed(2)} MB<br>
                            <strong>Uploaded:</strong> ${data.video.upload_time}
                        </div>
                    `;
                    
                    videoElement = document.getElementById('mainVideo');
                    videoElement.addEventListener('error', function(e) {
                        console.error('Video error:', e);
                        container.innerHTML += '<div class="error">⚠️ Video failed to load. Make sure the video format is MP4 (H.264).</div>';
                    });
                    
                    videoElement.addEventListener('loadedmetadata', function() {
                        console.log('Video loaded successfully');
                    });
                }
            } else if (lastVideoUrl !== null) {
                lastVideoUrl = null;
                container.innerHTML = '<div class="no-video">⏳ Waiting for admin to upload video...</div>';
            }
        }
    </script>
</body>
</html>
"""


# ---------------- ROUTES ----------------


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    # If you kept this as admin root, leave as-is.
    # If you want "/" to be existing subtitler.html, change this path to "/admin".
    return HTMLResponse(ADMIN_HTML)


@router.get("/client", response_class=HTMLResponse)
async def client_login_page():
    return HTMLResponse(LOGIN_HTML)


@router.post("/client/login")
async def client_login(
    username: str = Form(...),
    password: str = Form(...),
):
    # Load credentials from CSV
    creds = ds.load_user_credentials()

    # Basic validation: non-empty, length, and CSV match
    if not username or len(username) < 3:
        return HTMLResponse(
            LOGIN_HTML.replace(
                "</form>",
                '<div class="error">Username must be at least 3 characters</div></form>',
            )
        )

    expected_password = creds.get(username)
    if expected_password is None or expected_password != password:
        return HTMLResponse(
            LOGIN_HTML.replace(
                "</form>",
                '<div class="error">Invalid username or password</div></form>',
            )
        )

    ds.connected_users[username] = ds.ConnectedUser(
        username=username,
        connected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="online",
        last_seen=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        typing_status="idle",
        current_text="",
    )

    return HTMLResponse(CLIENT_HTML.replace("__USERNAME__", username))


@router.get("/api/metrics")
async def get_metrics():
    return {
        "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
        "summary": ds.get_summary(),
        "video": ds.current_video.model_dump() if ds.current_video else None,
        "users": [u.model_dump() for u in ds.connected_users.values()],
        "user_stats": ds.get_user_stats(),
    }


@router.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    allowed_types = [
        "video/mp4",
        "video/avi",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only video files are allowed.",
        )

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)
        video_url = f"/videos/{file.filename}"

        ds.current_video = ds.VideoInfo(
            filename=file.filename,
            upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            size=file_size,
            url=video_url,
        )

        data = {
            "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
            "summary": ds.get_summary(),
            "video": ds.current_video.model_dump(),
            "users": [u.model_dump() for u in ds.connected_users.values()],
            "user_stats": ds.get_user_stats(),
        }

        for username, ws in list(ds.active_websockets.items()):
            try:
                await ws.send_json(data)
            except Exception:
                pass

        return {"message": "Video uploaded successfully", "video": ds.current_video}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    await websocket.accept()
    ds.active_websockets["admin"] = websocket

    initial_data = {
        "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
        "summary": ds.get_summary(),
        "video": ds.current_video.model_dump() if ds.current_video else None,
        "users": [u.model_dump() for u in ds.connected_users.values()],
        "user_stats": ds.get_user_stats(),
    }
    await websocket.send_json(initial_data)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if "admin" in ds.active_websockets:
            del ds.active_websockets["admin"]
    except Exception as e:
        print(f"Admin WebSocket error: {e}")
        if "admin" in ds.active_websockets:
            del ds.active_websockets["admin"]


@router.websocket("/ws/client/{username}")
async def websocket_client(websocket: WebSocket, username: str):
    await websocket.accept()
    ds.active_websockets[username] = websocket

    if username in ds.connected_users:
        ds.connected_users[username].status = "online"
        ds.connected_users[username].last_seen = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    initial_data = {
        "subtitlers": [s.model_dump() for s in ds.subtitlers_db.values()],
        "summary": ds.get_summary(),
        "video": ds.current_video.model_dump() if ds.current_video else None,
        "users": [u.model_dump() for u in ds.connected_users.values()],
        "user_stats": ds.get_user_stats(),
    }
    await websocket.send_json(initial_data)

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if username in ds.connected_users:
                if data["type"] == "typing":
                    ds.connected_users[username].typing_status = "typing"
                    ds.connected_users[username].current_text = data["text"]
                elif data["type"] == "idle":
                    ds.connected_users[username].typing_status = "idle"
                    ds.connected_users[username].current_text = data["text"]
                elif data["type"] == "save":
                    ds.connected_users[username].current_text = data["text"]
                    print(
                        f"User {username} saved subtitle: {data['text'][:50]}..."
                    )
                ds.connected_users[username].last_seen = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                await ds.broadcast_user_update()

    except WebSocketDisconnect:
        if username in ds.active_websockets:
            del ds.active_websockets[username]
        if username in ds.connected_users:
            ds.connected_users[username].status = "offline"
            ds.connected_users[username].typing_status = "idle"
            ds.connected_users[username].last_seen = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await ds.broadcast_user_update()
    except Exception as e:
        print(f"Client {username} WebSocket error: {e}")
        if username in ds.active_websockets:
            del ds.active_websockets[username]
        if username in ds.connected_users:
            ds.connected_users[username].status = "offline"
            ds.connected_users[username].typing_status = "idle"
            ds.connected_users[username].last_seen = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await ds.broadcast_user_update()
