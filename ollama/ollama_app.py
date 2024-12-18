import json
import os
import time

import streamlit as st

from ollama import Client

ollama_client = Client(
    host='http://192.168.100.231:11434',
)

USE_CHINESE_PROMPT = True
INCLUDE_AFSIM_BACKGROUND = True
MAX_STEP_COUNT = 5 # Max steps to prevent infinite thinking time. Can be adjusted.

def make_api_call(messages, max_tokens, is_final_answer=False):
    for attempt in range(3):
        try:
            response = ollama_client.chat(
                model="qwen2.5:72b",
                # model="qwen2.5:32b",
                # model="qwen2.5-coder:32b-instruct-fp16",
                # model="qwq:32b-preview-fp16",
                messages=messages,
                options={"temperature":0.2, 
                        #  "num_predict":max_tokens # 这里可能会导致 unicode 解析错误
                         },
                format='json',
            )
            # print('ollama response:', response)

            # 尝试处理 qwen2.5:72b 模型返回的 content 包含的 unicode 字符错误，但是似乎没有效果，先不使用 qwen2.5:72b 模型
            # response_content = response['message']['content']
            # response_content = response_content.encode('utf-8').decode('unicode_escape')
            # return json.loads(response_content)

            return json.loads(response['message']['content'])
        except Exception as e:
            print('********** Exception start *********', f"Error: {str(e)}\n")
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

def generate_response(prompt):
    if INCLUDE_AFSIM_BACKGROUND:
        system_info = """AFSIM是一个通用的建模框架，由美国空军研究实验室（AFRL）开发和维护1。它的主要目的是用于模拟和分析作战环境，帮助用户评估军事战略和战术决策的有效性。
具体来说，AFSIM提供了完整的仿真环境，包括：
1.各种战斗平台（例如飞机、坦克、船只等）的模拟。
2.各种武器系统的模拟。
3.环境效应的建模，例如天气、地形等。

你是一位AFSIM建模的专家，将用户的需求，分解成一个个细颗粒度的需求。可以一步一步解释你的推理。"""
    else:
        system_info = "你是一位专业的人工智能助手，可以一步一步解释你的推理。"
    if USE_CHINESE_PROMPT:
        messages = [
            {"role": "system", "content": system_info + """对于每个步骤，提供一个标题来描述你在该步骤中所做的事情，以及内容。决定是否需要另一个步骤，或者是否准备好给出最终答案。
以 JSON 格式回复"title"、"content"和"next_action"（"continue"或"final_answer"）键。尽可能多地使用推理步骤。至少 3 个。了解你作为LLM的局限性，以及你能做什么和不能做什么。在你的推理中，包括对替代答案的探索。考虑你可能是错的，如果你的推理是错的，它会在哪里。充分测试所有其他可能性。你可能会错。当您说您正在重新检查时，请真正重新检查，并使用另一种方法进行。不要只是说您正在重新检查。使用至少 3 种方法来得出答案。使用最佳实践。

有效 JSON 响应的示例：
```json
{
"title"："识别关键信息"，
"content"："要开始解决这个问题，我们需要仔细检查给定的信息并确定将指导我们解决过程的关键要素。这涉及..."，
"next_action"："continue"
}```
"""},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "谢谢！我现在会按照我的指示一步一步思考，在分解问题之后从头开始。"}
        ]
    else:
        messages = [
            {"role": "system", "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, provide a title that describes what you're doing in that step, along with the content. Decide if you need another step or if you're ready to give the final answer. Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys. USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
"""},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
        ]
    
    steps = []
    step_count = 1
    total_thinking_time = 0
    
    while True:
        start_time = time.time()
        step_data = make_api_call(messages, 300)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time

        if 'title' not in step_data:
            step_data['title'] = "..."
        if 'content' not in step_data:
            print(time.time(), '未生成有效 content，重试...')  # Retry if no valid content generated
            continue
        steps.append((f"Step {step_count}: {step_data['title']}", step_data['content'], thinking_time))
        
        messages.append({"role": "assistant", "content": json.dumps(step_data)})
        
        if step_data['next_action'] == 'final_answer' or step_count > MAX_STEP_COUNT:
            break
        
        step_count += 1

        # Yield after each step for Streamlit to update
        yield steps, None  # We're not yielding the total time until the end

    # Generate final answer
    if USE_CHINESE_PROMPT:
        messages.append({"role": "user", "content": "请根据上述推理提供最终答案"})
    else:
        messages.append({"role": "user", "content": "Please provide the final answer based on your reasoning above."})
    
    start_time = time.time()
    final_data = make_api_call(messages, 200, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    steps.append(("Final Answer", final_data['content'], thinking_time))

    yield steps, total_thinking_time

def main():
    st.set_page_config(page_title="y1 prototype", page_icon="🧠", layout="wide")
    
    st.title("y1: AFSIM 需求分解 demo")
    
    st.markdown("""
    GitHubCopilotWorkspace-like Requirements Decomposition Demo 
    """)
    
    # Text input for user query
    user_query = st.text_input("输入你的 AFSIM 场景:", placeholder="e.g., 如何生成一个简单的 1v1 红蓝对抗场景？",
                            #    value="如何生成一个简单的 1v1 红蓝对抗场景？"
                               )
    
    if user_query:
        st.write("正在生成回复...")
        
        # Create empty elements to hold the generated text and total time
        response_container = st.empty()
        time_container = st.empty()
        
        # Generate and display the response
        for steps, total_thinking_time in generate_response(user_query):
            with response_container.container():
                for i, (title, content, thinking_time) in enumerate(steps):
                    if title.startswith("Final Answer"):
                        st.markdown(f"### {title}")
                        st.markdown(content.replace('\n', '<br>'), unsafe_allow_html=True)
                    else:
                        with st.expander(title, expanded=True):
                            st.markdown(content.replace('\n', '<br>'), unsafe_allow_html=True)
            
            # Only show total time when it's available at the end
            if total_thinking_time is not None:
                time_container.markdown(f"**Total thinking time: {total_thinking_time:.2f} seconds**")

if __name__ == "__main__":
    main()
