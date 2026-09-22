import os
from dotenv import load_dotenv
from openai import OpenAI
from cli.LocalRepository import save_conversations
from layer.ui.display import conversation_disply


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def openai_api(user_input, conversation, console):
    is_first_turn_of_chat = "title" not in conversation.metadata
    with console.status("[loading]Thinking... [/loading]") as status:
        if is_first_turn_of_chat:
            status.update("[loading]Generating title... [/loading]")

            title_response = client.responses.create(
                model="gpt-6-astra",
                instructions="You are a utility that generates short titles for chat logs. Summarize the user's request in 3 to 5 words. Do not use quotes, punctuation, or prefix words like 'Title:'.",
                input=[{"role": "user", "content": user_input}]
            )
            client_title = title_response.output_text

            conversation = client.conversations.update(
                conversation_id=conversation.id,
                metadata={"title": client_title}
            )

        save_conversations(
            conversation.id, client_title, "user", user_input, conversation.created_at)

        status.update("[loading]Thinking... [/loading]")
        response = client.responses.create(
            model="gpt-6-astra",
            input=[{"role": "user", "content": user_input}],
            conversation=conversation.id
        )
        chat_output = response.output_text

        save_conversations(conversation.id, client_title,
                           "assistant", chat_output, conversation.created_at)
        chat_conversation = conversation_disply(
            chat_output, console, is_user=False)
        console.print(chat_conversation)
