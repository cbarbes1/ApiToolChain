from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("directory.pdf")

data = loader.load()

data2 = loader.load_and_split()

print(data)
input("Data 1")


for item in data2:
    print(item.page_content)
input("Data 2")