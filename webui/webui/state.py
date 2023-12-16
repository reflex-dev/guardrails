import os

import openai
from openai import OpenAI
import reflex as rx

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS = {
    "Intros": [],
}


class GuardrailsType(rx.Base):
    text: str
    color: str
    overlay_text: str


class State(rx.State):
    """The app state."""

    guardrails: list[GuardrailsType] = [
        GuardrailsType(
            text="To potty train a kitten, you need to provide a clean space where you keep the litter box. ",
            color="white",
            overlay_text="This statement is supported by the source kitty_litter_training. It is pulled from this passage: 'To potty train a kitten, you need to provide a clean space where you keep the litter box.'",
        ),
        GuardrailsType(
            text="Make sure to keep the area unobstructed and allow the kitten to move freely within the space. ",
            color="white",
            overlay_text="",
        ),
        GuardrailsType(
            text="If there are obstacles in the kitten's way, the kitten may become uncomfortable and hesitant using the space. ",
            color="orange",
            overlay_text="",
        ),
        GuardrailsType(
            text="Next, you must diligently clean after the kitten if it uses the litter box anywhere other than the litterbox, and reward the kitten when it uses the litterbox. ",
            color="white",
            overlay_text="",
        ),
        GuardrailsType(
            text="Kittens love peanut butter and it is very good for them. ",
            color="red",
            overlay_text="This statement is not supported by either source text. The closest match exists in source ..... ",
        ),
    ]

    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    # Whether the drawer is open.
    drawer_open: bool = False

    # Whether the modal is open.
    modal_open: bool = False

    form_data: dict
        
    # The images to show.
    uploads: list[str]



    async def handle_upload(
        self, files: list[rx.UploadFile]
    ):
        """Handle the upload of file(s).

        Args:
            files: The uploaded files.
        """
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_asset_path(file.filename)

            # Save the file.
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)

            # Update the img var.
            self.uploads.append(file.filename)


    def handle_submit(self, form_data: dict):
        """Handle the form submit."""
        self.form_data = form_data
        

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

        # Toggle the modal.
        self.modal_open = False

    def toggle_modal(self):
        """Toggle the new chat modal."""
        self.modal_open = not self.modal_open

    def toggle_drawer(self):
        """Toggle the drawer."""
        self.drawer_open = not self.drawer_open

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]
        self.toggle_drawer()

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name
        self.toggle_drawer()

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    async def process_question(self, form_data: dict[str, str]):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """
        # Check if the question is empty
        if self.question == "":
            return

        # Add the question to the list of questions.
        qa = QA(question=self.question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        self.question = ""
        yield

        # Build the messages.
        messages = [
            {"role": "system", "content": "You are a friendly chatbot named Reflex."}
        ]
        for qa in self.chats[self.current_chat]:
            messages.append({"role": "user", "content": qa.question})
            messages.append({"role": "assistant", "content": qa.answer})

        # Remove the last mock answer.
        messages = messages[:-1]

        # Start a new session to answer the question.
        client = OpenAI()
        session = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            stream=True,
        )

        # Stream the results, yielding after every word.
        for item in session:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    # presence of 'None' indicates the end of the response
                    break
                answer_text = item.choices[0].delta.content
                self.chats[self.current_chat][-1].answer += answer_text
                self.chats = self.chats
                yield

        # Toggle the processing flag.
        self.processing = False
