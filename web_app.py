import uvicorn
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from portfolio_server.sse import create_sse_app
from portfolio_server.data.storage import load_portfolio
from portfolio_server.tools.visualization_tools import visualize_portfolio

# 1. 继承原有的 SSE App (保留 MCP 功能)
app = create_sse_app()

# 2. 定义可视化的 API 接口 (适配前端需求)
async def api_get_portfolio(request):
    user_id = request.path_params['user_id']
    data = load_portfolio(user_id)
    return JSONResponse(data)

async def api_get_chart(request):
    user_id = request.path_params['user_id']
    # 调用现有的可视化工具生成图表
    image_obj = visualize_portfolio(user_id)
    return Response(content=image_obj.data, media_type="image/png")

# 3. 定义前端页面路由
async def serve_dashboard(request):
    return FileResponse('static/index.html')

# 4. 将新路由添加到应用中
app.routes.append(Route("/dashboard", serve_dashboard))  # 访问 /dashboard 查看界面
app.routes.append(Route("/api/portfolio/{user_id}", api_get_portfolio))
app.routes.append(Route("/api/chart/{user_id}", api_get_chart))

# 挂载静态文件目录 (可选，用于放 css/js)
# app.routes.append(Mount("/static", app=StaticFiles(directory="static"), name="static"))

if __name__ == "__main__":
    # 在 8082 端口启动，避免与纯 MCP 服务的 8081 冲突，或者直接替代
    uvicorn.run(app, host="0.0.0.0", port=8082)
