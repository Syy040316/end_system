"""
测试推送API的简单脚本
使用方法：python test_push_api.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_push_api():
    print("=" * 50)
    print("测试第三方推送API")
    print("=" * 50)
    
    # 1. 登录获取Token
    print("\n1. 登录获取Token...")
    login_data = {
        "username": "test_user",  # 修改为你的用户名
        "password": "password123"  # 修改为你的密码
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        response.raise_for_status()
        token = response.json()["data"]["access_token"]
        print(f"✓ 登录成功，Token: {token[:30]}...")
    except Exception as e:
        print(f"✗ 登录失败: {e}")
        print("请确保：")
        print("  1. 后端服务正在运行 (docker-compose ps)")
        print("  2. 用户名和密码正确")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 推送单个职位
    print("\n2. 测试推送单个职位...")
    job_data = {
        "job_id": f"test_job_{datetime.now().timestamp()}",
        "company": "测试科技有限公司",
        "position": "Python后端工程师",
        "description": "负责后端系统开发",
        "skills": ["Python", "Django", "PostgreSQL", "Redis"],
        "location": "北京",
        "salary_min": 25,
        "salary_max": 35,
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/jobs/push", headers=headers, json=job_data)
        response.raise_for_status()
        result = response.json()
        print(f"✓ 推送成功: {result['message']}")
        print(f"  Job ID: {result['data']['job_id']}")
        print(f"  是否新建: {result['data']['created']}")
    except Exception as e:
        print(f"✗ 推送失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应: {e.response.text}")
    
    # 3. 批量推送职位
    print("\n3. 测试批量推送职位...")
    batch_data = {
        "jobs": [
            {
                "job_id": f"batch_job_1_{datetime.now().timestamp()}",
                "company": "阿里巴巴",
                "position": "Java开发工程师",
                "skills": ["Java", "Spring Boot", "MySQL"],
                "location": "杭州",
                "salary_min": 30,
                "salary_max": 40,
                "status": "active"
            },
            {
                "job_id": f"batch_job_2_{datetime.now().timestamp()}",
                "company": "腾讯",
                "position": "前端工程师",
                "skills": ["Vue", "React", "TypeScript"],
                "location": "深圳",
                "salary_min": 25,
                "salary_max": 35,
                "status": "active"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/jobs/push/batch", headers=headers, json=batch_data)
        response.raise_for_status()
        result = response.json()
        print(f"✓ 批量推送完成: {result['message']}")
        print(f"  成功: {result['data']['success_count']}")
        print(f"  失败: {result['data']['failed_count']}")
        print(f"  总计: {result['data']['total']}")
    except Exception as e:
        print(f"✗ 批量推送失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应: {e.response.text}")
    
    # 4. 更新职位
    print("\n4. 测试更新职位...")
    update_data = {
        "salary_min": 28,
        "salary_max": 38,
        "description": "负责后端系统开发和架构设计"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/jobs/push/{job_data['job_id']}", 
            headers=headers, 
            json=update_data
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 更新成功: {result['message']}")
    except Exception as e:
        print(f"✗ 更新失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应: {e.response.text}")
    
    # 5. 下架职位
    print("\n5. 测试下架职位...")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v1/jobs/push/{job_data['job_id']}", 
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 下架成功: {result['message']}")
    except Exception as e:
        print(f"✗ 下架失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应: {e.response.text}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    print("\n提示：")
    print("  - 前往 http://localhost:8080 查看前端界面")
    print("  - 访问"招聘搜索"页面查看推送的职位")
    print("  - 访问"第三方数据接入"页面查看完整API文档")


if __name__ == "__main__":
    test_push_api()

