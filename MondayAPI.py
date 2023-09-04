import os
import json
import requests

from dotenv import load_dotenv, find_dotenv
from rich.console import Console

from logger_setup import log


_ = load_dotenv(find_dotenv()) # read local .env file
board_id = os.environ['MONDAY_BOARD_ID']
group_name = os.environ['MONDAY_GROUP_NAME']

class MondayAPI:

    BASE_URL = "https://api.monday.com/v2"

    def __init__(self, api_key: str):
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        self.console = Console()

    def add_item(self, query: str) -> str:
        log.debug("")
        log.debug(f"Adding item to Monday.com with query: {query}")
        payload = json.dumps({
            "query": f"mutation {{create_item (board_id: 5055046136, group_id: \"new_group\", item_name: \"{query}\") {{id}}}}"
        })

        log.debug(f"Sending Payload: {payload}")
        response = requests.post(self.BASE_URL, headers=self.headers, data=payload)
        log.info(f"Response: {response.text}")
        if response.status_code == 200:
            log.debug(f"Item added successfully")
            return "Item added successfully"
        else:
            log.error(f"Request failed: {response.text}")
            return f"Request failed: {response.text}"


    def add_item_with_priority(self, query: str) -> str:
        log.debug("Adding item to Monday.com with query")
        query = json.loads(query)
        title = query.get("title")
        description = query.get("text")
        priority = query.get("priority")

        column_values = json.dumps({
            "text": description,
            "priority": priority
        }).replace('"', '\\"')

        query = f'''
                mutation {{
                    create_item (
                        board_id: {board_id},
                        group_id: "{group_name}",
                        item_name: "{title}",
                        column_values: "{column_values}"
                    ) {{
                        id
                    }}
                }}
                '''

        payload = json.dumps({
            "query": query
        })

        response = None
        with self.console.status("[green]Adding Item to Monday.com[/green] \n", spinner='aesthetic') as status:
            response = requests.post(self.BASE_URL, headers=self.headers, data=payload)

        log.info(f"Response: {response.text}")
        if response and response.status_code == 200:
            log.debug(f"Item added successfully")
            return "Item added successfully"
        else:
            log.error(f"Request failed: {response.text}")
            return f"Request failed: {response.text}"


