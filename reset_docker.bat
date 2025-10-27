@echo off
echo ==========================================
echo 清理并重启招聘监控系统
echo ==========================================
echo.

echo 1. 停止所有容器...
docker-compose down

echo.
echo 2. 删除旧容器和数据卷...
docker-compose down -v

echo.
echo 3. 重新构建并启动服务...
docker-compose up -d --build --force-recreate

echo.
echo 4. 等待服务启动...
timeout /t 15 /nobreak

echo.
echo 5. 查看服务状态...
docker-compose ps

echo.
echo ==========================================
echo 重启完成！
echo ==========================================
echo.
echo 访问系统：
echo   - 前端: http://localhost:5173
echo   - 后端: http://localhost:5000
echo.
pause

