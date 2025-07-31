from eagle.agents.base import (
    BasicAgent,
    BasicAgentConfigSchema,
    BasicWorkingMemoryState
)
from eagle.agents.react_agent.prompts import prompt_generator
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
from eagle.agents.base import BasicWorkingMemoryState
from langchain_core.language_models.chat_models  import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import List, Any, Dict, Optional
from pydantic import Field, field_validator, BaseModel
import hashlib
from datetime import datetime, timezone

# React special state
class ReactAgentState(AgentState):
    """
    State for the React Planning Agent.
    """
    messages: List[Any] = []
    observation: str = ""
    plan: str = ""
    tools_interactions: Dict[str, Any] = {}

# Config Schema
class SharedObjectsMemoryConfigSchema(BaseModel):
    language: str = Field(default="pt-br", description="Language for object summaries.")
    k: int = Field(default=10, description="Number of recent memories to retrieve.")

class ReactPlanningAgentConfigSchema(BasicAgentConfigSchema):
    chat_history_window_size: int = Field(default=5, description="Size of the chat history window.")
    observe_tools: List[BaseTool] = Field(default_factory=list, description="List of tools for the observe node.")
    planning_tools: List[BaseTool] = Field(default_factory=list, description="List of tools for the planning node.")
    executing_tools: List[BaseTool] = Field(default_factory=list, description="List of tools for the executing node.")
    observe_important_guidelines: str = Field(default="", description="Important guidelines for the observe node.")
    plan_important_guidelines: str = Field(default="", description="Important guidelines for the plan node.")
    execute_important_guidelines: str = Field(default="", description="Important guidelines for the execute node.")
    observe_node_llm: Optional[BaseChatModel] = Field(default=None, description="Pre-instantiated LLM for the observe node.")
    observe_node_llm_prompt_language: str = Field(default="pt-br", description="Prompt language for the observe node.")
    observe_node_llm_use_structured_output: bool = Field(default=False, description="Whether to use structured output for the observe node.")
    plan_node_llm: Optional[BaseChatModel] = Field(default=None, description="Pre-instantiated LLM for the plan node.")
    plan_node_llm_prompt_language: str = Field(default="pt-br", description="Prompt language for the plan node.")
    plan_node_llm_use_structured_output: bool = Field(default=False, description="Whether to use structured output for the plan node.")
    execute_node_llm: Optional[BaseChatModel] = Field(default=None, description="Pre-instantiated LLM for the execute node.")
    execute_node_llm_prompt_language: str = Field(default="pt-br", description="Prompt language for the execute node.")
    execute_node_llm_use_structured_output: bool = Field(default=False, description="Whether to use structured output for the execute node.")
    observe_shared_objects_config: SharedObjectsMemoryConfigSchema = Field(
        default=SharedObjectsMemoryConfigSchema(),
        description="Configuration for shared objects memory for the observe node."
    )
    plan_shared_objects_config: SharedObjectsMemoryConfigSchema = Field(
        default=SharedObjectsMemoryConfigSchema(),
        description="Configuration for shared objects memory for the plan node."
    )
    execute_shared_objects_config: SharedObjectsMemoryConfigSchema = Field(
        default=SharedObjectsMemoryConfigSchema(),
        description="Configuration for shared objects memory for the execute node."
    )

    @field_validator('observe_tools', 'planning_tools', 'executing_tools', mode='before')
    def validate_tool_objects(cls, v):
        if isinstance(v, list) and all(issubclass(type(tool), BaseTool) for tool in v):
            return v
        raise TypeError("All tools must be instances of BaseTool or its subclasses.")

    @field_validator('observe_node_llm', 'plan_node_llm', 'execute_node_llm', mode='before')
    def validate_llm_objects(cls, v):
        if v is None or issubclass(type(v), BaseChatModel):
            return v
        raise TypeError("LLM must be an instance of BaseChatModel or its subclasses.")

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Serialize LLM objects to dictionaries
        for field_name in ['observe_node_llm', 'plan_node_llm', 'execute_node_llm']:
            data[field_name] = getattr(self, field_name)
        # Serialize tools to dictionaries
        for field_name in ['observe_tools', 'planning_tools', 'executing_tools']:
            data[field_name] = getattr(self, field_name)
        return data

    class Config:
        arbitrary_types_allowed = True

# Helper function
def process_graph_stream(graph, inputs, config):
    """
    Helper function to process the graph stream and update tool interactions.
    """
            
    tool_calls_by_tool_names = {}
        
    done = False
    while not done:
        for s in graph.stream(inputs, stream_mode="values"):
            messages = s["messages"]
            state_snapshot = graph.get_state(config)
            if isinstance(messages[-1], AIMessage) and len(messages[-1].tool_calls) > 0: 
                for tool_call in messages[-1].tool_calls:
                    inputs["tools_interactions"][tool_call['id']] = {
                        "call": tool_call,
                        "response": None
                    }
            elif isinstance(messages[-1], ToolMessage):
                # check if all messages are ToolMessage
                if all(isinstance(m, ToolMessage) for m in messages):
                    for message in messages:
                        tool_name = inputs["tools_interactions"][message.tool_call_id]['call']['name']
                        args_hash = hashlib.sha256(str(inputs["tools_interactions"][message.tool_call_id]['call']['args']).encode("utf-8")).hexdigest()
                        response_hash = hashlib.sha256(str(message.content).encode("utf-8")).hexdigest()
                        if tool_name in tool_calls_by_tool_names and args_hash in tool_calls_by_tool_names[tool_name]:
                            if tool_calls_by_tool_names[tool_name][args_hash] != response_hash:
                                inputs["tools_interactions"][message.tool_call_id]['response'] = message.content if message.content != '' else 'Empty response!!'
                        else:
                            inputs["tools_interactions"][message.tool_call_id]['response'] = message.content if message.content != '' else 'Empty response!!'
                        
                        if tool_name not in tool_calls_by_tool_names:
                            tool_calls_by_tool_names[tool_name] = {
                                args_hash: response_hash
                            }
                        else:
                            tool_calls_by_tool_names[tool_name][args_hash] = response_hash
                    return inputs, None
                else:
                    raise ValueError("Expected all messages to be ToolMessage.")
        done = isinstance(messages[-1], AIMessage) and (not messages[-1].tool_calls) and messages[-1].content != ''    
    return inputs, messages[-1]

# Nodes

def observe_node(state: BasicWorkingMemoryState, config: RunnableConfig, store):

    observe_node_llm = config.get("configurable").get("observe_node_llm")
    observe_node_prompt_language = config.get("configurable").get("observe_node_llm_prompt_language")
    observe_node_prompt_use_structured_output = config.get("configurable").get("observe_node_llm_use_structured_output", False)
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="observe",
        language=observe_node_prompt_language,
        llm=observe_node_llm,
        use_structured_output=observe_node_prompt_use_structured_output,
    )
    
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]

    chat_id = config.get("configurable").get("chat_id")

    tools = config.get("configurable").get("observe_tools", [])

    important_guidelines = config.get("configurable").get("observe_important_guidelines")

    shared_memory_configs = config.get("configurable").get("observe_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages))
    
    message = None
    inputs = {
        "messages": state.messages[-window_size:],
        "observation": state.observation,
        "plan": state.plan,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        # Fetch object summary
        objects_summary = ""
        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=object_ids, language=shared_memory_configs['language']
            )
        graph = create_react_agent(
            model=observe_node_llm,
                prompt=prompt.partial(
                    agent_name=config.get("configurable").get("agent_name"),
                    agent_description=config.get("configurable").get("agent_description"),
                    observation=state.observation,
                    plan=state.plan,
                    objects_summary=objects_summary,
                    important_guidelines=important_guidelines
                ),
                tools=tools,
                state_schema=ReactAgentState,
            )
        inputs, message = process_graph_stream(graph, inputs, config)

    # Access the 'role' attribute directly instead of using subscript notation
    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")

    if response.action == "nothing":
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "messages": [AIMessage(content=response.message, name=config.get("configurable").get("agent_name"))],
        }

    elif response.action == "answer":
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "messages": [AIMessage(content=response.message, name=config.get("configurable").get("agent_name"))],
        }

    elif response.action == "think":
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False,
            "observation": response.message
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

def plan_node(state: BasicWorkingMemoryState, config: RunnableConfig, store):

    plan_node_llm = config.get("configurable").get("plan_node_llm")
    plan_node_prompt_language = config.get("configurable").get("plan_node_llm_prompt_language")
    plan_node_prompt_use_structured_output = config.get("configurable").get("plan_node_llm_use_structured_output", False)
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="plan",
        language=plan_node_prompt_language,
        llm=plan_node_llm,
        use_structured_output=plan_node_prompt_use_structured_output
    )
    
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]

    chat_id = config.get("configurable").get("chat_id")

    tools = config.get("configurable").get("planning_tools", [])

    important_guidelines = config.get("configurable").get("plan_important_guidelines")

    shared_memory_configs = config.get("configurable").get("plan_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages))
    
    message = None
    inputs = {
        "messages": state.messages[-window_size:],
        "observation": state.observation,
        "plan": state.plan,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        # Fetch object summary
        objects_summary = ""
        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=object_ids, language=shared_memory_configs['language']
            )
        graph = create_react_agent(
            model=plan_node_llm,
            prompt=prompt.partial(
                agent_name=config.get("configurable").get("agent_name"),
                agent_description=config.get("configurable").get("agent_description"),
                observation=state.observation,
                plan=state.plan,
                objects_summary=objects_summary,
                important_guidelines=important_guidelines
            ),
            tools=tools,
            state_schema=ReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    # Access the 'role' attribute directly instead of using subscript notation
    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")

    if response.action == "execute":
        return {
            "node_from": "plan_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False,
            "my_plan_is_complete": True,
            "observation": "",
            "plan": response.message,
        }

    elif response.action == "nothing":
        return {
            "node_from": "plan_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False,
            "my_plan_is_complete": False,
            "observation": "",
            "plan": response.message
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

def execute_node(state: BasicWorkingMemoryState, config: RunnableConfig, store):

    execute_node_llm = config.get("configurable").get("execute_node_llm")
    execute_node_prompt_language = config.get("configurable").get("execute_node_llm_prompt_language")
    execute_node_prompt_use_structured_output = config.get("configurable").get("execute_node_llm_use_structured_output", False)
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="execute",
        language=execute_node_prompt_language,
        llm=execute_node_llm,
        use_structured_output=execute_node_prompt_use_structured_output
    )
    
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]

    chat_id = config.get("configurable").get("chat_id")

    tools = config.get("configurable").get("executing_tools", [])

    important_guidelines = config.get("configurable").get("execute_important_guidelines")

    shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages))

    message = None
    inputs = {
        "messages": state.messages[-window_size:],
        "observation": state.observation,
        "plan": state.plan,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        # Fetch object summary
        objects_summary = ""
        must_cite_objects_summary = ""

        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            must_cite_object_ids = []
            if state.interaction_initial_datetime:
                for metadata in last_memories_metadata:
                    if datetime.fromtimestamp(metadata.created_at/1000).astimezone(timezone.utc) >= state.interaction_initial_datetime:
                        must_cite_object_ids.append(metadata.object_id)
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=list(set(object_ids)-set(must_cite_object_ids)), language=shared_memory_configs['language']
            )
            must_cite_objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=must_cite_object_ids, language=shared_memory_configs['language']
            )
        graph = create_react_agent(
            model=execute_node_llm,
            prompt=prompt.partial(
                agent_name=config.get("configurable").get("agent_name"),
                agent_description=config.get("configurable").get("agent_description"),
                plan=state.plan,
                objects_summary=objects_summary,
                must_cite_objects_summary=must_cite_objects_summary,
                important_guidelines=important_guidelines
            ),
            tools=tools,
            state_schema=ReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")

    if response.action == "success":
        return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "my_plan_is_complete": False,
            "messages": [AIMessage(content=response.message, name=config.get("configurable").get("agent_name"))],
        }

    elif response.action == "failure":
        return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False,
            "my_plan_is_complete": False,
            "observation": response.message
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

# Agent class
class ReactPlanningAgent(BasicAgent):

    AGENT_TYPE = "react_planning_basic"
    OBSERVE_NODE = observe_node
    PLAN_NODE = plan_node
    EXECUTE_NODE = execute_node
    CONFIG_SCHEMA = ReactPlanningAgentConfigSchema