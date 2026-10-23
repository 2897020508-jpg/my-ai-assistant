import streamlit as st
import urllib.request
import json

# ========== 密钥：从"保险箱"里读，不写在代码里 ==========
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    st.error(
        "没有找到 API Key。请在本地 .streamlit/secrets.toml "
        "或 Streamlit Cloud 的 Secrets 里设置 DEEPSEEK_API_KEY。"
    )
    st.stop()

URL = "https://api.deepseek.com/chat/completions"

# ========== 四种 AI 人设 ==========
PERSONAS = {
    "通用助手": "你是一个乐于助人的中文助手，回答要通俗、简洁。",
    "Python 老师": "你是一位耐心的 Python 老师，用生活中的例子解释，每次只讲一个重点，最后给一个小练习。",
    "Web3 导师": "你是一位 Web3 导师，用小白能听懂的话解释区块链和智能合约，并提醒安全风险。",
    "英语陪练": "你是一位英语陪练，先用简单英文回复，再附上中文解释，鼓励我大胆开口。",
    "健身教练": "你是一位健身教练，给我制定科学的健身计划，注意饮食和休息。",
    "营养师": "你是一位营养师，帮我制定健康的饮食计划，注意营养均衡和热量控制。",
}

# ========== 页面基本设置 ==========
st.set_page_config(page_title="我的 AI 助手 v3", page_icon="🤖", layout="centered")

# ========== 一小段 CSS：让界面更好看 ==========
st.markdown("""
<style>
/* 聊天气泡：加圆角、内边距、淡淡的边框 */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(128, 128, 128, 0.18);
}

/* 页面顶部留一点空间 */
.block-container {
    padding-top: 2rem;
}

/* 按钮：圆角 + 稍微大一点 */
.stButton > button {
    border-radius: 12px;
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# ========== 初始化"储物柜" ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": PERSONAS["通用助手"]}
    ]
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""
if "persona" not in st.session_state:
    st.session_state.persona = "通用助手"

# ========== 侧边栏：设置区 ==========
with st.sidebar:
    st.header("⚙️ 设置")

    persona_name = st.selectbox("选择 AI 类型", list(PERSONAS.keys()))

    # 如果换了人设，就更新第一条 system 消息
    if persona_name != st.session_state.persona:
        st.session_state.persona = persona_name
        st.session_state.messages[0]["content"] = PERSONAS[persona_name]

    st.divider()

    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": PERSONAS[persona_name]}
        ]
        st.session_state.pending_question = ""
        st.rerun()

    st.caption("当前版本：v3")
    st.caption("有记忆 · 可换人设 · 界面美化")

# ========== 标题 ==========
st.title("🤖 我的 AI 助手 v3")
st.caption("有记忆 · 可换人设 · 界面更漂亮")

# ========== 调用 AI 的函数 ==========
def ask_ai(messages):
    data = json.dumps({
        "model": "deepseek-chat",
        "messages": messages
    }).encode()

    req = urllib.request.Request(URL, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    })

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return "出错了：" + str(e)

# ========== 显示历史聊天记录 ==========
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="😎"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])

# ========== 欢迎页 + 示例问题（只在没聊过时显示） ==========
if len(st.session_state.messages) == 1:
    st.write("你好，我是你的小伙伴")
    st.write("可以从下面选一个问题，也可以直接在下面输入。")

    col1, col2, col3 = st.columns(3)
    examples = [
        "用一句话解释智能合约",
        "帮我制定今天的学习计划",
        "Python 里变量是什么？",
    ]
    for col, q in zip([col1, col2, col3], examples):
        if col.button(q, use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

# ========== 输入框 ==========
typed = st.chat_input("输入你的问题，按回车发送")
question = typed or st.session_state.pending_question
st.session_state.pending_question = ""

# ========== 用户提问：先把你说的存下来 ==========
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.rerun()

# ========== 如果最后一句是用户说的，就让 AI 回答 ==========
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("AI 正在思考..."):
            answer = ask_ai(st.session_state.messages)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})