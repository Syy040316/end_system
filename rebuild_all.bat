@echo off
echo ==========================================
echo 重新构建所有服务...
echo ==========================================

echo.
echo 1. 停止所有服务...
docker-compose down

echo.
echo 2. 重新构建并启动...
docker-compose up -d --build

echo.
echo 3. 等待服务启动...
timeout /t 10 /nobreak

echo.
echo 4. 查看服务状态...
docker-compose ps

echo.
echo 5. 查看最新日志...
docker-compose logs --tail=50

echo.
echo ==========================================
echo 完成！访问 http://localhost:8080 查看前端
echo ==========================================
pause

