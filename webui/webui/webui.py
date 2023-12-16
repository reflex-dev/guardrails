"""The main Chat app."""

import reflex as rx

from webui import styles
from webui.components import chat, modal, navbar, sidebar
from webui.state import State, GuardrailsType

color = "rgb(107,99,246)"


def render_guardrails_text(guardrails: GuardrailsType) -> rx.Component:
    """Render the guardrails text."""
    return rx.tooltip(
            rx.span(guardrails.text, color=guardrails.color),
            label=guardrails.overlay_text,
        )
    


def index() -> rx.Component:
    """The main app."""
    return rx.vstack(
        rx.vstack(
            rx.heading("Guardrails X Reflex", size="xl"),
            rx.text("This app lets you ask questions relevant to documents below. Guardrails AI validates the responses from OpenAI. More about provenance. (add link here)"),
            height="20%",
        ),
        #navbar(),

        rx.hstack(
            rx.vstack(
                rx.heading("Control Panel", size="xl"),

                rx.vstack(
                    rx.box(rx.foreach(State.guardrails, render_guardrails_text)),
                ),

                
                


                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="OpenAI API Key",
                            name="OpenAI_API_Key",
                        ),
                        rx.button("Submit", type_="submit"),
                    ),
                    on_submit=State.handle_submit,
                    reset_on_submit=True,
                ),
                rx.text(State.form_data.to_string(),
                        **styles.message_style),

                rx.divider(),

                rx.upload(
                    rx.vstack(
                        rx.button(
                            "Select File",
                            color=color,
                            bg="white",
                            border=f"1px solid {color}",
                        ),
                        rx.text(
                            "Drag and drop files here or click to select files"
                        ),
                    ),
                    border=f"1px dotted {color}",
                    padding="5em",
                ),
                rx.hstack(rx.foreach(rx.selected_files, rx.text)),
                rx.button(
                    "Upload",
                    on_click=lambda: State.handle_upload(
                        rx.upload_files()
                    ),
                ),
                rx.button(
                    "Clear",
                    on_click=rx.clear_selected_files,
                ),
                rx.text("Source Documents"),
                rx.foreach(
                    State.uploads, lambda upload: rx.text(upload)
                ),
                


                
                
  
                
                width="50%",
                height="80%",

            ),
            rx.vstack(
                chat.chat(),
                chat.action_bar(),
                width="100%",
                height="80%",
            ),
            height="100vh",
            width="100%",
            # align_items="center",
            # justify_content="center",
            # spacing="2em",
        ),

        #sidebar(),
        #modal(),
        bg=styles.bg_dark_color,
        color=styles.text_light_color,
        min_h="100vh",
        # align_items="stretch",
        # justify_content="center",
        # spacing="0",
    )


# Add state and page to the app.
app = rx.App(state=State, style=styles.base_style)
app.add_page(index)
app.compile()
