# MindSpore GEO 优化 Issue 清单

> 来源: GEO Search Assessment 评分报告（suggestions.md）
> 生成时间: 2026-03-13
> 评估范围: 10个典型问题 × 4个主流AI搜索平台（ChatGPT、豆包、千问、DeepSeek）

---

## Issue #1: 官网活动页面和贡献指南页面采用SPA渲染，AI搜索引擎无法索引内容

**优先级**: P0
**标签**: `GEO-优化`, `基础设施`, `SSR`, `P0`

### 背景

MindSpore 官网（mindspore.cn）的活动页面（`/activities`）和贡献指南页面（`/contribution`）均使用 Nuxt.js 构建的单页应用（SPA）。SPA 页面的内容通过 JavaScript 在客户端动态渲染，HTML 源码中仅包含 Nuxt.js 的框架配置代码和空白容器，不包含任何实际业务内容。

AI 搜索平台（ChatGPT、豆包、千问、DeepSeek）的爬虫在抓取网页时，通常不会执行 JavaScript，因此无法获取 SPA 页面中的动态内容。这意味着 MindSpore 官网上的活动信息和贡献流程对 AI 搜索引擎完全不可见。

### 问题

1. **"MindSpore 2026年有哪些活动规划？"** — 由于活动页面内容不可索引，ChatGPT 的回答几乎无信息增量，仅给出泛泛的活动类型推测（评分C），引用中甚至出现了隐私政策页面（privacy/en）和 Facebook Huawei Kenya 帖子等完全不相关的链接。千问能回答出具体活动是因为从论坛等其他可索引来源获取了信息。
2. **"新手如何加入MindSpore社区参与贡献？"** — 虽然各平台整体表现尚可（依赖 GitHub 上的 CONTRIBUTING.md 等可索引内容），但贡献页面本身的详细流程、SIG组织信息等无法被引用，导致各平台对主仓库位置说法不一（GitHub/Gitee/AtomGit各有说法）。

### 影响范围

- 活动页面：影响全部AI平台对MindSpore社区活动信息的获取
- 贡献页面：影响全部AI平台对贡献流程、SIG组织、主仓库地址等信息的引用
- 潜在影响：官网其他SPA页面（如社区页面、文档页面等）可能存在同样的问题

### 改进措施

1. **将关键页面改为SSR（服务端渲染）或SSG（静态站点生成）**
   - 对 `/activities`、`/contribution` 页面启用 Nuxt.js 的 SSR 模式或使用 `nuxt generate` 进行静态预渲染
   - 确保 HTML 源码中直接包含页面的核心文本内容，不依赖客户端 JavaScript 渲染

2. **创建年度活动日历静态页面**
   - 新建 `/activities/2026` 静态页面，以纯 HTML 形式列出已确认活动和常规活动时间线
   - 包含活动名称、时间、参与方式、报名链接等结构化信息

3. **添加 `/sitemap.xml`**
   - 生成包含所有关键页面URL的 sitemap，提交到各搜索引擎
   - 确保 sitemap 中的页面内容可被直接抓取

4. **添加 SEO 元标签**
   - 为每个关键页面添加 `<meta name="description">`、`<meta name="robots" content="index,follow">`
   - 添加 OpenGraph 标签（`og:title`、`og:description`、`og:image`），提升在社交媒体和AI平台中的展示效果

5. **活动公告同步发布到可索引渠道**
   - 每次发布活动时，同步在 discuss.mindspore.cn 论坛（Discourse，可被爬虫索引）发布活动帖
   - 在 GitHub/Gitee 仓库的 Discussions 或 Wiki 中同步活动信息

6. **添加 Schema.org Event 结构化数据**
   - 为活动页面添加 JSON-LD 格式的 Schema.org Event 标记，帮助搜索引擎和AI平台理解活动的时间、地点、类型等结构化信息

---

## Issue #2: 缺少官方版本发布策略文档，AI平台对MindSpore发布节奏的描述严重失真

**优先级**: P0
**标签**: `GEO-优化`, `文档缺失`, `版本管理`, `P0`

### 背景

当用户通过 AI 搜索平台询问"MindSpore 的版本发布节奏是什么？"时，4个主流平台给出了4种不同的说法：

- ChatGPT 声称"每2-4个月发布一次"，引用了 GitLink 上2022年的旧仓库
- 豆包声称"每1-2个月发布一个主线版本"，并称"2.0是LTS版本（2024年发布，支持至2027年）"
- 千问声称"每2-3个月发布一个主要版本"，并称"2.3是LTS版本"
- DeepSeek 声称"月度发布"，并编造了一个完全不存在的规则："偶数版本为稳定版，奇数版本为开发版"

实际数据显示：MindSpore v2.2→v2.3 的间隔约为7个月（2023-10到2024-07），远非"每月"或"每2-3个月"。GitHub 上的 Releases 页面**完全为空**（只有 tags，最新到 v2.3.0），后续版本（2.4+）已迁移到其他平台但未提供迁移说明。

### 问题

1. **所有平台均在猜测发布频率**：由于没有官方策略文档，4个平台给出了4种不同的发布周期说法（月度/双月/2-4月/半年），没有一个与实际数据完全吻合
2. **LTS版本信息矛盾**：豆包说2.0是LTS，千问说2.3是LTS，MindSpore是否存在正式的LTS机制完全不明确
3. **DeepSeek编造了不存在的版本策略**：声称MindSpore采用"偶数为稳定版，奇数为开发版"的策略，这一规则从未在任何官方渠道出现
4. **GitHub Releases页面为空**：这是AI平台获取版本信息的重要来源，页面为空直接导致信息缺失
5. **仓库迁移无说明**：GitHub仅到v2.3.0，用户和AI平台无法找到后续版本的发布信息

### 影响范围

- 直接影响：所有用户通过AI搜索了解MindSpore版本状态时获得不准确信息
- 间接影响：错误的版本信息可能导致用户选择了不合适的版本进行开发或部署

### 改进措施

1. **发布官方版本发布策略文档**
   - 在 mindspore.cn 创建 `/version-policy` 或 `/releases` 页面（SSR渲染）
   - 内容应包含：
     - 版本号命名规则（主版本.次版本.补丁版本的含义）
     - 发布频率承诺（如"主版本约每X个月发布一次"）
     - LTS政策：是否存在LTS版本？如果有，哪些版本是LTS？维护周期多长？
     - 维护周期：每个版本的支持时间窗口
     - 版本选型建议：新用户推荐哪个版本？生产环境推荐哪个版本？

2. **在GitHub上正式使用Releases功能**
   - 为 v2.0.0 及之后的每个版本创建 GitHub Release
   - 每个 Release 包含：版本号、发布日期、核心特性摘要、完整 Changelog 链接、安装命令
   - 即使主仓库已迁移，也应在 GitHub 保留 Release 记录或添加重定向说明

3. **建立统一的版本历史页面**
   - 在 mindspore.cn 创建版本历史页面，按时间线列出所有已发布版本
   - 每个版本条目包含：版本号、发布日期、Release Notes 链接、下载链接
   - 用表格或时间线形式清晰展示版本演进

4. **在GitHub README中添加仓库迁移说明**
   - 明确说明当前主仓库位置（Gitee/AtomGit/其他）
   - 说明GitHub仓库的定位（镜像/归档/主仓库）
   - 提供指向当前活跃仓库和最新版本的链接

5. **明确LTS版本标记**
   - 如果存在LTS策略：在Release Notes中为LTS版本添加明确标记，在版本策略文档中说明LTS的选择标准和维护承诺
   - 如果不存在LTS策略：在文档中明确说明"MindSpore目前不采用LTS版本策略"，避免AI平台猜测

---

## Issue #3: FAQ中关于"MindSpore不支持直接读取其他框架模型"的表述力度不足，导致3/4平台传播严重错误信息

**优先级**: P0
**标签**: `GEO-优化`, `FAQ`, `模型格式`, `事实错误`, `P0`

### 背景

MindSpore 官方 FAQ（特性咨询页面）明确说明：
- MindSpore 采用 Protobuf 存储训练参数，**无法直接读取其他框架的模型**
- MindSpore 的 ckpt 和 TensorFlow 的 ckpt 虽然都用 Protobuf，但 proto 定义不同，**不通用**
- MindSpore **不支持导入 ONNX 格式，只支持导入 MINDIR**

然而，当用户询问"MindSpore目前支持读取哪些第三方框架的模型及格式？"时，4个主流AI平台中有3个给出了与官方完全矛盾的错误回答。

### 问题

1. **豆包（评分3/10，P0）**：声称存在 `mindspore.train.imports` 和 `mindspore.convert` 模块可以直接解析 PyTorch、TensorFlow、ONNX、Caffe 模型——**这些模块完全不存在**。声称"兼容TensorFlow/PyTorch的ckpt格式"直接与官方FAQ矛盾。给出了8个引用链接，但多个URL路径为编造。

2. **DeepSeek（评分3/10，P0）**：回答内容与豆包**高度雷同**（表格结构、文字几乎一致），同样声称可通过不存在的模块直接读取各框架模型，引用链接也与豆包完全一致。疑似两个平台共享了同一个错误知识源。

3. **ChatGPT（评分6/10，P2）**：虽未直接编造模块名，但暗示可通过 MindConverter 直接迁移模型，未充分强调"不能直接读取"这一关键限制，混淆了训练框架原生能力和 Lite 转换工具能力。

4. **仅千问正确回答**（评分9/10）：正确指出"不支持直接读取"，清晰区分了训练阶段（主框架，仅MINDIR）和推理阶段（Lite converter_lite）。

### 影响范围

- 这是本次评估中**错误率最高的问题**：75%的平台给出了不同程度的错误信息
- 错误后果严重：用户按照AI平台的指引尝试使用不存在的API或模块，将在运行时报错，浪费大量调试时间
- 豆包和DeepSeek的错误信息看起来权威详尽（含表格、代码示例），普通用户很难判断其为编造内容

### 改进措施

1. **在FAQ中用强调格式突出关键限制**
   - 使用告警框（admonition）或加粗红色文字明确标注：
     > **重要限制**：MindSpore **不支持** 直接读取 PyTorch（.pth/.pt）、TensorFlow（.ckpt/.pb）、Caffe（.caffemodel）或 ONNX（.onnx）格式的模型文件。
   - 列出明确的"不支持"操作清单，逐一说明原因

2. **创建独立的"模型迁移指南"页面**
   - 在 mindspore.cn 创建专门的模型迁移文档（SSR渲染，非SPA）
   - 内容结构：
     - **第一部分：MindSpore原生支持的格式**（.ckpt / .mindir）
     - **第二部分：训练迁移方案**（用其他框架API读取参数 → 参数名映射 → `save_checkpoint` 保存）
     - **第三部分：推理转换方案**（MindSpore Lite converter_lite 支持 ONNX/TF/Caffe → .ms）
     - **第四部分：常见误解澄清**（不能直接读取 ≠ 完全不兼容；converter_lite 仅限推理，不用于训练）
   - 每部分包含完整的代码示例，经过官方验证可运行

3. **明确区分"主框架能力"与"Lite转换工具能力"**
   - 当前FAQ未提及converter_lite，导致平台将Lite的转换能力错误归因为主框架的原生读取能力
   - 建议在FAQ中新增一条："如何将其他框架模型迁移到MindSpore？"，分别说明训练迁移和推理转换两条路径

4. **向AI平台提交错误信息反馈**
   - 通过豆包（火山引擎）、DeepSeek、ChatGPT的官方反馈渠道提交纠错请求
   - 在社区论坛、技术博客（CSDN/知乎/掘金）发布"MindSpore模型格式常见误解"文章，增强正确信息在互联网上的权重

5. **发布"MindSpore模型格式全景图"**
   - 以图文形式清晰展示 .ckpt / .mindir / .ms / .onnx 各格式的定位、用途和关系
   - 标注每种格式在训练/推理/导出/导入场景中的支持情况

---

## Issue #4: 缺少官方PyTorch→MindSpore迁移指南，导致多个AI平台大量编造不存在的迁移API

**优先级**: P0
**标签**: `GEO-优化`, `文档缺失`, `模型迁移`, `API编造`, `P0`

### 背景

PyTorch 到 MindSpore 的模型迁移是用户高频需求。当用户询问"我有一个PyTorch模型，应该如何转换为MindSpore模型？"时，正确的迁移路径应该是：
1. 使用 PyTorch API 读取模型参数（`torch.load`）
2. 逐层映射参数名（如 `running_mean` → `moving_mean`）
3. 使用 MindSpore 的 `save_checkpoint` 保存为 .ckpt 格式
4. 推理场景可另选 MindSpore Lite converter_lite（ONNX→.ms）

然而，当前 MindSpore 没有一个独立、完整、可被AI搜索引擎索引的迁移指南页面。迁移相关信息分散在 FAQ 的简短条目、API 映射表、华为云博客等多个位置。

### 问题

1. **ChatGPT（评分C，P0）**：推荐了错误的"官方推荐路径" `PyTorch→ONNX→MindSpore`，但官方FAQ明确说不支持导入ONNX用于训练。编造了不存在的 `ms.load("model.mindir")` API，将推理场景的Lite转换路径与训练场景混淆。零引用，完全没有官方来源支撑。

2. **豆包（评分B+，P1）**：权重迁移法基本正确，但使用了不标准的 `load_parameter_slice` API（正确应为 `load_param_into_net`）。ONNX方案中编造了 `onnx.onnx2mindir()` 和 `load_mindir()` 两个不存在的API。

3. **DeepSeek（评分D，P0）**：编造了大量不存在的API和工具：
   - `mindspore.convert.convert_pt_to_ms()`（该模块和函数完全不存在）
   - `ms.nn.GraphKernel().load_onnx()`（完全不存在）
   - `ms_converter --framework=PYTORCH`（不是标准用法）

4. **仅千问和Perplexity正确**：千问正确指出"没有一键自动转换工具"、"无法直接读取.pth"；Perplexity 明确指出"不能直接读取PyTorch的原生checkpoint"并提供了准确的4步迁移流程。

### 影响范围

- 3/5平台（60%）给出了包含编造API的错误迁移路径
- 用户按照这些错误指引操作，将遇到 `ModuleNotFoundError` 或 `AttributeError`，浪费大量调试时间
- PyTorch→MindSpore迁移是MindSpore获取新用户的关键路径，错误信息严重影响用户体验和社区增长

### 改进措施

1. **创建官方"PyTorch→MindSpore迁移指南"独立页面**
   - URL建议：`mindspore.cn/docs/zh-CN/stable/migration/pytorch_to_mindspore.html`
   - 使用SSR渲染，确保AI搜索引擎可索引
   - 页面结构：
     - 概述：MindSpore与PyTorch的核心差异（计算图、API命名、参数存储格式）
     - 方法一：训练迁移（网络结构重写 + 权重参数转换）— 含完整可运行代码
     - 方法二：推理转换（converter_lite：ONNX→.ms）— 含命令行示例
     - 常见问题：参数名映射规则、精度验证方法、常见报错排查

2. **提供官方验证的迁移脚本模板**
   - 发布一个经过官方测试的 Python 脚本，包含：
     ```
     torch.load() → 遍历参数 → 名称映射 → ms.Tensor转换 → save_checkpoint()
     ```
   - 脚本应覆盖常见网络结构（ResNet、BERT等）的参数名映射
   - 放置在官方仓库的 `examples/` 或 `tools/` 目录下

3. **发布"PyTorch↔MindSpore参数名映射表"**
   - 整理常见层类型的参数名对应关系：
     - `running_mean` → `moving_mean`
     - `running_var` → `moving_variance`
     - `weight` → `weight`（大部分一致）
     - `bias` → `bias`（大部分一致）
   - 以表格形式发布在迁移指南页面中

4. **在FAQ中强调"不支持ONNX导入用于训练"**
   - 多个平台推荐ONNX→MindSpore作为训练迁移路径，这是错误的
   - 在FAQ中明确说明：ONNX导入仅适用于MindSpore Lite推理场景，不可用于训练
   - 补充技术原因（IR不兼容、算子子集差异等）

---

## Issue #5: TransData算子FAQ内容过于简短且存在术语歧义，导致AI平台完全误解或无法回答

**优先级**: P0
**标签**: `GEO-优化`, `FAQ`, `TransData`, `术语歧义`, `P0`

### 背景

TransData 是 MindSpore/Ascend 生态中的一个重要底层算子，当网络中相互连接的算子使用的数据格式不一致时（如 NCHW 与 NC1HWC0），框架会自动插入 TransData 算子进行格式转换。在 Ascend 设备上，TransData 用于将数据从通用4D格式转换为华为Ascend支持的5D格式，以提升计算性能。

然而，MindSpore 官方 FAQ（算子API页面）对 TransData 的描述**仅有两句话**，既不包含性能优化方法，也不包含出现场景的技术解释。

### 问题

1. **豆包（评分1/10，P0 — 完全偏题）**：将 TransData 理解为大数据领域的 ETL 算子，全文讨论的是 CSV/JSON/Parquet 格式转换、字段映射、数据清洗等内容。引用了 FusionInsight HD、MaxCompute、Flink 文档，与 MindSpore/Ascend 的 TransData 算子毫无关系。
   - **根本原因**：「TransData」一词在大数据领域和 AI 框架领域有不同含义，FAQ 中缺乏足够的上下文让AI平台正确识别

2. **DeepSeek（评分0/10，P0 — 回答完全无关）**：输出了一段关于"如何复制DeepSeek回答内容"的使用指南，与 TransData 算子毫无关系。疑似平台对话上下文混乱或输入解析失败。

3. **ChatGPT（评分8/10，健康）**和**千问（评分8/10，健康）**均给出了正确回答，说明当AI平台具备正确的知识源时可以准确回答，但当前官方FAQ的信息量太少，无法帮助豆包和DeepSeek建立正确的上下文关联。

### 影响范围

- 2/4平台（50%）在该问题上完全失败（一个完全偏题，一个回答无关内容）
- TransData 是 Ascend 用户在性能调优（Profiler 分析）时的高频遭遇问题，信息缺失影响Ascend生态的用户体验

### 改进措施

1. **扩展FAQ中TransData的回答内容**
   - 当前仅两句话，建议扩展为包含：
     - **功能定义**："TransData 是 MindSpore/CANN 在 Ascend 设备上自动插入的数据格式转换算子"
     - **出现场景**：当相邻算子的数据格式不一致时（如 Conv2D 期望 NC1HWC0，而上游输出 NCHW）
     - **常见格式说明**：NCHW、NHWC、NC1HWC0、FracZ 等 Ascend 特有格式的含义
     - **性能影响**：TransData 是 Memory Bound 操作，不产生计算价值，过多 TransData 会拖慢训练/推理速度
     - **优化方法**：至少列出算子融合、冗余消除、统一格式布局规划 3-4 种方法

2. **在FAQ标题中消除术语歧义**
   - 当前标题可能仅为"TransData算子"，建议改为：
     > "TransData — MindSpore/Ascend 数据格式转换算子的功能与性能优化"
   - 标题中包含 "MindSpore" 和 "Ascend" 关键词，帮助AI平台正确识别问题的领域上下文

3. **创建TransData专题技术文档**
   - 独立页面，内容包含：
     - Ascend 数据格式体系（NCHW/NHWC/NC1HWC0/FracZ/ND_RNN_BIAS等）
     - TransData 在计算图中的自动插入机制（附图）
     - 使用 MindSpore Profiler 定位 TransData 算子的方法（附截图和命令）
     - 减少 TransData 的实践指南（统一输入格式、选择合适的数据预处理layout）
   - 在FAQ中添加指向该专题文档的链接

4. **向豆包和DeepSeek提交反馈**
   - 豆包的偏题回答和DeepSeek的无关回答属于平台层面的知识缺陷
   - 建议通过社区内容发布（技术博客、论坛帖子）增强正确信息在互联网上的权重

---

## Issue #6: 版本发布信息分散，缺乏统一的版本特性综述页面，AI平台对新版本特性描述出现大规模编造

**优先级**: P0
**标签**: `GEO-优化`, `文档缺失`, `版本特性`, `信息编造`, `P0`

### 背景

MindSpore 2.8.0 的版本信息分散在多个独立来源中：
- 主框架 Release Notes（mindspore.cn/docs）
- MindSpore Lite Release Notes（mindspore.cn/lite/docs）
- 昇腾社区发布文章（hiascend.com）
- 各子模块的独立 Changelog

当用户询问"MindSpore 2.8.0版本有哪些最新特性？"时，AI平台需要从多个分散的来源拼凑信息。这导致了严重的信息失真问题。

### 问题

1. **豆包（评分C，P0 — 大规模编造）**：以权威口吻描述了大量完全不存在的 MindSpore 2.8.0 特性，包括：
   - "分层张量并行（Hierarchical Tensor Parallelism）"（不存在）
   - "动态显存复用"（不存在）
   - "INT4/INT8混合精度推理延迟降低40%"（不存在）
   - "Android 15/iOS 18原生适配"（不存在）
   - "VS Code插件MindSpore Assistant"（不存在）
   - "AI for Science专用算子"（不存在）
   - "支持导入PyTorch 2.4+版本的.pth模型，迁移成功率95%"（与官方FAQ直接矛盾）
   - 多个引用URL为编造路径（如 `release_notes/2.8.0.html`，实际路径是 `RELEASE.html`）

2. **ChatGPT（评分B+，P2）**：内容准确但仅覆盖了 MindSpore Lite 部分特性（LoRA权重更新、ACL推理、Python 3.12），完全缺少主框架的重大特性（HyperParallel架构、SGLang推理引擎、vLLM适配等）。

3. **千问（评分A，健康）**：最准确最全面，正确描述了HyperParallel架构（HyperShard/HyperOffload/HyperMPMD）、SGLang/vLLM推理适配、Dataset DataLoader等实际特性。其成功原因是同时引用了官方Release Notes和昇腾社区发布文章。

### 影响范围

- 豆包的编造内容看起来权威详尽，普通用户无法辨别真假，可能基于不存在的特性做出技术决策
- 不完整的版本特性介绍（如ChatGPT仅覆盖Lite）可能让用户错过重要的框架能力更新

### 改进措施

1. **为每个大版本创建"What's New in MindSpore X.Y"综述页面**
   - URL建议：`mindspore.cn/whatsnew/2.8.0`
   - 整合主框架、Lite、各子模块的特性到一个统一页面
   - 页面顶部放置3-5个亮点特性的简明摘要（带视觉化标注）

2. **在Release Notes中增加"亮点特性"摘要section**
   - 当前Release Notes以技术变更列表为主，AI平台难以提取"最重要的N个特性"
   - 建议在页面顶部添加结构化的亮点摘要：
     ```
     ## 亮点特性
     1. HyperParallel架构：声明式并行 + 多级卸载 + 异构并行
     2. 推理引擎：支持SGLang，升级适配vLLM v0.11.0
     3. 科学计算：支持Protenix蛋白质结构预测
     ```

3. **每次版本发布时同步在mindspore.cn博客区发布特性解读文章**
   - 千问的优势来自于昇腾社区的发布文章，说明博客类内容对AI平台的信息获取非常重要
   - 建议在 mindspore.cn 官网博客、discuss.mindspore.cn 论坛、技术媒体（CSDN/知乎/掘金）同步发布

4. **统一Release Notes的URL模式**
   - 豆包编造了 `release_notes/2.8.0.html`（实际是 `RELEASE.html`）
   - 考虑更直观、可预测的URL结构（如 `/release-notes/2.8.0`），方便AI平台推断URL
   - 为旧路径设置301重定向

5. **在Release Notes页面添加版本对比入口**
   - 添加"相比上一版本的变化"链接或diff视图
   - 帮助AI平台理解版本间的增量变化

---

## Issue #7: 各AI平台对MindSpore主仓库位置说法不一，贡献指南中CLA签署入口不统一

**优先级**: P1
**标签**: `GEO-优化`, `贡献指南`, `仓库地址`, `CLA`, `P1`

### 背景

当用户询问"新手如何加入MindSpore社区参与贡献？"时，各AI平台对MindSpore主仓库位置给出了不同的说法：
- Perplexity 引用了 GitHub 上的 CONTRIBUTING_CN.md
- 豆包提到 AtomGit 为主仓库
- 千问提到 Gitee 为代码托管平台
- DeepSeek 的CLA签署链接指向了 openEuler 的CLA系统（clasign.osinfra.cn）

### 问题

1. **主仓库位置不明确**：用户无法确定应该在 GitHub、Gitee 还是 AtomGit 上提交PR和Issue
2. **CLA签署入口不统一**：DeepSeek引用了openEuler的CLA系统，Perplexity引用了GitHub的cla-assistant，新手无法确定正确的签署渠道
3. **贡献指南页面为SPA**：官方贡献页面（mindspore.cn/contribution）无法被AI平台索引，各平台只能从GitHub的CONTRIBUTING.md等散落文件获取信息

### 影响范围

- 影响所有希望参与MindSpore开源贡献的新手
- 错误的CLA签署链接可能导致新手签署了错误项目的CLA，或在签署流程中受阻放弃贡献

### 改进措施

1. **在官网、GitHub README、贡献指南中统一标注当前主仓库地址**
   - 明确声明："MindSpore的主仓库位于 [具体地址]，欢迎在此提交Issue和PR"
   - 如果存在多个镜像仓库，说明各仓库的定位（主仓库/镜像/归档）

2. **在贡献指南中提供唯一权威的CLA签署链接**
   - 明确标注CLA签署的唯一入口URL
   - 说明CLA签署的完整流程（包括签署后的生效时间和验证方式）

3. **创建"新手贡献快速入门"静态页面**
   - 用纯HTML实现（非SPA），确保可被AI平台索引
   - 内容包含：CLA签署链接 → 主仓库地址 → good first issue筛选链接 → Fork/PR流程图 → Code Review规范
   - 放置在容易被发现的位置（如 mindspore.cn/contributing）

4. **在GitHub/Gitee README中添加"如何贡献"section**
   - AI平台优先索引README内容
   - 添加简明的贡献快速入门步骤（5步以内）
   - 包含指向完整贡献指南的链接

---

## Issue #8: FAQ中PyNative模式和Graph模式的对比说明不充分，默认模式信息缺失导致平台回答矛盾

**优先级**: P1
**标签**: `GEO-优化`, `FAQ`, `执行模式`, `信息缺失`, `P1`

### 背景

MindSpore 支持两种执行模式：PyNative（动态图）和 Graph（静态图）。当用户询问"MindSpore的PyNative模式和Graph模式该怎么选？"时，官方FAQ仅提供了3个简要点（精度一致但性能不同、调试能力差异、语法支持差异），内容深度明显不足。

### 问题

1. **默认模式信息矛盾**：千问声称"MindSpore 2.0及以上版本默认启用Graph模式"，DeepSeek声称"PyNative是MindSpore的默认模式"。官方FAQ**未明确说明默认模式是哪个**，导致两个平台给出了互相矛盾的信息。

2. **混合模式未被提及**：豆包是唯一提到 `@ms.jit` 混合模式（PyNative + 局部静态图）的平台，但这恰恰是实际开发中最常用的方案。官方FAQ完全未提及混合模式。

3. **引用版本混乱**：ChatGPT引用了r1.3/r1.5的旧版文档，DeepSeek完全零引用。各平台引用的MindSpore版本跨度从r1.3到r2.4.0，说明缺乏一个canonical URL引导平台引用最新版本。

### 影响范围

- "默认模式"是用户在项目初始化时需要做出的第一个关键决策，错误信息会影响项目的开发效率
- 混合模式的缺失导致用户可能在"纯PyNative"和"纯Graph"之间二选一，而忽略了最优的混合方案

### 改进措施

1. **在FAQ中明确声明默认执行模式**
   - 添加一句明确声明："MindSpore X.Y 版本默认使用 [PyNative/Graph] 模式，可通过 `ms.set_context(mode=ms.PYNATIVE_MODE)` 或 `ms.set_context(mode=ms.GRAPH_MODE)` 切换"

2. **补充混合模式（@ms.jit）的说明**
   - 在FAQ中新增"混合模式"选项的说明
   - 内容：何时使用混合模式、`@ms.jit` 装饰器的用法、性能对比
   - 提供简单的代码示例

3. **扩展FAQ为完整的"执行模式选择指南"**
   - 当前FAQ回答过于简洁（仅3个要点），建议扩展为：
     - 对比表（PyNative vs Graph vs 混合模式，维度：性能/调试/语法/适用场景）
     - 选择决策树（开发阶段→PyNative，生产部署→Graph，兼顾→混合）
     - 代码示例（各模式的设置方法和典型用法）

4. **添加版本标注和canonical URL**
   - 在FAQ页面顶部标注适用版本范围（如"适用于MindSpore 2.0+"）
   - 在 `<head>` 中添加 `<link rel="canonical">` 标签指向 stable 版本URL

---

## Issue #9: 多卡训练数据分片的官方FAQ内容过于简短（r1.2版本），与AI平台回答的信息量差距过大

**优先级**: P1
**标签**: `GEO-优化`, `FAQ`, `分布式训练`, `文档过时`, `P1`

### 背景

当用户询问"MindSpore多卡训练时如何给不同NPU分配不同数据分片？"时，所有4个AI平台都给出了基本正确的回答（核心知识点 `num_shards`/`shard_id` 一致）。然而，各平台的回答内容远比官方FAQ丰富得多。

当前官方FAQ（来自r1.2版本，2021年）仅包含两行代码示例（`GeneratorDataset(..., num_shards=8, shard_id=0)`），没有任何上下文说明、初始化流程或注意事项。

### 问题

1. **官方FAQ版本过旧（r1.2，2021年）**：内容仅有两行代码和一句解释，未涵盖后续版本新增的 `dataset.shard()` 方法等内容
2. **AI平台回答的信息量远超官方**：
   - 千问提供了完整的单机8卡训练代码、分片原理说明（交错分片 vs 连续分片）、启动方式对比
   - 豆包提供了进阶优化section（分片前打乱、自定义分片、随机种子一致性）
   - DeepSeek提到了 `DistributedSampler` 方法和多机多卡环境变量说明
3. **`DistributedSampler` API存在性未验证**：DeepSeek提到的 `ds.DistributedSampler` 是否存在需要确认，如果存在则需要更好地文档化

### 影响范围

- 官方FAQ信息量不足本身不会导致AI平台出错（本题各平台表现均可），但会削弱官方作为"权威来源"的地位
- 用户在官方FAQ中找不到详细指导，转而依赖AI平台的回答，增加了接触错误信息的风险

### 改进措施

1. **更新FAQ中数据分片的回答内容**
   - 从r1.2版本更新到最新版本
   - 扩展为包含：
     - 完整初始化流程（`init()` → `set_auto_parallel_context()` → 数据分片 → 训练循环）
     - `GeneratorDataset` 构造函数参数方式和 `dataset.shard()` 方法两种方式
     - 完整的可运行代码示例（单机8卡Ascend场景）
     - 常见注意事项（num_shards必须等于设备数、shuffle顺序、batch size含义等）

2. **创建"分布式训练快速入门"专题页面**
   - 一站式指南，整合数据分片 + 通信初始化 + 启动方式
   - 包含不同场景的启动命令（mpirun vs launch工具 vs 环境变量方式）
   - 提供可直接复制运行的训练脚本模板

3. **验证并文档化 `DistributedSampler` API**
   - 确认 `ds.DistributedSampler` 是否为有效API
   - 如果存在：在API文档和FAQ中说明其用法和与 `num_shards/shard_id` 的关系
   - 如果不存在：在FAQ中说明替代方案

---

## Issue #10: FAQ页面缺乏结构化标记和锚点ID，AI平台引用精准度低且版本混乱

**优先级**: P2
**标签**: `GEO-优化`, `SEO`, `结构化数据`, `canonical-URL`, `P2`

### 背景

MindSpore 的FAQ页面（如 `faq/feature_advice.html`、`faq/operators_api.html`）以纯文本Q&A形式呈现，多个FAQ条目排列在同一个长页面中。当AI平台需要引用某个特定FAQ回答时，无法指向精确位置，只能引用整个页面URL。

### 问题

1. **缺乏锚点ID**：FAQ中每个问题没有独立的锚点（如 `#pynative-vs-graph`），AI平台无法精确引用到具体FAQ条目
2. **缺乏Schema.org结构化数据**：页面未使用 FAQPage JSON-LD 标记，搜索引擎和AI平台无法以结构化方式理解页面内容
3. **版本引用混乱**：各AI平台引用的FAQ版本从r1.2到r2.5.0不等（ChatGPT引用r1.3/r1.5，豆包引用r2.3，千问引用r2.2.0），缺乏canonical URL引导
4. **缺乏 `<meta name="description">`**：FAQ页面没有针对性的元描述标签

### 影响范围

- 影响所有FAQ相关问题（PyNative/Graph模式选择、模型格式支持、TransData算子等）的引用精准度
- 版本混乱导致用户可能被引导到过时的文档版本

### 改进措施

1. **为每个FAQ条目添加独立锚点ID**
   - 使用语义化的ID：`#pynative-vs-graph`、`#model-format-support`、`#transdata-operator`
   - 使用 `<h2>` 或 `<h3>` 标签包裹每个FAQ标题

2. **添加Schema.org FAQPage结构化数据**
   ```json
   {
     "@context": "https://schema.org",
     "@type": "FAQPage",
     "mainEntity": [{
       "@type": "Question",
       "name": "MindSpore的PyNative模式和Graph模式该怎么选？",
       "acceptedAnswer": {
         "@type": "Answer",
         "text": "..."
       }
     }]
   }
   ```

3. **建立Canonical URL策略**
   - 在每个FAQ页面的 `<head>` 中添加 `<link rel="canonical" href="https://www.mindspore.cn/docs/zh-CN/stable/faq/...">`
   - 确保 `stable` 版本始终指向最新稳定版
   - 旧版本URL（r1.2、r2.2.0等）通过 `<link rel="canonical">` 指向stable版本

4. **添加页面级元描述**
   - 为每个FAQ页面添加 `<meta name="description">` 标签
   - 内容应包含该页面涵盖的主要FAQ主题关键词

---

## Issue #11: 安装页面缺少pip包名变更说明和安装方式对比表

**优先级**: P2
**标签**: `GEO-优化`, `安装文档`, `用户体验`, `P2`

### 背景

"MindSpore支持哪些安装方式？"是所有10个评估问题中AI平台表现最好的一题（4个平台全部为D级健康状态，平均得分8.6/10）。这证明了**官方文档质量直接决定AI平台回答质量**。

然而，即便在这个表现最好的问题上，仍然存在一些可以优化的细节。

### 问题

1. **pip包名变更未说明**：MindSpore从早期的 `mindspore-gpu`/`mindspore-cpu` 分包方式演变为统一的 `mindspore` 包（2.x版本后）。ChatGPT仍在推荐 `pip install mindspore-gpu` 这种过时的包名格式，豆包使用了 `mindspore-gpu==2.8.0 cudatoolkit=11.6` 的错误命令格式（cudatoolkit不是pip参数）。
2. **缺少安装方式对比表**：所有4个平台都自行生成了安装方式对比表（pip vs conda vs Docker vs 源码），说明用户对此有强烈需求，但官方安装页面没有提供。
3. **CANN/MindSpore版本配套信息不够醒目**：千问提到的CANN版本配套问题是Ascend用户最常见的安装障碍，但安装页面中配套表的位置不够醒目。

### 改进措施

1. **在安装页面添加"包名变更说明"**
   - 明确说明从 `mindspore-gpu`/`mindspore-cpu` 到统一 `mindspore` 包的变更时间和原因
   - 提供当前推荐的安装命令

2. **在安装页面顶部添加安装方式简明对比表**
   - 对比维度：适用场景、难度、前置条件、推荐程度
   - 帮助新用户快速选择最适合的安装方式

3. **在安装页面醒目位置放置CANN/MindSpore版本配套表链接**
   - 或直接在安装页面内嵌版本配套表
   - 强调"MindSpore版本需与CANN版本严格对应"

---

## Issue #12: 缺少"MindSpore模型格式全景图"，用户和AI平台无法正确理解各格式的定位和关系

**优先级**: P2
**标签**: `GEO-优化`, `技术文档`, `模型格式`, `P2`

### 背景

MindSpore 生态中涉及多种模型文件格式：`.ckpt`（训练checkpoint）、`.mindir`（MindSpore IR，可用于跨平台部署）、`.ms`（MindSpore Lite推理模型）、`.onnx`（导出格式，有2G限制）。此外还涉及其他框架的格式：`.pth/.pt`（PyTorch）、`.pb`（TensorFlow）、`.caffemodel`（Caffe）。

在"MindSpore支持读取哪些第三方框架模型及格式"和"PyTorch模型如何转换为MindSpore模型"两个问题中，多个AI平台混淆了各格式的定位和相互关系，导致了大量错误回答。

### 问题

1. 平台将 MindSpore Lite converter_lite 的转换能力（推理场景）错误归因为主框架的原生读取能力（训练场景）
2. 平台将 ONNX 导出能力误解为 ONNX 导入能力（MindSpore不支持导入ONNX，只支持导出和通过Lite转换）
3. 不同格式在训练/推理/导出/导入场景中的适用范围不清晰

### 改进措施

1. **发布"MindSpore模型格式全景图"技术文档或博文**
   - 以图文并茂的方式展示各格式的定位、用途和转换关系
   - 核心内容：
     ```
     训练阶段：.ckpt（保存/加载checkpoint）
     导出阶段：.mindir（MindSpore IR）/ .onnx（有2G限制）
     推理部署：.mindir → 直接推理 / .onnx → converter_lite → .ms → Lite推理
     跨框架迁移：其他框架参数 → 手动映射 → save_checkpoint → .ckpt
     ```
   - 明确标注"不支持"的路径（如：不能直接读取.pth/.pt/.pb/.caffemodel）

2. **在FAQ和迁移指南中引用该全景图**
   - 将全景图链接到所有相关的FAQ条目和迁移文档中
   - 帮助用户在遇到格式问题时快速找到正确答案

---

## Issue #13: 建立季度性AI平台回答质量监控机制

**优先级**: P2
**标签**: `GEO-优化`, `持续监控`, `流程`, `P2`

### 背景

本次GEO评估发现，不同AI平台对MindSpore的回答质量差异巨大（千问评级A vs DeepSeek评级C+），且同一平台在不同问题上的表现也极不稳定（DeepSeek在"v2.8.0新特性"上评分A-，但在"TransData算子"上评分0/10）。

AI平台的知识库会定期更新，当前的错误可能在未来被修正，但也可能出现新的错误。仅靠一次性评估无法持续保障MindSpore在AI搜索平台上的信息质量。

### 问题

1. 当前没有定期监控机制来跟踪AI平台回答质量的变化
2. 无法及时发现新出现的事实错误或信息衰减（如新版本发布后旧信息未更新）
3. 改进措施实施后缺乏效果验证手段

### 改进措施

1. **建立"AI平台回答质量监控"季度流程**
   - 每季度在4个主流AI平台上测试top 20个FAQ问题
   - 使用本次评估建立的评分框架（现象分类A-E、严重级别P0-P2）
   - 产出季度质量报告，跟踪改进趋势

2. **建立"AI平台回答质量跟踪表"**
   - 记录每次评估的结果、发现的新问题、已修正的旧问题
   - 跟踪每个P0问题的修复进展

3. **建立AI平台反馈闭环**
   - 对发现的严重错误（P0），通过AI平台的官方反馈渠道提交纠错
   - 跟踪纠错请求的处理状态
   - 同时通过多渠道内容发布（博客、论坛、社区文章）增强正确信息在互联网上的权重

4. **与MindSpore文档发布流程集成**
   - 每次重大文档更新或版本发布后，触发一次针对性的AI平台回答质量检查
   - 确保新发布的信息能被AI平台正确获取和引用

---

## Issue #14: Release Notes缺少统一URL模式，AI平台编造了不存在的文档路径

**优先级**: P2
**标签**: `GEO-优化`, `URL规范`, `Release-Notes`, `P2`

### 背景

MindSpore的Release Notes使用 `RELEASE.html` 作为文件名（如 `/lite/docs/zh-CN/r2.8.0/RELEASE.html`），这种命名方式不够直观，也不符合常见的URL模式（如 `/release-notes/2.8.0`）。

### 问题

1. **豆包编造了看似合理的URL路径**：使用了 `release_notes/2.8.0.html` 和 `feature/2.8.0_feature.html` 等路径——这些路径虽然不存在，但比实际路径 `RELEASE.html` 更符合用户的直觉预期
2. **URL不可预测**：AI平台无法通过版本号推断Release Notes的URL，只能从实际抓取中获取
3. **主框架和Lite的Release Notes URL结构不同**：增加了AI平台正确引用的难度

### 改进措施

1. **考虑采用更直观的URL结构**
   - 如 `/release-notes/2.8.0` 或 `/docs/zh-CN/stable/release-notes/`
   - 使URL可从版本号直接推断

2. **为旧路径设置301重定向**
   - 将 `RELEASE.html` 路径重定向到新路径（如适用）
   - 确保已有引用不会失效

3. **在版本历史页面中提供Release Notes索引**
   - 列出所有版本的Release Notes链接
   - 帮助AI平台和用户快速找到特定版本的发布说明

---

> 以上Issue基于GEO Search Assessment对10个MindSpore典型问题×4个主流AI搜索平台的系统性评估结果生成。
> 建议按P0→P1→P2优先级顺序推进，P0问题应在1个月内完成改进。
