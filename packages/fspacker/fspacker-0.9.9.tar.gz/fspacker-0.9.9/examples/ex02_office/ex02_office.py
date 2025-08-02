from pypdf import PageObject
from pypdf import PdfWriter
from pypdf.annotations import FreeText


def main():
    writer = PdfWriter()

    page = PageObject.create_blank_page(None, 612, 792)  # 创建一个标准页面大小
    writer.add_page(page)
    writer.add_outline_item("示例 - 书签", 1, parent=None)

    # Create the annotation and add it
    annotation = FreeText(
        text="Hello World\nThis is the second line!",
        rect=(50, 550, 200, 650),
        font="Arial",
        bold=True,
        italic=True,
        font_size="20pt",
        font_color="00ff00",
        border_color="0000ff",
        background_color="cdcdcd",
    )

    # Set annotation flags to 4 for printable annotations.
    # See "AnnotationFlag" for other options, e.g. hidden etc.
    annotation.flags = 4

    writer.add_annotation(page_number=0, annotation=annotation)

    with open("oputput.pdf", "wb") as file:
        writer.write(file)


if __name__ == "__main__":
    main()
