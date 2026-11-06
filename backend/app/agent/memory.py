from langchain_core.messages import trim_messages

def get_short_term_memory():
    """
    配置短期记忆策略：保留最近的 10 条消息，且总 token 不超过 2000。
    """
    return trim_messages(
        max_tokens=2000,
        strategy="last",
        token_counter=len, 
        include_system=True,
        allow_partial=False,
        start_on="human",
    )