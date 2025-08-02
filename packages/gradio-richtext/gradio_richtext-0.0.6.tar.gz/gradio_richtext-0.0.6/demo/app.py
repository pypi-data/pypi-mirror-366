
import gradio as gr
from gradio_richtext import RichText


example = RichText().example_value()

demo = gr.Interface(
    lambda x:x,
    RichText(),  # interactive version of your component
    RichText(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
