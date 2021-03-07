from src.text_to_command import TextToCmdBuffer

buffer = TextToCmdBuffer()

buffer.add_text("King G6")
print(buffer.get_command().text())

buffer.clear()

buffer.add_text("exit")
print(buffer.get_command().text())
