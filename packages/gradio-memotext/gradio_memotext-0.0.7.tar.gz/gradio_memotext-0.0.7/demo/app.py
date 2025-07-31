
import gradio as gr
from gradio_memotext import MemoText


example = MemoText().example_value()

demo = gr.Interface(
    lambda x:x,
    MemoText(),  # interactive version of your component
    MemoText(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
