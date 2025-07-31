import json
import logging
from typing import List, Optional, Any, Generator, Dict, Callable

from agents_manager.models import Genai
from agents_manager.Container import Container
from agents_manager.utils import write_log
from agents_manager.Agent import Agent


class AgentManager:
    def __init__(self, log: bool = True) -> None:
        """
        Initialize the AgentManager with an empty list of agents.
        """

        self.log = log
        self.tool_logger = logging.getLogger("agents_manager.Tool")
        self.logger = logging.getLogger("agents_manager.AgentManager")
        self.container_logger = logging.getLogger("agents_manager.Container")

        write_log(self.log, self.logger, "AgentManager log setup")

        self.agents: List[Agent] = []

    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the manager's list.

        Args:
            agent (Agent): The agent instance to add.
        """
        if not isinstance(agent, Agent):
            raise ValueError("Only Agent instances can be added")
        _, existing_agent = self.get_agent(agent.name)
        if not existing_agent:
            self.agents.append(agent)

    def get_agent(self, name: str) -> tuple[Optional[int], Optional[Agent]]:
        """
        Retrieve an agent by name.
        Args:
            name (str): The name of the agent to find.
        Returns:
            tuple[Optional[int], Optional[Agent]]: A tuple containing the index and agent if found, else (None, None).
        """

        for _, agent in enumerate(self.agents):
            if agent.name == name:
                return _, agent
        return None, None

    def _initialize_user_input(
        self, name: str, user_input: Optional[Any] = None
    ) -> tuple[Optional[int], Optional[Agent]]:

        _, agent = self.get_agent(name)

        if agent is None:
            raise ValueError(f"No agent found with name: {name}")
        agent.set_messages([])
        agent.set_system_message(agent.instruction)
        agent.set_tools(agent.tools)
        agent.set_output_format()
        if user_input:
            agent.set_user_message(user_input)
        return _, agent

    @staticmethod
    def get_model_current_messages(agent: Agent, current_messages: list):
        if type(agent.get_model()) == Genai:
            return current_messages
        else:
            new_current_messages = []

            for curr in current_messages:
                if curr["role"] != "system":
                    new_current_messages.append(curr)

            return new_current_messages

    @staticmethod
    def _update_current_message(
        agent: Agent, current_messages: list, tool_responses: list, tool_call: Dict
    ):
        current_messages.append(tool_call)

        tool_response = agent.get_model().get_tool_message(tool_responses)
        if isinstance(tool_response, dict):
            current_messages.append(tool_response)
        if isinstance(tool_response, list):
            current_messages.extend(tool_response)

        agent.set_messages(current_messages)

    def _handle_agent_tool_call(
        self,
        tool_result: Agent,
        function_name: str,
        id: Any,
        user_input: Optional[Any],
    ):
        if not self.get_agent(tool_result.name)[1]:
            self.add_agent(tool_result)

        write_log(
            self.log,
            self.logger,
            f"Delegating execution to nested agent from container: {tool_result.name}",
        )

        child_response = self.run_agent(tool_result.name, user_input)

        return {
            "id": id,
            "tool_result": str(child_response.get("content", child_response)),
            "name": function_name,
        }

    def _handle_tool_call(
        self,
        agent: Agent,
        tool: Callable,
        function_name: str,
        arguments: dict,
        index: int,
        user_input: Optional[Any],
        id: Any,
        current_messages: list,
        assistant_message: list,
    ):
        write_log(
            self.log,
            self.logger,
            f"Invoking callable tool: {tool.__name__}",
        )

        tool_result = tool(**arguments)

        if isinstance(tool_result, Agent):
            write_log(
                self.log,
                self.tool_logger,
                f"{{tool_name: {tool.__name__}, arguments: {arguments}, result: {tool_result}}}",
            )
            tool_response = self._handle_agent_tool_call(
                tool_result, function_name, id, user_input
            )

        else:
            write_log(
                self.log,
                self.tool_logger,
                f"{{tool_name: {tool.__name__}, arguments: {arguments}, result: {tool_result}}}",
            )
            tool_response = {
                "id": id,
                "tool_result": str(tool_result),
                "name": function_name,
            }

        self._update_current_message(
            agent, current_messages, [tool_response], assistant_message[index]
        )

        write_log(
            self.log,
            self.logger,
            f"Tool '{tool.__name__}' completed successfully.",
        )

    def _handle_handover_tool_call(
        self,
        agent: Agent,
        tool: Callable,
        function_name: str,
        index: int,
        user_input: Optional[Any],
        id: Any,
        current_messages: list,
        assistant_message: list,
    ):
        write_log(
            self.log,
            self.logger,
            f"Invoking handover tool: {tool.__name__}",
        )

        tool_result = tool()

        write_log(
            self.log,
            self.tool_logger,
            f"{{tool_name: {tool.__name__}, arguments: {{}}, result: {tool_result}}}",
        )

        write_log(
            self.log,
            self.logger,
            f"Delegating execution to agent: {tool_result}",
        )

        if tool.share_context:
            child_response = self.run_agent(
                tool_result,
                self.get_model_current_messages(
                    self.get_agent(tool_result)[1], current_messages
                ),
            )
        else:
            child_response = self.run_agent(tool_result, user_input)

        tool_response = {
            "id": id,
            "tool_result": str(child_response.get("content", child_response)),
            "name": function_name,
        }

        self._update_current_message(
            agent, current_messages, [tool_response], assistant_message[index]
        )

        write_log(
            self.log,
            self.logger,
            f"Handover tool '{tool.__name__}' completed successfully.",
        )

    def _handle_container_tool_call(
        self,
        agent: Agent,
        tool: Callable,
        function_name: str,
        arguments: dict,
        index: int,
        user_input: Optional[Any],
        id: Any,
        current_messages: list,
        assistant_message: list,
    ):
        write_log(
            self.log,
            self.logger,
            f"Invoking container tool: {tool.name} with arguments: {arguments}",
        )

        tool_result = tool.run(arguments)

        if isinstance(tool_result, Agent):
            write_log(
                self.log,
                self.container_logger,
                f"{{tool_name: {tool.name}, arguments: {arguments}, result: {tool_result}}}",
            )

            tool_response = self._handle_agent_tool_call(
                tool_result, function_name, id, user_input
            )

        else:
            write_log(
                self.log,
                self.container_logger,
                f"{{tool_name: {tool.name}, arguments: {arguments}, result: {tool_result}}}",
            )

            tool_response = {
                "id": id,
                "tool_result": str(tool_result),
                "name": function_name,
            }

        self._update_current_message(
            agent, current_messages, [tool_response], assistant_message[index]
        )

        write_log(
            self.log,
            self.logger,
            f"Container tool '{tool.name}' completed successfully.",
        )

    def process_tools(
        self,
        agent: Agent,
        tool_calls: list,
        user_input: Any,
        current_messages: list,
        assistant_message: list,
    ):
        for i, tool_call in enumerate(tool_calls):
            output = agent.get_model().get_keys_in_tool_output(tool_call)
            id, function_name = output["id"], output["name"]
            arguments = (
                json.loads(output["arguments"])
                if isinstance(output["arguments"], str)
                else output["arguments"]
            )

            write_log(
                self.log,
                self.logger,
                f"Preparing to invoke tool '{function_name}' with arguments: {arguments}",
            )

            for tool in agent.tools:
                if isinstance(tool, Callable) and (
                    tool.__name__ == function_name
                    and not tool.__name__.startswith("handover_")
                ):
                    self._handle_tool_call(
                        agent,
                        tool,
                        function_name,
                        arguments,
                        i,
                        user_input,
                        id,
                        current_messages,
                        assistant_message,
                    )

                elif isinstance(tool, Callable) and (
                    tool.__name__.startswith("handover_")
                    and tool.__name__ == function_name
                ):
                    self._handle_handover_tool_call(
                        agent,
                        tool,
                        function_name,
                        i,
                        user_input,
                        id,
                        current_messages,
                        assistant_message,
                    )

                elif isinstance(tool, Container) and (
                    tool.name == function_name and not tool.name.startswith("handover_")
                ):
                    self._handle_container_tool_call(
                        agent,
                        tool,
                        function_name,
                        arguments,
                        i,
                        user_input,
                        id,
                        current_messages,
                        assistant_message,
                    )

    def run_agent(self, name: str, user_input: Optional[Any] = None) -> Dict:
        """
        Run a specific agent's non-streaming response.

        Args:
            name (str): The name of the agent to run.
            user_input (str, optional): Additional user input to append to messages.

        Returns:
            Any: The agent's response.
        """
        _, agent = self._initialize_user_input(name, user_input)

        write_log(self.log, self.logger, f"Executing agent: {agent.name}")
        response = agent.get_response()

        if not response["tool_calls"]:
            write_log(
                self.log,
                self.logger,
                f"Agent {agent.name} returned a response without tool calls.",
            )
            return response

        tool_calls = response["tool_calls"]
        current_messages = agent.get_messages()
        assistant_message = agent.get_model().get_assistant_message(response)

        self.process_tools(
            agent, tool_calls, user_input, current_messages, assistant_message
        )

        return self.run_agent(
            agent.name, self.get_model_current_messages(agent, current_messages)
        )

    def run_agent_stream(
        self,
        name: str,
        user_input: Optional[Any] = None,
    ) -> Generator[Dict, None, None]:
        """
        Run a specific agent's streaming response.

        Args:
            name (str): The name of the agent to run.
            user_input (str, optional): Additional user input to append to messages.

        Returns:
            Any: The agent's response.
        """
        _, agent = self._initialize_user_input(name, user_input)

        write_log(self.log, self.logger, f"Executing agent (streaming): {agent.name}")

        result = agent.get_stream_response()
        response = ""

        for resp in result:
            if resp["tool_calls"]:
                response = resp
            else:
                yield resp

        if not response:
            write_log(
                self.log, self.logger, f"{agent.name} returned without any tool calls"
            )
            return

        tool_calls = response["tool_calls"]
        current_messages = agent.get_messages()
        assistant_message = agent.get_model().get_assistant_message(response)

        self.process_tools(
            agent, tool_calls, user_input, current_messages, assistant_message
        )

        write_log(
            self.log, self.logger, f"Streaming final response from agent: {agent.name}"
        )

        yield from self.run_agent_stream(
            agent.name, self.get_model_current_messages(agent, current_messages)
        )
        return
