from eagle.utils.output import convert_schema
from eagle.utils.prompt_utils import PromptGenerator, EagleJsonOutputParser
from eagle.agents.react_agent.prompts import (
    OBJECTS_SUMMARY_STR_EN,
    OBJECTS_SUMMARY_STR_PT_BR,
    OBSERVATION_STR_PT_BR,
    OBSERVATION_STR_EN,
    PLAN_STR_PT_BR,
    PLAN_STR_EN,
    TOOLS_INTERACTIONS_STR_PT_BR,
    TOOLS_INTERACTIONS_STR_EN,
    SYSTEM_PROMPT_TUPLE_PT_BR,
    SYSTEM_PROMPT_TUPLE_EN,
    IMPORTANT_GUIDELINES_STR_PT_BR,
    IMPORTANT_GUIDELINES_STR_EN
)
from pydantic import BaseModel, Field
from typing import ClassVar
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional

# Gemeral prompts
YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR = """
Você coordena duas conversas: uma com o demandante e outra com os participantes.
{%- if messages_with_requester %}
Abaixo, sua conversa com o DEMANDANTE:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
Nenhuma mensagem trocada com o demandante ainda.
{%- endif %}
{%- if messages_with_agents %}
Abaixo, as mensagens trocadas entre os PARTICIPANTES:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
Nenhuma mensagem trocada entre os participantes ainda.
{%- endif %}
"""

YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN = """
You are coordinating two conversations: one with the requester and another with the participants.
{%- if messages_with_requester %}
Below is your conversation with the REQUESTER:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
No messages exchanged with the requester yet.
{%- endif %}
{%- if messages_with_agents %}
Below are the messages exchanged between the PARTICIPANTS:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
No messages exchanged between the participants yet.
{%- endif %}
"""

THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR = """
{%- if participants %}
Abaixo, uma descrição dos participantes:
-----------------------------------------------------
{%- for participant in participants %}
Nome: {{ participant.name }}
Descrição: {{ participant.description }}


{%- endfor %}
-----------------------------------------------------
{%- endif %}
"""

THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN = """
{%- if participants %}
Below is a description of the participants:
-----------------------------------------------------
{%- for participant in participants %}
Name: {{ participant.name }}
Description: {{ participant.description }}


{%- endfor %}
-----------------------------------------------------
{%- endif %}
"""

MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR = """
{%- if must_cite_objects_summary %}
Caso você decisa ENCERRAR o debate, os seguintes objetos devem ser citados na resposta, com os respectivos IDs:
--------------- Objetos a serem citados-----------------
{{ must_cite_objects_summary }}
--------------------------------------------------------
{%- endif %}
"""

MUST_CITE_OBJECTS_SUMMARY_STR_EN = """
{%- if must_cite_objects_summary %}
If you decide to END the debate, the following objects must be cited in the response, with their respective IDs:
--------------- Objects to be cited-----------------
{{ must_cite_objects_summary }}
--------------------------------------------------------
{%- endif %}
"""

# Prompt strings
OBSERVE_A_DEBATE_STR_PT_BR = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBSERVATION_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Agora, decida o que fazer a seguir. Você pode escolher entre as seguintes opções:
1. Caso as demandas do DEMANDANTE ainda não tenham sido atendidas, você pode continuar o debate. Para isso, escolha um dos PARTICIPANTES (jamais o DEMANDANTE) e faça uma pergunta ou solicitação a ele. Nesse caso, o retorno em json deve ter a seguinte estrutura:
{
    "acao": "continuar_debate",
    "participante": <nome EXATO do participante escolhido e JAMAIS o nome do DEMANDANTE>,
    "mensagem": <Mensagem a ser enviada ao participante. Deixe uma string vazia caso não seja necessário enviar uma mensagem específica e baste passar a vez para esse participante.>
}

2. Caso as demandas do DEMANDANTE do debate tenham sido atendidas, você pode encerrar o debate, ou, caso não haja nenhuma necessidade de debate, nem precisa começar um. Nesse caso, o retorno em json deve ter a seguinte estrutura:
{
    "acao": "encerrar_debate",
    "mensagem": <Mensagem a ser enviada ao DEMANDANTE do debate com o resumo, principais pontos e conclusões do debate, caso um debate tenha acontecido, ou uma resposta direta caso não tenha havido um debate>
}

RESPOSTA:
"""

OBSERVE_A_DEBATE_STR_EN = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN + \
    PLAN_STR_EN + \
    OBSERVATION_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    MUST_CITE_OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
Now, decide what to do next. You can choose between the following options:
1. If the REQUESTER's demands have not yet been met, you can continue the debate. To do this, choose one of the PARTICIPANTS (never the REQUESTER) and ask them a question or make a request. In this case, the return in json must have the following structure:
{
    "action": "continue_debate",
    "participant": <EXACT name of the chosen participant and NEVER the name of the REQUESTER>,
    "message": <Message to be sent to the participant. Leave an empty string if no specific message is needed and just pass the turn to that participant.>
}

2. If the REQUESTER's demands have been met, you can end the debate, or if there is no need for a debate, you don't even need to start one. In this case, the return in json must have the following structure:
{
    "action": "end_debate",
    "message": <message to be sent to the requester of the debate with the summary, main points, and conclusions of the debate, if a debate has taken place, or a direct response if no debate has occurred>
}

RESPONSE:
"""

# Prompts
OBSERVE_A_DEBATE_PROMPT_PT_BR = ChatPromptTemplate.from_messages(
    [
        SYSTEM_PROMPT_TUPLE_PT_BR,
        HumanMessagePromptTemplate.from_template(
            template=OBSERVE_A_DEBATE_STR_PT_BR,
            template_format="jinja2"
        ),
    ]
)

OBSERVE_A_DEBATE_PROMPT_EN = ChatPromptTemplate.from_messages(
    [
        SYSTEM_PROMPT_TUPLE_EN,
        HumanMessagePromptTemplate.from_template(
            template=OBSERVE_A_DEBATE_STR_EN,
            template_format="jinja2"
        ),
    ]
)

# Schemas
class ObserveDebatePromptOutputSchemaEN(BaseModel):
    action: str = Field(description="Action to be taken by the agent. Can be 'continue_debate' or 'end_debate'.")
    participant: Optional[str] = Field(default="", description="Name of the chosen participant, required if action is 'continue_debate'.")
    message: str = Field(description="Message to be sent to the participant or supervisor.")

class ObserveDebatePromptOutputSchemaPT_BR(BaseModel):
    acao: str = Field(description="Ação a ser tomada pelo agente. Pode ser 'continuar_debate' ou 'encerrar_debate'.")
    participante: Optional[str] = Field(default="", description="Nome do participante escolhido, necessário se a ação for 'continuar_debate'.")
    mensagem: str = Field(description="Mensagem a ser enviada ao participante ou supervisor.")

# Output Parsers
class ObserveDebatePromptOutputParser(EagleJsonOutputParser):
    """Custom output parser for the observe debate prompt. Language: pt-br."""

    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": ObserveDebatePromptOutputSchemaPT_BR,
            "convertion_schema": {
                "acao": {
                    "target_key": "action",
                    "value_mapping": {
                        "continuar_debate": "continue_debate",
                        "encerrar_debate": "end_debate"
                    }
                },
                "participante": {
                    "target_key": "participant",
                    "value_mapping": {}  # No value mapping needed for this key
                },
                "mensagem": {
                    "target_key": "message",
                    "value_mapping": {}  # No value mapping needed for this key
                }
            }
        },
        "en": {
            "class_for_parsing": ObserveDebatePromptOutputSchemaEN,
            "convertion_schema": {
                "action": {
                    "target_key": "action",
                    "value_mapping": {
                        "continue_debate": "continue_debate",
                        "end_debate": "end_debate"
                    }
                },
                "participant": {
                    "target_key": "participant",
                    "value_mapping": {}  # No value mapping needed for this key
                },
                "message": {
                    "target_key": "message",
                    "value_mapping": {}  # No value mapping needed for this key
                }
            }
        },
    }

    TARGET_SCHEMA: BaseModel = ObserveDebatePromptOutputSchemaEN

# Prompts dictionary
_PROMPTS_DICT = {
    "observe_debate": {
        "output_parser": ObserveDebatePromptOutputParser,
        "languages": {
            "pt-br": OBSERVE_A_DEBATE_PROMPT_PT_BR,
            "en": OBSERVE_A_DEBATE_PROMPT_EN,
        },
    },
}

# Initialize the PromptGenerator with the prompts dictionary
prompt_generator = PromptGenerator(prompts_dict=_PROMPTS_DICT)