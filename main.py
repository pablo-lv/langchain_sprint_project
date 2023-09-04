import os
import json
import warnings
warnings.filterwarnings('ignore')

import openai
from langchain.agents import AgentType, initialize_agent, create_csv_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.chains import SimpleSequentialChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv
from langchain.output_parsers import CommaSeparatedListOutputParser
from rich import print
from rich.console import Console
from rich.panel import Panel


from logger_setup import log
from MondayAPI import MondayAPI
from priority_router import build_priority_multi_router_chain
from monday_transform_chain import build_transform_chain

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

console = Console()

def add_single_task():
    task = input("What task would you like to add? ")
    monday_task_manager(task)

def load_tasks_from_csv():
    monday_task_manager(load_csv=True)


def main():
    console.clear()
    panel = Panel("[bold blue]Welcome to Task Manager[/bold blue]", title="Task Manager Menu", style="bold white on blue")
    options_panel = Panel("[1] Add a single task\n[2] Load CSV\n[Q] Quit", title="Options", style="bold white on blue")
    console.print(panel)
    while True:
        console.print(options_panel)
        choice = input("Select an option: ")


        if choice == "1":
            add_single_task()
        elif choice == "2":
            load_tasks_from_csv()
        elif choice.lower() == "q":
            console.print("Goodbye!")
            break
        else:
            console.print("Invalid choice. Please select a valid option.", style="bold red")



def monday_task_manager(task= "", load_csv=False):
    DEFAULT_TEMPERATURE = 0
    GPT_THREE_TURBO = "gpt-3.5-turbo"
    GPT4 = "gpt-4"

    LLM = ChatOpenAI(temperature=DEFAULT_TEMPERATURE, model_name=GPT_THREE_TURBO)
    LLM_GPT4 = ChatOpenAI(temperature=DEFAULT_TEMPERATURE, model_name=GPT_THREE_TURBO)
    monday_api = MondayAPI(os.environ['MONDAY_API_KEY'])

    # Monday.com API Agent
    tools = [
        Tool.from_function(
            func=monday_api.add_item_with_priority,
            name="Add Item to Monday.com",
            description="Useful for when you need to add a new item to Monday, input is the name of the new item",
        ),
    ]
    agent = initialize_agent(tools, LLM, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
    log.info("MondayCom Agent initialized")
    transform_chain = build_transform_chain()
    priority_router_chain =  build_priority_multi_router_chain(LLM)

    # Usage:
    simple_sequential_chain = SimpleSequentialChain(chains=[priority_router_chain, transform_chain])
    log.info("Simple sequential chain created")

    # CSV Agent
    if load_csv:
        csv_agent = create_csv_agent(LLM_GPT4, "todo.csv", verbose=False)
        log.info("CSV Agent initialized")

        get_todo_items_tmpl = "Retrieve {input} records from the 'item' column. \n{format_instructions}"

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()
        prompt = PromptTemplate(
            template=get_todo_items_tmpl,
            input_variables=["input"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format(input="all")
        todo_list = csv_agent.run(prompt)
        todo_output = output_parser.parse(todo_list)
        for item in todo_output:
            todo_payload = simple_sequential_chain.run(item)
            result_str = json.dumps(todo_payload)
            print(result_str)
            agent.run(f"Add this to monday {str(result_str)}")
    else:
        todo_payload = simple_sequential_chain.run(task)
        result_str = json.dumps(todo_payload)
        print(result_str)
        agent.run(f"Add this to monday {str(result_str)}")


if __name__ == "__main__":
    main()