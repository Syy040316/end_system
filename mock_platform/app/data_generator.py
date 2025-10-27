"""
招聘数据生成器
使用Faker生成模拟招聘信息，支持增删改查和定时更新
"""
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Optional

fake = Faker('zh_CN')


class JobDataGenerator:
    """招聘数据生成器"""
    
    # 预定义数据
    COMPANIES = [
        "字节跳动", "阿里巴巴", "腾讯", "百度", "美团",
        "拼多多", "京东", "网易", "滴滴出行", "小米",
        "华为", "bilibili", "快手", "新浪", "搜狐",
        "携程", "去哪儿", "58同城", "知乎", "蚂蚁金服"
    ]
    
    POSITIONS = [
        "Python开发工程师", "Java开发工程师", "前端开发工程师",
        "后端开发工程师", "全栈开发工程师", "算法工程师",
        "数据分析师", "产品经理", "测试工程师", "运维工程师",
        "架构师", "技术总监", "项目经理", "UI设计师", "数据工程师"
    ]
    
    SKILLS = [
        "Python", "Java", "JavaScript", "Go", "C++",
        "React", "Vue", "Angular", "Node.js", "Spring Boot",
        "Django", "Flask", "MySQL", "PostgreSQL", "MongoDB",
        "Redis", "Kafka", "Docker", "Kubernetes", "AWS",
        "机器学习", "深度学习", "数据分析", "大数据", "微服务"
    ]
    
    CITIES = [
        "北京", "上海", "深圳", "杭州", "广州",
        "成都", "南京", "武汉", "西安", "苏州"
    ]
    
    EDUCATION_LEVELS = ["本科", "硕士", "博士", "大专", "不限"]
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.deleted_jobs: Dict[str, Dict] = {}
    
    def initialize_jobs(self, count: int = 500):
        """初始化招聘数据"""
        print(f"正在生成 {count} 条招聘信息...")
        
        for _ in range(count):
            job = self._generate_job()
            self.jobs[job['id']] = job
        
        print(f"成功生成 {len(self.jobs)} 条招聘信息")
    
    def _generate_job(self) -> Dict:
        """生成单条招聘信息"""
        job_id = str(uuid.uuid4())
        company = random.choice(self.COMPANIES)
        position = random.choice(self.POSITIONS)
        
        # 随机选择3-5个技能
        skills = random.sample(self.SKILLS, k=random.randint(3, 5))
        
        # 薪资范围（K为单位）
        salary_min = random.choice([8, 10, 15, 20, 25, 30, 35, 40])
        salary_max = salary_min + random.choice([5, 10, 15, 20])
        
        # 工作经验（年）
        experience = random.choice([0, 1, 2, 3, 5, 8, 10])
        
        # 发布时间（过去30天内随机）
        publish_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        return {
            "id": job_id,
            "company": company,
            "position": position,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "skills": skills,
            "experience_required": experience,
            "education_required": random.choice(self.EDUCATION_LEVELS),
            "location": random.choice(self.CITIES),
            "job_description": self._generate_job_description(position, skills, experience),
            "publish_date": publish_date.isoformat(),
            "update_date": publish_date.isoformat(),
            "status": "active",
            "view_count": random.randint(10, 1000)
        }
    
    def _generate_job_description(self, position: str, skills: List[str], experience: int) -> str:
        """生成岗位描述"""
        desc = f"""
【岗位职责】
1. 负责{position}相关工作
2. 参与系统架构设计和技术方案制定
3. 协同团队完成项目开发和优化
4. 解决技术难题，提升系统性能

【任职要求】
1. {experience}年以上相关工作经验
2. 熟练掌握 {', '.join(skills[:3])}
3. 了解 {', '.join(skills[3:])} 等技术
4. 良好的团队协作和沟通能力
5. 有大型项目经验者优先

【福利待遇】
- 五险一金，带薪年假
- 弹性工作制
- 技术培训机会
- 团队建设活动
        """.strip()
        
        return desc
    
    def random_update_jobs(self, update_ratio: float = 0.1):
        """随机更新部分招聘信息"""
        job_ids = list(self.jobs.keys())
        update_count = int(len(job_ids) * update_ratio)
        
        if update_count == 0:
            return
        
        jobs_to_update = random.sample(job_ids, update_count)
        
        for job_id in jobs_to_update:
            job = self.jobs[job_id]
            
            # 随机选择更新操作
            operation = random.choice([
                'salary',      # 薪资调整
                'status',      # 状态变更
                'description', # 描述修改
                'delete'       # 下架（5%概率）
            ])
            
            if operation == 'salary':
                # 薪资±10%
                adjustment = random.choice([-0.1, 0.1])
                job['salary_min'] = int(job['salary_min'] * (1 + adjustment))
                job['salary_max'] = int(job['salary_max'] * (1 + adjustment))
            
            elif operation == 'status':
                # 状态切换
                job['status'] = 'inactive' if job['status'] == 'active' else 'active'
            
            elif operation == 'description':
                # 描述微调
                job['job_description'] += f"\n\n【更新于{datetime.now().strftime('%Y-%m-%d')}】需求有所调整"
            
            elif operation == 'delete' and random.random() < 0.05:
                # 5%概率下架
                job['status'] = 'deleted'
                self.deleted_jobs[job_id] = job
                del self.jobs[job_id]
                continue
            
            job['update_date'] = datetime.now().isoformat()
        
        print(f"已更新 {len(jobs_to_update)} 条招聘信息")
    
    def add_new_jobs(self, count: int = 5):
        """新增招聘信息"""
        for _ in range(count):
            job = self._generate_job()
            self.jobs[job['id']] = job
        
        print(f"已新增 {count} 条招聘信息，当前总数: {len(self.jobs)}")
    
    def get_jobs(
        self,
        page: int = 1,
        per_page: int = 20,
        status: str = 'active',
        city: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """获取招聘列表（分页）"""
        jobs = list(self.jobs.values())
        
        # 过滤
        if status:
            jobs = [j for j in jobs if j['status'] == status]
        
        if city:
            jobs = [j for j in jobs if j['location'] == city]
        
        if keyword:
            keyword = keyword.lower()
            jobs = [
                j for j in jobs
                if keyword in j['position'].lower()
                or keyword in j['company'].lower()
                or any(keyword in skill.lower() for skill in j['skills'])
            ]
        
        # 排序（最新更新在前）
        jobs.sort(key=lambda x: x['update_date'], reverse=True)
        
        # 分页
        start = (page - 1) * per_page
        end = start + per_page
        
        return jobs[start:end]
    
    def count_jobs(
        self,
        status: str = 'active',
        city: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> int:
        """统计招聘数量"""
        jobs = list(self.jobs.values())
        
        if status:
            jobs = [j for j in jobs if j['status'] == status]
        
        if city:
            jobs = [j for j in jobs if j['location'] == city]
        
        if keyword:
            keyword = keyword.lower()
            jobs = [
                j for j in jobs
                if keyword in j['position'].lower()
                or keyword in j['company'].lower()
                or any(keyword in skill.lower() for skill in j['skills'])
            ]
        
        return len(jobs)
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """根据ID获取招聘详情"""
        return self.jobs.get(job_id)
    
    def search_jobs(
        self,
        keyword: str = '',
        skills: Optional[List[str]] = None,
        city: Optional[str] = None,
        salary_min: int = 0,
        salary_max: int = 999999
    ) -> List[Dict]:
        """搜索招聘信息"""
        jobs = list(self.jobs.values())
        
        # 只返回active状态
        jobs = [j for j in jobs if j['status'] == 'active']
        
        # 关键词过滤
        if keyword:
            keyword = keyword.lower()
            jobs = [
                j for j in jobs
                if keyword in j['position'].lower()
                or keyword in j['company'].lower()
                or any(keyword in skill.lower() for skill in j['skills'])
            ]
        
        # 技能过滤
        if skills:
            jobs = [
                j for j in jobs
                if any(skill in j['skills'] for skill in skills)
            ]
        
        # 城市过滤
        if city:
            jobs = [j for j in jobs if j['location'] == city]
        
        # 薪资过滤
        jobs = [
            j for j in jobs
            if j['salary_max'] >= salary_min and j['salary_min'] <= salary_max
        ]
        
        return jobs
    
    def get_updates_since(self, since: datetime) -> Dict:
        """获取指定时间后的更新"""
        updated_jobs = [
            j for j in self.jobs.values()
            if datetime.fromisoformat(j['update_date']) > since
        ]
        
        deleted_jobs = [
            j for j in self.deleted_jobs.values()
            if datetime.fromisoformat(j['update_date']) > since
        ]
        
        return {
            "updated": updated_jobs,
            "deleted": deleted_jobs,
            "count": {
                "updated": len(updated_jobs),
                "deleted": len(deleted_jobs)
            }
        }
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        active_jobs = [j for j in self.jobs.values() if j['status'] == 'active']
        inactive_jobs = [j for j in self.jobs.values() if j['status'] == 'inactive']
        
        return {
            "total": len(self.jobs),
            "active": len(active_jobs),
            "inactive": len(inactive_jobs),
            "deleted": len(self.deleted_jobs),
            "cities": list(set(j['location'] for j in active_jobs)),
            "companies": list(set(j['company'] for j in active_jobs)),
            "avg_salary": sum(j['salary_max'] for j in active_jobs) // len(active_jobs) if active_jobs else 0
        }

