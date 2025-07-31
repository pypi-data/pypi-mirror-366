from eagle.agents.react_agent.base import ReactPlanningAgent, ReactAgentState, process_graph_stream
from eagle.chat_schemas.base import BasicChatSupervisorWorkingMemoryState
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
from eagle.chat_schemas.debate_schemas.agents.prompts import prompt_generator
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from pydantic import Field
from datetime import datetime, timezone

class DebateModeratorReactAgentState(ReactAgentState):

    messages_with_requester: list = []
    messages_with_agents: list = []
    participants: list = []

class DebateModeratorSimpleAgentWorkingMemoryState(BasicChatSupervisorWorkingMemoryState):
    participant: str = Field(default="", description="Name of the next participant to speak.")

def observe_node(state: DebateModeratorSimpleAgentWorkingMemoryState, config: RunnableConfig, store) -> DebateModeratorSimpleAgentWorkingMemoryState:
    """
    Process the observation phase, make a decision, and update the state.
    """
    observe_node_llm = config.get("configurable").get("observe_node_llm")
    observe_node_prompt_language = config.get("configurable").get("observe_node_llm_prompt_language")
    observe_node_llm_use_structured_output = config.get("configurable").get("observe_node_llm_use_structured_output", False)
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="observe_debate",
        language=observe_node_prompt_language,
        use_structured_output=observe_node_llm_use_structured_output,
        llm=observe_node_llm if observe_node_llm else None
    )
    
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]
    
    chat_id = config.get("configurable").get("chat_id")

    shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

    
    tools = config.get("configurable").get("executing_tools", [])

    important_guidelines = config.get("configurable").get("observe_important_guidelines")

    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_requester))

    # Process the graph with the inputs
    message = None
    inputs = {
        "messages": [state.messages_with_requester[-1]],
        "messages_with_requester": state.messages_with_requester[-window_size:],
        "messages_with_agents": state.messages_with_agents,
        "participants": state.participants,
        "plan": state.plan,
        "observation": state.observation,
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
                    if datetime.fromtimestamp(metadata.created_at / 1000).astimezone(timezone.utc) >= state.interaction_initial_datetime:
                        must_cite_object_ids.append(metadata.object_id)
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=list(set(object_ids)-set(must_cite_object_ids)), language=shared_memory_configs['language']
            )
            must_cite_objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=must_cite_object_ids, language=shared_memory_configs['language']
            )
        graph = create_react_agent(
            model=observe_node_llm,
            prompt=prompt.partial(
                agent_name=config.get("configurable").get("agent_name"),
                agent_description=config.get("configurable").get("agent_description"),
                observation=state.observation,
                plan=state.plan,
                objects_summary=objects_summary,
                must_cite_objects_summary=must_cite_objects_summary,
                important_guidelines=important_guidelines,
            ),
            tools=tools,
            state_schema=DebateModeratorReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    # Access the 'role' attribute directly instead of using subscript notation
    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")
    
    if response.action == "end_debate":
        return {
            "execution_is_complete": True,
            "messages_with_requester": [
                AIMessage(content=response.message, name=config.get("configurable").get("agent_name"))
            ],
            "flow_direction": "requester"
        }
    elif response.action == "continue_debate":
        if response.message:
            messages_with_agents = [
                AIMessage(content=response.message, name=config.get("configurable").get("agent_name")) 
            ]
        else:
            messages_with_agents = []
        return {
            "execution_is_complete": True,
            "messages_with_agents": messages_with_agents,
            "flow_direction": "agents",
            "participant": response.participant
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

class DebateModeratorSimpleAgent(ReactPlanningAgent):
    """
    A subclass of ReactPlanningAgent to implement a debate moderator agent.
    The agent is responsible for managing the flow of the debate and ensuring that each participant has a chance to speak.
    """

    AGENT_TYPE = "debate_moderator"
    WORKING_MEMORY_STATE = DebateModeratorSimpleAgentWorkingMemoryState
    OBSERVE_NODE = observe_node
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
