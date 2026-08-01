from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Spotify_AI_Interview_Guide.pdf"

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCN", parent=styles["Title"], fontName="STSong-Light", fontSize=23, leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#5B3CC4")))
styles.add(ParagraphStyle(name="HeadingCN", parent=styles["Heading2"], fontName="STSong-Light", fontSize=15, leading=21, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#30274A")))
styles.add(ParagraphStyle(name="BodyCN", parent=styles["BodyText"], fontName="STSong-Light", fontSize=9.5, leading=15, spaceAfter=6))
styles.add(ParagraphStyle(name="CodeCN", parent=styles["Code"], fontName="STSong-Light", fontSize=8.5, leading=13, backColor=colors.HexColor("#F3F0FA"), borderPadding=7, spaceAfter=8))


def paragraph(text, style="BodyCN"):
    return Paragraph(text.replace("\n", "<br/>"), styles[style])


def heading(text):
    return paragraph(text, "HeadingCN")


def bullet(text):
    return paragraph(f"- {text}")


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#766C8E"))
    canvas.drawString(1.7 * cm, 1.1 * cm, "Spotify AI Recommendation Platform - Interview Guide")
    canvas.drawRightString(19.3 * cm, 1.1 * cm, f"Page {document.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm, topMargin=1.55*cm, bottomMargin=1.7*cm)
    story = [Spacer(1, 0.8*cm), paragraph("Spotify AI Recommendation Platform", "TitleCN"), paragraph("面试代码与知识点复习手册", "TitleCN"), Spacer(1, 0.4*cm)]
    story += [paragraph("适用对象：项目作者 xiaozhihuang。内容基于本项目实际代码、数据集和架构，帮助你在软件工程实习面试中清楚解释设计选择、代码细节和可改进点。", "BodyCN")]
    story += [heading("1. 项目 30 秒介绍"), paragraph("这是一个全栈音乐推荐平台。React + TypeScript 负责仪表盘和交互；FastAPI 暴露 REST API；SQLAlchemy 连接 PostgreSQL；推荐引擎对 6,096 首歌曲的 8 个音频特征进行标准化，再使用余弦相似度生成 Top-10 个性化推荐。用户的 like/dislike 会保存到数据库并改变后续结果。Docker Compose 将前端、后端和数据库作为 3 个服务部署。")]
    story += [heading("2. 代码结构 - 需要会讲"), bullet("frontend/src/main.tsx：单页 React UI，负责调用 API、管理 profile/recommendations/favorites 状态，以及点赞和不感兴趣交互。"), bullet("app/main.py：FastAPI 路由层。接口包括 profile、recommendations、feedback、favorites、analytics 和健康检查。"), bullet("app/services/recommendation_engine.py：核心业务逻辑与 NumPy 相似度计算。"), bullet("app/models.py：User、UserInteraction、RecommendationHistory 三个 ORM 数据模型。"), bullet("app/schemas.py：Pydantic 请求/响应模型，用于输入校验和 OpenAPI 文档。"), bullet("docker-compose.yml：React、FastAPI、PostgreSQL 三服务编排。")]
    story += [heading("3. 前端面试知识点"), bullet("React state：useState 保存 profile、songs、favorites、analytics；状态变化触发重新渲染。"), bullet("useEffect：页面首次挂载时并行请求多个 API，避免手动刷新数据。"), bullet("异步请求：fetch 返回 Promise；检查 response.ok；失败时展示错误状态而非白屏。"), bullet("组件拆分：SongCard 负责单个歌曲卡片，Cover 负责封面；这样可以复用并减少重复 JSX。"), bullet("TypeScript：Profile、Song、Analytics 类型约束 API 数据结构，减少运行时字段错误。"), paragraph("常问：为什么用 React？回答：组件化、状态驱动 UI、生态成熟；本项目需要多个数据视图和交互，React 比手写 DOM 更可维护。")]
    story += [heading("4. 后端与 API 知识点"), bullet("REST 设计：GET 用于读取 profile/recommendations/favorites；POST /feedback 用于创建用户行为。"), bullet("Pydantic：FeedbackCreate 限制 user_id 必须大于 0，action 必须是 like 或 dislike。"), bullet("依赖注入：Depends(get_db) 为每个请求创建数据库 Session，并在 finally 中关闭。"), bullet("错误处理：前端检查非 2xx 响应；后端对无效 action 返回 422。"), bullet("CORS：允许 Vite 开发服务器 localhost:5173 访问 FastAPI。")]
    story += [heading("5. 推荐算法 - 高频重点"), paragraph("输入特征：danceability、energy、speechiness、acousticness、instrumentalness、liveness、valence、tempo，共 8 维。先计算每列均值 μ 和标准差 σ，标准化公式为 z = (x - μ) / σ。标准化非常重要，因为 tempo 的数值范围远大于 0-1 的 energy；不处理会让 tempo 主导相似度。")]
    story += [paragraph("余弦相似度：cos(a,b) = (a · b) / (||a|| ||b||)。值越接近 1，歌曲和用户偏好向量方向越相似。项目从用户 liked 歌曲求平均偏好向量；新用户没有 like 时使用确定性的 onboarding seed。之后按分数排序，过滤 dislike，取 Top-10。", "CodeCN")]
    story += [bullet("复杂度：当前每次推荐计算约 O(N×D)，N=6,096，D=8；小数据集足够快。大规模场景可预计算向量、使用 ANN 索引（FAISS/ScaNN）或缓存结果。"), bullet("局限：内容推荐容易让推荐范围变窄，无法发现用户未接触过但相似用户喜欢的歌曲；后续可加入 collaborative filtering 和 exploration。")]
    story += [PageBreak(), heading("6. 数据库与 SQLAlchemy"), bullet("users：用户基本信息。user_id 是主键。"), bullet("user_interactions：记录 song_id、like/dislike、时间戳；它是个性化反馈的来源。"), bullet("recommendation_history：记录展示过的歌曲与分数，便于分析、去重和审计。"), bullet("Foreign key：interaction/history 的 user_id 引用 users，保证数据关系完整性。"), bullet("Index：user_id 和 song_id 上的索引可以加快按用户查收藏、查历史和过滤 dislike 的查询。"), paragraph("常问：为什么 SQLAlchemy？回答：它把表映射为 Python 类，减少手写 SQL、支持多种数据库并能集中管理事务；高复杂度统计查询仍可使用原生 SQL。")]
    story += [heading("7. Docker 与部署"), bullet("backend.Dockerfile：基于 Python 镜像，安装 requirements，运行 uvicorn。"), bullet("frontend/Dockerfile：Node 构建 Vite 静态文件，再由 Nginx 提供服务。多阶段构建减少最终镜像体积。"), bullet("docker-compose.yml：db 使用 postgres:16-alpine，backend 依赖数据库 healthcheck，frontend 反向代理 API 请求。"), bullet("环境变量：DATABASE_URL 不写死在代码中；本地默认 SQLite，Docker 中使用 PostgreSQL 连接串。")]
    story += [heading("8. 面试问题与示范回答"), paragraph("Q: 点赞后推荐如何变化？\nA: POST /feedback 写入 UserInteraction。下一次 GET /recommendations 会读取 liked 歌曲形成偏好向量；dislike 歌曲会放入 excluded 集合并从排序结果过滤。"), paragraph("Q: 如何避免重复推荐？\nA: 当前项目记录 RecommendationHistory；下一步可将最近推荐 song_id 加入 excluded 集合，并设置时间窗口或衰减策略。"), paragraph("Q: 如果数据量增长到百万首歌？\nA: 特征向量离线标准化和持久化，使用向量数据库/ANN 检索候选集，再用精确 cosine rerank；把推荐计算移到异步任务，并缓存每个用户的结果。"), paragraph("Q: 如何测试？\nA: 为 engine 编写单元测试，验证标准化、过滤 dislike、Top-K 长度；用 FastAPI TestClient 测试 API 状态码和反馈写入；用 Playwright 测试点赞后收藏列表变化。")]
    story += [heading("9. 现场 coding 可能考什么"), bullet("实现 cosine_similarity(vec_a, vec_b)，处理零向量。"), bullet("给定 liked/disliked song IDs，返回不在 disliked 中的 Top-K 分数。"), bullet("用 SQL 查询每个用户最近 7 天最常互动的 genre。"), bullet("解释 list、set、dict：本项目用 set 做 dislike 过滤，平均 O(1) membership check。"), bullet("解释 HTTP 200/201/400/404/422/500 的含义，以及什么时候返回它们。")]
    story += [heading("10. 最后检查清单"), bullet("不要说使用了真实 Spotify 登录或真实用户行为；当前是本地演示账号和 CSV 数据集。"), bullet("所有量化数据可说：6,096 tracks、1,818 artists、8 audio features、6,096×8 matrix、Top-10、9 API endpoints、3 Docker services。"), bullet("准备打开 GitHub README、FastAPI /docs 和网页 demo；按“问题 - 设计 - 实现 - 结果 - 改进”顺序讲述。")]
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
    print(OUTPUT)
