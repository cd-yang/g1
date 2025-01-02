import os
from textwrap import dedent

from crewai import Agent, Crew, Task

# 配置模型（qwen2.5-coder:7b）
os.environ["OPENAI_API_BASE"] = 'http://192.168.100.231:11434'
os.environ["OPENAI_MODEL_NAME"] = 'ollama/qwen2.5-coder:32b'
os.environ["OPENAI_API_KEY"] = 'EMPTY'

#
# 智能体逻辑
#
 
def senior_engineer_agent():
	"""AFSIM仿真业务专家智能体"""
	return Agent(
		role='AFSIM仿真业务专家',
		goal='根据需求完成需求分解',
		backstory=dedent('''AFSIM是一个通用的建模框架，由美国空军研究实验室（AFRL）开发和维护1。它的主要目的是用于模拟和分析作战环境，帮助用户评估军事战略和战术决策的有效性。
具体来说，AFSIM提供了完整的仿真环境，包括：
1.各种战斗平台（例如飞机、坦克、船只等）的模拟。
2.各种武器系统的模拟。
3.环境效应的建模，例如天气、地形等。

你是一位AFSIM建模的专家，将用户的需求，分解成一个个细颗粒度的需求。可以一步一步解释你的推理。
			'''),
		allow_delegation=False,
		verbose=True
	)

 
def chief_qa_engineer_agent():
	"""首席软件质量工程师智能体"""
	return Agent(
		role='首席软件质量工程师',
		goal='确保代码实现了需求',
		backstory='''你怀疑AFSIM仿真业务专家没有按照邀请进行需求分解，你特别专注于逻辑的正确性和一致性。''',
		allow_delegation=True,
		verbose=True
	)


#
# 任务逻辑
#
 
def code_task(agent, game):
	return Task(description=dedent(f'''你将按照AFSIM建模需求，将其分解成可理解的、更细粒度的需求:
 
		AFSIM 需求
		------------
		{game}
		'''),
		expected_output='你的输出是分解后的需求，不要输出其他任何内容！',
		agent=agent
	)
 
def review_task(agent, game):
	return Task(description=dedent(f'''你将按照 AFSIM 仿真需求，一步一步分解需求:
 
		AFSIM 需求
		------------
		{game}
 
		根据给定的需求，检查其中的错误。包括检查逻辑正确性、一致性等。
		'''),
		# expected_output='你的输出是完整的Python代码, 特别注意只需要输出Python代码，不要输出其他任何内容！',
		expected_output='你的输出是分解后的需求，不要输出其他任何内容！',
		agent=agent
	)


#
# 团队逻辑
#
 
print('')
game = input('# 您好，请输入 AFSIM 的需求：\n\n')
print('')
 
# 智能体
senior_engineer_agent = senior_engineer_agent()
chief_qa_engineer_agent = chief_qa_engineer_agent()
 
# 任务
code_game = code_task(senior_engineer_agent, game)
review_game = review_task(chief_qa_engineer_agent, game)
 
# 团队
crew = Crew(
	agents=[
		senior_engineer_agent,
		chief_qa_engineer_agent
	],
	tasks=[
		code_game,
		review_game,
	],
	verbose=True
)
 
# 执行
game_code = crew.kickoff()


# 输出
print("\n\n########################")
print("## 结果")
print("########################\n")
print(game_code)
 
# 存储代码
filename = 'afsim_result_crewai.md'
 
print("\n\n########################\n")
with open(filename, 'w', encoding='utf-8') as file:
    file.write(game_code.raw)
 
print(f"结果已经存储到文件： {filename}")
