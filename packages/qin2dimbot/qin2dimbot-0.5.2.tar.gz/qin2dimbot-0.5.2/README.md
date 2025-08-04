# telegram_dify_bot

一个为 Dify Workflow “量身定做”的 Telegram 群聊机器人。

这不只是又一个普通的 Telegram Bot。它的每个特性，都是为了榨干 Dify Workflow 的全部潜力，并解决群聊机器人那些「难绷」的交互痛点而设计的。

## 🤖 Bot 端：一个合格的群聊“工具人”

Bot 端负责处理一切与 Telegram 交互的脏活累活，目标是让用户感觉自己不是在跟一个冷冰冰的程序对话。

### 如何与 Bot 对话？

很简单，在它能看到的任何地方（白名单群组/私聊），用以下姿势 Q 它：

1.  **直接 @ 它** (`mention`) [🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-mention-hello-world.mp4)
2.  **回复（引用）它发的任何消息** (`reply`) [🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-reply.mp4)
3.  **引用用户消息或转发外部消息再 @ 它** (`reply_and_mention`)，让它“围观”并发表看法 [🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-boke-forward-quote-info.mp4)

### 人机交互特性（我们解决了哪些痛点）

1. **优雅的富文本**：Bot 能优雅地展示各种 Telegram 风格的富文本，告别简陋的纯文本。
2. **无负担的上下文切换**：这可能是最重要的特性。指令与对话的记忆是完全隔离的。你可以在使唤它做各种任务（Agentic Workflow）和闲聊之间无缝切换，彻底摆脱“我需要 `/reset` 吗？”的精神内耗。
3. **所见即所得的流式响应**：对耗时长的任务，Bot 会实时“直播”它的工作进度，而不是让你盯着“正在输入...”干着急。支持 `blocking` 与 `streaming` 智能切换。
4. **Agent 思考过程全透明**：当使用 Agent 时，它的 `thought` 和 `action` 会被实时追踪并展示。你知道它在想什么，在调用什么工具，一切尽在掌握。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-agent-node.mp4)
5. **不止于文本的全模态交互**：无论是文字、图片、文档还是音视频，尽管丢给它。它不仅能“看”懂，还能用图文并茂的方式给你回应。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-mixed-input.mp4)
6. **INSTANT VIEW 释放想象力**：Telegram 客户端支持的渲染表达比较有限，但借助 Telegraph 可表达完整的全模态上下文信息。[preview](https://telegra.ph/%E5%8E%9F%E5%AD%90%E4%B9%8B%E5%BF%83Atomic-Heart-%E6%B8%B8%E6%88%8F%E4%BB%8B%E7%BB%8D-07-20) |  [instant view](https://r2-datalake.echosec.top/blog-obs/2025/07/ce7082a7ffb1b73575e0d35bf1cea8f5.png) | [telegraph article](https://r2-datalake.echosec.top/blog-obs/2025/07/a68a20d8886ad9a4a97f6827e9d22f06.png)

### 已上线的实用指令

-   `/zlib`：获取最新的 Z-Library 接口。如果你在指令后直接跟上书名，它会一步到位地返回搜索结果链接。
-   `/auto-translation`：在国际友人扎堆的群里，自动进行 `i18n` 双向翻译。支持自动启停和上下文语种识别。

### 其他“幕后”特性

-   **白名单**：闲人免入，只为小圈子服务。
-   **防刷屏**：内置了消息编辑速率控制，避免因过于“激动”而被 Telegram 关小黑屋 (`flood ratelimit`)。
-   **拒绝崩溃**：设计了充足的兜底策略，确保在各种意外情况下，它都能给你一个得体的响应，而不是直接“裂开”。
-   **交互感知（Reaction）**：会根据你不同的@姿势，微调上下文结构，并给出不同的交互反馈，让你感觉它“活”过来了。
-   **ping/pong**：使用模板消息响应空输入，这是 healthy check 不需要智能体现。

### 未来的一些脑洞 & Flag

- [ ] **真正的长期记忆**
  > 这是圣杯，也是天坑。目标是让 Bot 能理解碎片化消息背后的深层意图，在连续的对话中表现得更像一个“有记忆”的伙伴，而不是一个金鱼。

- [ ] **视频与音频输出**
  > 需求量极低，但好像有点酷的实验性探索。

- [ ] **Call the bot**
  > 一拍脑门想的，Dify 和机器人接口支不支持实时通话还是个未知数。

- [ ] **群内“仅你可见”的私聊**
  > 在“避免机器人被滥用”和“防止用户社死”之间寻找一个微妙的平衡点。

---

## 🧠 Dify 端：机器人的灵魂所在

> **Tips:** 这部分 Workflow 并未开源。以下介绍基于 [`@qin2dimbot`](https://t.me/qin2dimbot) 的当前配置，仅供参考。

### 核心工作流骨架

1.  **大脑中枢 (意图识别)**：所有请求的第一站。一个灵活、高拓展性的前置节点，负责判断用户“到底想干啥”，然后把请求派发给对应的专才。
2.  **联网搜索问答**：优化的联网搜索流程，让它能基于最新信息回答你的问题。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-web-search.mp4)
3.  **自动翻译机 (AutoTranslation)**：混合模态翻译能力，不仅能处理文本，还能响应 `/auto-translation` 指令，是 `i18n` 群组的刚需。
4.  **能跑代码的数科助理 (Agent: DataScience)**：一个内置代码解释器的 Agent，专门处理计算量大的数科问题。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-agent-node.mp4)
5.  **自带反爬工具的数据矿工 (Agent: DeepMining)**：装备了自研数据挖掘工具，能强行“阅读”指定表网的完整内容，形成对 LLM 友好的上下文，尤其擅长处理有反爬措施的网站。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-url-context.mp4)
6.  **街景猜谜大师 (GeoGuessr)**：一个“图一乐”功能。给它图文线索，它会像真人高手一样，遵循最佳实践，一步步分析画面细节，调用地图工具，最后给出精准的定位和附近的街景。幻觉控制能力较强。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-geolocation.mp4)
7.  **代码助理 (Agent: CodingAssistant)**：一个接入了 `context7` 和 `code-interpreter` 的助手，快速解决文档 QA 和编程问题。
8.  **兜底的温柔 (GreetingBot)**：作为 `ELSE` 分支存在，专门负责在所有意图都匹配失败时，陪用户尬聊。根据统计，它平均每天要响应 13 次来自用户的 `hello`。[🔗](https://r2-datalake.echosec.top/telegram-dify-bot/invoke-bot-general-qa.png)

## Memory, yes but...

在为群聊机器人设计智能时，`Memory`（记忆）是一个绕不开的话题。它听起来很美，是通往“更像人”的阶梯，但在实践中，它更像一个潘多拉魔盒，一旦打开，涌出的全是令人头疼的难题。

### 从「结构化输出」说起：Workflow 的诱惑

当用户在群里 Q 机器人时，我们没法预知他的真实意图。因此，一个可靠的「意图分类」前置节点必不可少，它像一个交通枢纽，将不同的用户输入分流到不同的 Workflow Branch 中处理。

理想情况下，每个分支的终点都应产出一个结构清晰的 JSON，包含 `type`、`answer` 及可选的 `extras` 字段。这样，Bot 端就能根据精准的 `type` 为不同场景精心设计交互，极大地提升用户的 Reaction 感知。

然而，在 Dify v1.6.0 的 Chatflow 中，我们只有纯 `text_chunk`。这意味着，你得在每个分支后面都手动加一个代码节点来 `json.dumps()`。这不仅姿势笨拙，还埋下了「块断裂」和「流式阻塞」的隐患。相比之下，一开始就为结构化输出而生的 Workflow 模式，显得诱人多了。

### 群聊，记忆的混沌之地

传统的 Chatbot 活在一对一的聊天室里，每一次问答都顺理成章地构成上下文，我称之为“瀑布式 QA”。但群聊是一个多玩家在线的混沌环境，机器人被 Q 一下，就留下一段 `history`。此时，一个灵魂拷问出现了：来自不同用户的消息，是该塞进同一个 Conversation，还是相互隔离？

**方案一：共享一个 Conversation**

最直接的问题是，随着时间推移，`history` 会像滚雪球一样越积越多，导致 Chatflow 运行越来越不稳定，后续回答被“记忆污染”的风险剧增。你可能会说：“简单，来个 `/reset` 不就行了？” 但新的问题接踵而至：“谁”有权重置？“何时”是重置的最佳时机？这简直是俄罗斯套娃式的难题。

**方案二：不同用户，不同 Conversation**

这能解决一部分问题，但一个更隐蔽、更棘手的挑战浮出水面：**Telegram-Dify 交互框架的设计复杂度被无限拉高。**

请注意，Telegram Bot 本身无法获取群聊的历史消息，它只能“看”到当前@它的那条消息。这意味着，只有“触发交互”的消息才会被存入 Dify 的 Conversation。表面上看，多轮对话的 `history` 似乎被保留了，但这种 `history` 是破碎的、不完整的。它会立刻、并严重地影响「意图分类」的准确性，以及多轮 QA 场景下模型的表达能力。

举个最典型的例子，一个指令：“总结我们刚才的聊天内容，生成一张词云。”

这个任务在 Chatflow 中几乎不可能原生实现。因为在用户的世界里，“我们”和“刚才”指的是最近一段时间内，多个群友的发言。但在 Bot 的世界里：

1️⃣ Bot 没有时间概念。

2️⃣ Bot 眼里只有“我”（用户）与“你”（机器人），不存在“他们”。

要实现这个功能，可行的方案是绕开 Chatflow 的记忆：在 Bot 端本地维护一个数据库（或通过 Pyrogram 运行 User Account），通过复杂的 `reply` 和 `mention` 关系链，以及时间戳范围，用工程化的方式强行定义出“刚才”和“我们”所包含的 `message`，再将这些内容作为一次性任务（One-shot Task）提交给 Dify 处理。

作为一个一次性任务，你自然希望它不受任何历史记忆的干扰，以求模型给出最快、最准的响应。

### 难绷的用户体验

从日常观察不难发现，群聊的主要信息熵增载体是用户间的交流。机器人通常是被偶尔 Q 一下，解决某个即时问题。此刻，用户要的就是一个快、准、稳的答案。他可能早就忘了上次 Q 机器人是猴年马月的事，但 Bot 却被困在那个没有时间概念的 Conversation 里，用上一次的记忆来污染这一次的回答。

最难绷的情况莫过于：群成员 Q 了一下机器人，发现效果不对，于是 `/reset`，然后重复提问。更折磨的是，用户每次提问前都要先进行一番自我拷问：“我清了吗？”“要不要清？”“我能清吗？”——这种交互体验充满了心智负担，太出戏了。

既然 Chatflow 在群聊场景下痛点如此密集，为什么我还在纠结？显然，最难以权衡的就是 `history`。那么，`memory as history` 这种模式本身是不是就有问题？

### 拨开迷雾：我到底想要什么？

一顿思考过后，我对理想方案的需求已经非常清晰：

1.  **瑞士军刀**：智能端必须快刀斩乱麻，提供又快又准的 QA。
2.  **拒绝降智**：前后两次完全无关的调用，绝不能因“记忆”而产生错误的关联。
3.  **用户隔离**：不同用户的调用必须完全隔离，互不影响。
4.  **交互可塑**：能针对不同 `type` 的场景，在 Telegram 端进行深度定制和优化。
5.  **告别 /reset**：`/reset` 指令剥离了“像人一样交流”的 `reaction` 感，它太复杂，太出戏，我不喜欢。
6.  **尽力而为的上下文**：在需要时，能有办法（比如通过工程化手段）获取到有限但关键的上下文。

如果你也按我的标准去审视 Dify，打开日志会发现，理想状态下的群聊 Conversation，几乎都只有 1 条消息。

那么，在优雅设计的极大诱惑下，**WHY NOT Workflow？**

### 结论：让记忆「润物细无声」

阶段性结论是：在群聊场景下，大模型的长期记忆（或者说 `印象` 与 `画像`），是一个可选的、锦上添花的特性，而非必需品。

大多数时候，`memory` 应该优雅且低调地存在。它不应是对话的沉重状态，而是一种微妙的引导。它“润物细无声”，在每一次调用中，轻微地调整模型的输出走向，最终给用户带来感知明显却又不着痕迹的交互升级。最重要的是，在长期的交互中，它绝不能把模型的智能带向极端和偏执。

## FQA

### Telegram `parse_mode=HTML` 支持的标签列表

> https://core.telegram.org/bots/api#html-style

| 格式化名称             | HTML 标签                                                  | 描述和说明                                                   |
| :--------------------- | :--------------------------------------------------------- | :----------------------------------------------------------- |
| **加粗**               | `<b>...</b>` 或 `<strong>...</strong>`                     | 使文本变为粗体。两者效果相同。                               |
| **斜体**               | `<i>...</i>` 或 `<em>...</em>`                             | 使文本变为斜体。两者效果相同。                               |
| **下划线**             | `<u>...</u>` 或 `<ins>...</ins>`                           | 为文本添加下划线。                                           |
| **删除线**             | `<s>...</s>` 或 `<strike>...</strike>` 或 `<del>...</del>` | 为文本添加删除线。                                           |
| **剧透**               | `<tg-spoiler>...</tg-spoiler>`                             | 隐藏部分文本，用户需要点击后才能查看。                       |
| **链接**               | `<a href="URL">...</a>`                                    | 创建一个超链接。URL 必须是完整的，例如 `https://example.com`。 |
| **行内代码**           | `<code>...</code>`                                         | 以等宽字体显示一小段文本，通常用于代码变量、命令等。         |
| **代码块**             | `<pre>...</pre>`                                           | 创建一个预格式化的多行代码块，保留所有空格和换行符，并以等宽字体显示。 |
| **带语法高亮的代码块** | `<pre><code class="language-python">...</code></pre>`      | 在代码块的基础上增加语法高亮。`language-python` 可以替换为 `language-javascript`, `language-java` 等。 |
| **引用**               | `<blockquote>...</blockquote>`                             | 创建一个引用块，通常带有垂直线标识。                         |

## Reference

https://docs.python-telegram-bot.org/en/stable/

https://core.telegram.org/api

