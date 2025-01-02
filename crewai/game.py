import os
from textwrap import dedent

from crewai import Agent, Crew, Task

# 配置模型（qwen2.5-coder:7b）
os.environ["OPENAI_API_BASE"] = 'http://192.168.100.231:11434'
os.environ["OPENAI_MODEL_NAME"] = 'ollama/qwen2.5-coder:32b'
os.environ["OPENAI_API_KEY"] = 'EMPTY'

#
# 3个智能体逻辑
#
 
def senior_engineer_agent():
	"""高级软件工程师智能体"""
	return Agent(
		role='高级软件工程师',
		goal='根据需求完成软件编程',
		backstory=dedent('''你是一位国际领先的科技公司的高级软件工程师。
			你非常擅长Python编程，并尽自己的最大努力编写功能齐全、运行良好的完美代码。
			'''),
		allow_delegation=False,
		verbose=True
	)
 
def qa_engineer_agent():
	"""高级软件质量工程师智能体"""
	return Agent(
		role='高级软件质量工程师',
		goal='分析程序代码，找出其中的错误，并修复这些错误代码',
		backstory=dedent('''你是一位检测代码的高级工程师。
			你对代码细节很敏锐，非常擅长找出代码中的Bug，包括检查是否缺少导入、变量声明、不匹配括号和语法错误等。
			您还能检查出代码的安全漏洞和逻辑错误。
			'''),
		allow_delegation=False,
		verbose=True
	)
 
def chief_qa_engineer_agent():
	"""首席软件质量工程师智能体"""
	return Agent(
		role='首席软件质量工程师',
		goal='确保代码实现了需求',
		backstory='''你怀疑程序员没有按照需求编写软件，你特别专注于编写高质量的代码。''',
		allow_delegation=True,
		verbose=True
	)


#
# 3个任务逻辑
#
 
def code_task(agent, game):
	return Task(description=dedent(f'''你将按照软件需求，使用Python编写程序:
 
		软件需求
		------------
		{game}
		'''),
		expected_output='你的输出是完整的Python代码, 特别注意只需要输出Python代码，不要输出其他任何内容！',
		agent=agent
	)
 
def review_task(agent, game):
	return Task(description=dedent(f'''你将按照软件需求，进一步使用Python完善给定的程序:
 
		软件需求
		------------
		{game}
 
		根据给定的Python程序代码，检查其中的错误。包括检查逻辑错误语法错误、缺少导入、变量声明、括号不匹配，以及安全漏洞。
		'''),
		expected_output='你的输出是完整的Python代码, 特别注意只需要输出Python代码，不要输出其他任何内容！',
		agent=agent
	)
 
def evaluate_task(agent, game):
	return Task(description=dedent(f'''你将按照软件需求，进一步使用Python完善给定的程序:
 
		软件需求
		------------
		{game}
 
		查看给定的Python程序代码，确保程序代码完整，并且符合软件需求。
		'''),
		expected_output='你的输出是完整的Python代码, 特别注意只需要输出Python代码，不要输出其他任何内容！',
		agent=agent
	)




#
# 团队逻辑
#
 
print('')
game = input('# 您好，我们是游戏智能编程团队，请输入游戏的详细描述：\n\n')
print('')
 
# 智能体
senior_engineer_agent = senior_engineer_agent()
qa_engineer_agent = qa_engineer_agent()
chief_qa_engineer_agent = chief_qa_engineer_agent()
 
# 任务
code_game = code_task(senior_engineer_agent, game)
review_game = review_task(qa_engineer_agent, game)
approve_game = evaluate_task(chief_qa_engineer_agent, game)
 
# 团队
crew = Crew(
	agents=[
		senior_engineer_agent,
		qa_engineer_agent,
		chief_qa_engineer_agent
	],
	tasks=[
		code_game,
		review_game,
		approve_game
	],
	verbose=True
)
 
# 执行
game_code = crew.kickoff()


# 输出
print("\n\n########################")
print("## 游戏代码结果")
print("########################\n")
print(game_code)
 
# 存储代码
filename = 'Game.py'
 
print("\n\n########################\n")
with open(filename, 'w', encoding='utf-8') as file:
    file.write(game_code.raw)
 
print(f"游戏代码已经存储到文件： {filename}")
print(f'你可以运行游戏：python {filename}')